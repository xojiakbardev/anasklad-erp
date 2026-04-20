import { api, handle } from "@/lib/api";

export interface Shop {
  id: string;
  external_id: number;
  name: string;
  created_at: string;
}

export interface Integration {
  id: string;
  source: string;
  label: string;
  status: "active" | "disabled" | "error";
  last_checked_at: string | null;
  last_error: string | null;
  created_at: string;
  shops: Shop[];
}

export const integrationsApi = {
  list: () => handle<Integration[]>(api.get("integrations")),

  connectUzum: (token: string, label: string) =>
    handle<Integration>(api.post("integrations/uzum", { json: { token, label } })),

  remove: (id: string) => handle<void>(api.delete(`integrations/${id}`)),

  test: (id: string) => handle<Integration>(api.post(`integrations/${id}/test`)),
};
