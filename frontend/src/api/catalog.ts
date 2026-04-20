import { api, handle } from "@/lib/api";

export interface ProductRow {
  product_id: string;
  external_id: number;
  title: string;
  category: string | null;
  image_url: string | null;
  sku_count: number;
  qty_fbo_total: number;
  qty_fbs_total: number;
  min_price: number | null;
  max_price: number | null;
  updated_at: string;
}

export interface ProductListResponse {
  items: ProductRow[];
  total: number;
  page: number;
  size: number;
}

export interface Variant {
  id: string;
  external_id: number;
  title: string;
  barcode: string | null;
  article: string | null;
  ikpu: string | null;
  characteristics: string | null;
  price: number | null;
  purchase_price: number | null;
  qty_fbo: number;
  qty_fbs: number;
  qty_sold_total: number;
  qty_returned_total: number;
  returned_percentage: number | null;
  archived: boolean;
  blocked: boolean;
  preview_image_url: string | null;
}

export interface SyncResult {
  integration_id: string;
  products_upserted: number;
  variants_upserted: number;
  shops_synced: number;
}

export const catalogApi = {
  listProducts: (params: {
    shop_id?: string;
    search?: string;
    page: number;
    size: number;
  }) => {
    const q = new URLSearchParams();
    if (params.shop_id) q.set("shop_id", params.shop_id);
    if (params.search) q.set("search", params.search);
    q.set("page", params.page.toString());
    q.set("size", params.size.toString());
    return handle<ProductListResponse>(api.get(`catalog/products?${q.toString()}`));
  },

  listVariants: (productId: string) =>
    handle<Variant[]>(api.get(`catalog/products/${productId}/variants`)),

  syncIntegration: (integrationId: string) =>
    handle<SyncResult>(api.post(`catalog/integrations/${integrationId}/sync`)),
};
