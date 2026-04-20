import { api, handle } from "@/lib/api";

export interface AbcRow {
  product_id: string;
  external_id: number;
  title: string;
  units_sold: number;
  revenue: number;
  profit: number;
  share: number;
  cumulative_share: number;
  rank: "A" | "B" | "C" | "N";
}

export interface TurnoverRow {
  variant_id: string;
  product_title: string;
  sku_title: string;
  qty_fbo: number;
  qty_fbs: number;
  avg_daily_sales: number;
  days_of_stock: number | null;
}

export interface StockRow {
  variant_id: string;
  product_id: string;
  product_title: string;
  sku_title: string;
  barcode: string | null;
  qty_fbo: number;
  qty_fbs: number;
  qty_total: number;
  price: number | null;
  purchase_price: number | null;
  archived: boolean;
  blocked: boolean;
}

export interface StockListResponse {
  items: StockRow[];
  total: number;
  page: number;
  size: number;
}

export const reportsApi = {
  abc: (days = 30) => handle<AbcRow[]>(api.get(`reports/abc?days=${days}`)),

  turnover: (days = 30, limit = 200) =>
    handle<TurnoverRow[]>(api.get(`reports/turnover?days=${days}&limit=${limit}`)),

  lowStock: (fbsThreshold = 5, fboThreshold = 5) =>
    handle<StockRow[]>(
      api.get(`reports/low-stock?fbs_threshold=${fbsThreshold}&fbo_threshold=${fboThreshold}`),
    ),

  stocks: (params: {
    search?: string;
    only_available?: boolean;
    only_low?: boolean;
    only_out?: boolean;
    page?: number;
    size?: number;
  }) => {
    const q = new URLSearchParams();
    if (params.search) q.set("search", params.search);
    if (params.only_available) q.set("only_available", "true");
    if (params.only_low) q.set("only_low", "true");
    if (params.only_out) q.set("only_out", "true");
    q.set("page", (params.page ?? 0).toString());
    q.set("size", (params.size ?? 100).toString());
    return handle<StockListResponse>(api.get(`reports/stocks?${q.toString()}`));
  },
};
