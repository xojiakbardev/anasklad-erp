import { api, handle } from "@/lib/api";

export interface FinanceBucket {
  revenue: number;
  commission: number;
  logistics: number;
  purchase_cost: number;
  profit: number;
  withdrawn: number;
  sales_count: number;
  units_sold: number;
  units_returned: number;
}

export interface DailyPoint {
  day: string;
  revenue: number;
  profit: number;
}

export interface TopProduct {
  product_id: number | null;
  title: string;
  units: number;
  revenue: number;
  profit: number;
}

export interface FinanceSummary {
  today: FinanceBucket;
  period: FinanceBucket;
  period_days: number;
  daily: DailyPoint[];
  top_products: TopProduct[];
}

export interface Sale {
  id: string;
  external_id: number;
  external_order_id: number | null;
  status: string | null;
  sold_at: string | null;
  product_title: string | null;
  sku_title: string | null;
  amount: number;
  seller_price: number | null;
  commission: number | null;
  logistic_delivery_fee: number | null;
  seller_profit: number | null;
  return_cause: string | null;
}

export interface Expense {
  id: string;
  external_id: number;
  name: string | null;
  type: "INCOME" | "OUTCOME" | null;
  source_kind: string | null;
  status: string | null;
  payment_price: number | null;
  amount: number;
  date_service: string | null;
}

export const financeApi = {
  summary: (days = 30) =>
    handle<FinanceSummary>(api.get(`finance/summary?days=${days}`)),

  listSales: (page = 0, size = 100) =>
    handle<{ items: Sale[]; total: number; page: number; size: number }>(
      api.get(`finance/sales?page=${page}&size=${size}`),
    ),

  listExpenses: (page = 0, size = 100) =>
    handle<{ items: Expense[]; total: number; page: number; size: number }>(
      api.get(`finance/expenses?page=${page}&size=${size}`),
    ),

  sync: (integrationId: string, days = 30) =>
    handle<{ sales_upserted: number; expenses_upserted: number }>(
      api.post(`finance/integrations/${integrationId}/sync?days=${days}`),
    ),
};
