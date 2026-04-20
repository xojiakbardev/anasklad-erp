# Deployment Guide

Production target: **single VPS with Docker Compose** (Hetzner / Contabo / DigitalOcean).
Kubernetes-ready — same images, just swap `docker-compose.prod.yml` for Helm/Kustomize later.

## 1. Server prerequisites

- Ubuntu 22.04 / 24.04, 2 vCPU / 4 GB RAM minimum
- Docker Engine 24+ with Compose v2
- Outbound HTTPS (for Uzum API, Let's Encrypt, GHCR)
- DNS record pointing to the server IP:
  - `anasklad.uz` → A record → server IP
  - `www.anasklad.uz` → CNAME → anasklad.uz

```bash
# Install Docker (if not present)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker "$USER"
# Re-login for group to take effect
```

## 2. Clone and configure

```bash
sudo mkdir -p /opt/anasklad
sudo chown "$USER":"$USER" /opt/anasklad
cd /opt/anasklad
git clone https://github.com/xojiakbardev/anasklad-erp.git .

# Generate secrets
JWT_SECRET=$(openssl rand -hex 32)
FERNET=$(docker run --rm python:3.13-slim \
    sh -c 'pip install -q cryptography && python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"')

cat > .env <<EOF
DOMAIN=anasklad.uz

POSTGRES_USER=anasklad
POSTGRES_PASSWORD=$(openssl rand -hex 16)
POSTGRES_DB=anasklad

JWT_SECRET=$JWT_SECRET
CREDENTIALS_FERNET_KEY=$FERNET

CORS_ORIGINS=https://anasklad.uz
VITE_API_URL=/api

SENTRY_DSN=
OTEL_EXPORTER_OTLP_ENDPOINT=
EOF

chmod 600 .env
```

## 3. Pull & start

Either **build on server** or **pull pre-built images from GHCR** (CI builds them).

```bash
# Option A — pull from GHCR (recommended)
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d

# Option B — build locally
docker compose -f docker-compose.prod.yml up -d --build

# Verify
docker compose -f docker-compose.prod.yml ps
curl -sf https://anasklad.uz/health/ready
```

Caddy handles TLS automatically via Let's Encrypt (HTTP-01 challenge on first request to the domain). Make sure ports 80/443 are open.

## 4. Migrations

Migrations run on every `api` startup (`alembic upgrade heads` in the entrypoint). No manual step needed.

To run manually for troubleshooting:
```bash
docker compose -f docker-compose.prod.yml exec api \
    sh -c "cd /app/backend && alembic current && alembic history"
```

## 5. Backups

```bash
mkdir -p /opt/anasklad/backups
chmod +x scripts/backup.sh

# Cron — daily at 03:00 UTC
(crontab -l 2>/dev/null; echo "0 3 * * * cd /opt/anasklad && ./scripts/backup.sh >> /var/log/anasklad-backup.log 2>&1") | crontab -

# Manual test
./scripts/backup.sh
```

Retention default: 7 days. Set `S3_BUCKET` in env to also upload to S3.

Restore:
```bash
gunzip -c backups/anasklad_YYYYMMDD.sql.gz | \
    docker compose -f docker-compose.prod.yml exec -T postgres \
    psql -U anasklad -d anasklad
```

## 6. Updates

```bash
cd /opt/anasklad
git pull
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
# Old containers are rolled one-by-one. Migrations run on api startup.
```

## 7. Monitoring

### Uptime
- [UptimeRobot](https://uptimerobot.com) free tier — ping `https://anasklad.uz/health/ready` every 5 min.

### Errors
Set `SENTRY_DSN` in `.env` — backend auto-reports.

### Tracing
Set `OTEL_EXPORTER_OTLP_ENDPOINT` (e.g. Grafana Cloud Tempo) — FastAPI, SQLAlchemy, httpx, redis auto-instrumented.

### Log tailing
```bash
docker compose -f docker-compose.prod.yml logs -f api worker
```

## 8. Rollback

```bash
docker compose -f docker-compose.prod.yml pull \
    --policy missing ghcr.io/xojiakbardev/anasklad-erp-api:sha-<PREV>
docker compose -f docker-compose.prod.yml up -d api worker
```

## 9. Post-deploy checklist

- [ ] `https://anasklad.uz` loads (SPA)
- [ ] `https://anasklad.uz/api/auth/login` returns `401` (not `502` / `404`)
- [ ] `https://anasklad.uz/health/ready` returns `{"status":"ready"}`
- [ ] SSL certificate valid (grade A+ on ssllabs.com)
- [ ] Backups directory populated after first cron run
- [ ] Register a test user, connect Uzum token, verify sync
