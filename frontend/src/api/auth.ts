import { api, handle } from "@/lib/api";

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  tenant_id: string;
  is_superuser: boolean;
  created_at: string;
}

export interface Tokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  access_expires_at: string;
  refresh_expires_at: string;
}

export interface AuthResponse {
  user: User;
  tokens: Tokens;
}

export const authApi = {
  login: (email: string, password: string) =>
    handle<AuthResponse>(api.post("auth/login", { json: { email, password } })),

  register: (params: {
    email: string;
    password: string;
    full_name: string | null;
    tenant_name: string;
  }) => handle<AuthResponse>(api.post("auth/register", { json: params })),

  me: () => handle<User>(api.get("auth/me")),
};
