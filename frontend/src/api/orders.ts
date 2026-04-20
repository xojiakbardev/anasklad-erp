import { api, handle } from "@/lib/api";

export type FbsStatus =
  | "CREATED"
  | "PACKING"
  | "PENDING_DELIVERY"
  | "DELIVERING"
  | "DELIVERED"
  | "ACCEPTED_AT_DP"
  | "DELIVERED_TO_CUSTOMER_DELIVERY_POINT"
  | "COMPLETED"
  | "CANCELED"
  | "PENDING_CANCELLATION"
  | "RETURNED";

export const KANBAN_COLUMNS: FbsStatus[] = [
  "CREATED",
  "PACKING",
  "PENDING_DELIVERY",
  "DELIVERING",
  "DELIVERED",
];

export interface Order {
  id: string;
  external_id: number;
  invoice_number: number | null;
  status: FbsStatus;
  scheme: string | null;
  price: number | null;
  cancel_reason: string | null;
  date_created: string | null;
  accept_until: string | null;
  deliver_until: string | null;
  completed_date: string | null;
  updated_at: string;
}

export interface OrderItem {
  id: string;
  external_sku_id: number | null;
  sku_title: string | null;
  product_title: string | null;
  amount: number;
  seller_price: number | null;
  purchase_price: number | null;
  commission: number | null;
  logistic_delivery_fee: number | null;
  seller_profit: number | null;
}

export interface OrderDetail extends Order {
  items: OrderItem[];
}

export interface OrderListResponse {
  items: Order[];
  total: number;
  page: number;
  size: number;
  counts_by_status: Record<string, number>;
}

export const ordersApi = {
  list: (params: { status?: FbsStatus; page?: number; size?: number }) => {
    const q = new URLSearchParams();
    if (params.status) q.set("status", params.status);
    q.set("page", (params.page ?? 0).toString());
    q.set("size", (params.size ?? 100).toString());
    return handle<OrderListResponse>(api.get(`orders?${q.toString()}`));
  },

  get: (id: string) => handle<OrderDetail>(api.get(`orders/${id}`)),

  confirm: (id: string) => handle<Order>(api.post(`orders/${id}/confirm`)),

  cancel: (id: string, reason: string, comment?: string) =>
    handle<Order>(api.post(`orders/${id}/cancel`, { json: { reason, comment } })),

  labelUrl: (id: string, size: "LARGE" | "BIG" = "LARGE") =>
    `${import.meta.env.VITE_API_URL || "/api"}${
      (import.meta.env.VITE_API_URL || "").endsWith("/api") ? "" : "/api"
    }/orders/${id}/label?size=${size}`,

  sync: (integrationId: string) =>
    handle<{ orders_upserted: number; shops_synced: number }>(
      api.post(`orders/integrations/${integrationId}/sync`),
    ),
};
