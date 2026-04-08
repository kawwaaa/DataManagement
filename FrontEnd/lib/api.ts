export type TopProduct = {
  name: string
  currentSales: number
  predictedSales: number
  growth: number
}

export type LowProduct = {
  name: string
  currentSales: number
  predictedSales: number
  decline: number
  suggestions: string[]
}

export type MonthlyForecastByYear = {
  "2025": Record<string, number>
  "2026": Record<string, number>
}

export type SalesSuggestion = {
  title: string
  desc: string
  impact: string
}

export type BundleSuggestion = {
  primary: string
  bundle: string
  chance: number
  lift: number
  suggestions: string[]
  expectedSalesIncrease: number
}

export type NextBuyWeek = {
  week: string
  suggestedBuy: number
  reason: string
}

export type NextBuyForecast = {
  product: string
  insight: string
  weeklyForecast: NextBuyWeek[]
  overrideApplied?: boolean
  source?: {
    forecast_file: string
    history_file: string
    override_file: string
  }
}

export type SaveNextBuyForecastInputResponse = {
  ok: boolean
  product: string
  savedWeek: string
  savedSuggestedBuy: number
  savedReason: string
  overrideFile: string
}

export type PairwiseAssociation = {
  partner: string
  support: number
  confidence: number
  lift: number
  pairCount: number
  reason: string
  strategies: string[]
  expectedSalesIncrease: number
  projectedRevenueLiftLkr: number
}

export type PairwiseAssociationResponse = {
  product: string
  pairs: PairwiseAssociation[]
  totalBills: number
  source?: string
}

export type SalesForecastResponse = {
  product: string
  your_question: string
  answer: string
  "2026_sales_lkr": number
  growth_percent: number
  peak_month: string
  peak_reason: string
  monthly_2026: Record<string, number>
  month_context?: string
  did_you_mean?: string[]
}

type ProxyPayload = {
  tool: string
  args?: Record<string, unknown>
}

async function callTool<T>(tool: string, args?: Record<string, unknown>): Promise<T> {
  const res = await fetch("/api/proxy", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
    body: JSON.stringify({ tool, args } satisfies ProxyPayload),
  })

  const payload = await res.json()

  if (!res.ok) {
    throw new Error(payload?.error ?? `Tool call failed (${res.status})`)
  }

  if (payload && typeof payload === "object" && "error" in payload && payload.error) {
    throw new Error(String(payload.error))
  }

  return payload as T
}

export function getTopProducts() {
  return callTool<TopProduct[]>("get_top_products")
}

export function getLowerProducts() {
  return callTool<LowProduct[]>("get_lower_products")
}

export function getProductList() {
  return callTool<string[]>("product_list")
}

export function getMonthlyForecastByYear(productName: string) {
  return callTool<MonthlyForecastByYear>("get_monthly_forecast_2025_2026", { product_name: productName })
}

export function getSalesBoosterSuggestions(productName: string) {
  return callTool<SalesSuggestion[]>("get_sales_booster_suggestions", { product_name: productName })
}

export function getBundleSriLanka() {
  return callTool<BundleSuggestion[]>("get_bundle_srilanka")
}

export function getNextBuyForecast(productName: string) {
  return callTool<NextBuyForecast>("get_next_buy_forecast", { product_name: productName })
}

export function saveNextBuyForecastInput(args: {
  productName: string
  week: string
  suggestedBuy: number
  reason: string
  insight?: string
}) {
  return callTool<SaveNextBuyForecastInputResponse>("save_next_buy_forecast_input", {
    product_name: args.productName,
    week: args.week,
    suggested_buy: args.suggestedBuy,
    reason: args.reason,
    insight: args.insight ?? "",
  })
}

export function getPairwiseProductList() {
  return callTool<string[]>("pairwise_product_list")
}

export function getPairwiseAssociations(productName: string, limit = 5) {
  return callTool<PairwiseAssociationResponse>("get_pairwise_associations", {
    product_name: productName,
    limit,
  })
}

export type ChatHistoryMessage = {
  role: "user" | "assistant"
  content: string
}

export function runSalesForecast(prompt: string, history: ChatHistoryMessage[] = []) {
  return callTool<SalesForecastResponse>("sales_forecast", { prompt, history })
}
