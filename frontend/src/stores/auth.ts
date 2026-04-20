import { create } from "zustand";
import { persist } from "zustand/middleware";

interface User {
  id: string;
  email: string;
  full_name: string | null;
  tenant_id: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  accessExpiresAt: string | null;

  setSession: (data: {
    user: User;
    accessToken: string;
    refreshToken: string;
    accessExpiresAt: string;
  }) => void;
  setTokens: (access: string, refresh: string, accessExpiresAt: string) => void;
  logout: () => void;
  tryRefresh: () => Promise<string | null>;
}

const STORAGE_KEY = "anasklad.auth";

export const authStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      accessExpiresAt: null,

      setSession: ({ user, accessToken, refreshToken, accessExpiresAt }) =>
        set({ user, accessToken, refreshToken, accessExpiresAt }),

      setTokens: (accessToken, refreshToken, accessExpiresAt) =>
        set({ accessToken, refreshToken, accessExpiresAt }),

      logout: () =>
        set({ user: null, accessToken: null, refreshToken: null, accessExpiresAt: null }),

      tryRefresh: async () => {
        const { refreshToken } = get();
        if (!refreshToken) return null;
        try {
          const baseUrl = import.meta.env.VITE_API_URL || "";
          const url = baseUrl.endsWith("/api") ? `${baseUrl}/auth/refresh` : `${baseUrl}/api/auth/refresh`;
          const res = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh_token: refreshToken }),
          });
          if (!res.ok) return null;
          const data = (await res.json()) as {
            access_token: string;
            refresh_token: string;
            access_expires_at: string;
          };
          set({
            accessToken: data.access_token,
            refreshToken: data.refresh_token,
            accessExpiresAt: data.access_expires_at,
          });
          return data.access_token;
        } catch {
          return null;
        }
      },
    }),
    { name: STORAGE_KEY },
  ),
);

export const useAuth = authStore;
