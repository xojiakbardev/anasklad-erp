import ky, { type KyInstance } from "ky";

import { authStore } from "@/stores/auth";

const baseUrl = import.meta.env.VITE_API_URL || "/api";

export const api: KyInstance = ky.create({
  prefixUrl: baseUrl.endsWith("/api") ? baseUrl : `${baseUrl}/api`,
  timeout: 30_000,
  retry: { limit: 1, methods: ["get"], statusCodes: [502, 503, 504] },
  hooks: {
    beforeRequest: [
      (request) => {
        const token = authStore.getState().accessToken;
        if (token) request.headers.set("Authorization", `Bearer ${token}`);
      },
    ],
    afterResponse: [
      async (request, _options, response) => {
        if (response.status !== 401) return response;
        const url = new URL(request.url);
        if (url.pathname.includes("/auth/")) return response;

        const refreshed = await authStore.getState().tryRefresh();
        if (!refreshed) {
          authStore.getState().logout();
          return response;
        }
        request.headers.set("Authorization", `Bearer ${refreshed}`);
        return ky(request);
      },
    ],
  },
});

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public details?: unknown,
  ) {
    super(message);
  }

  /**
   * Translate a backend error code (e.g. "auth.invalid_credentials") to a
   * user-facing string in the current i18n language. Falls back to the
   * server-provided message when no translation exists.
   */
  translatedMessage(t: (key: string) => string): string {
    const map: Record<string, string> = {
      "auth.invalid_credentials": "errors.invalid_credentials",
      "auth.email_taken": "errors.email_taken",
      "auth.token_expired": "errors.token_expired",
      "auth.token_invalid": "errors.token_expired",
      "integration.uzum.auth": "errors.uzum_auth",
      "integration.uzum.no_shops": "errors.uzum_no_shops",
    };
    const key = map[this.code];
    if (!key) return this.message;
    const localized = t(key);
    return localized === key ? this.message : localized;
  }
}

export async function handle<T>(promise: Promise<Response>): Promise<T> {
  try {
    const res = await promise;
    if (res.status === 204) return undefined as T;
    return (await res.json()) as T;
  } catch (err) {
    if (err instanceof Error && "response" in err) {
      const response = (err as { response: Response }).response;
      try {
        const body = (await response.json()) as {
          code?: string;
          title?: string;
          detail?: string;
          details?: unknown;
        };
        throw new ApiError(
          response.status,
          body.code ?? "unknown",
          body.title ?? body.detail ?? "Request failed",
          body.details,
        );
      } catch (inner) {
        if (inner instanceof ApiError) throw inner;
        throw new ApiError(response.status, "unknown", "Request failed");
      }
    }
    throw err;
  }
}
