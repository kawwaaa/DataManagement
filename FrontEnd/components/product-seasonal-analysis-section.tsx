"use client"

import { useEffect, useMemo, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Line, LineChart, Bar, BarChart, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Legend } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { TrendingUp } from "lucide-react"
import { getMonthlyForecastByYear, getProductList, getSalesBoosterSuggestions, type SalesSuggestion } from "@/lib/api"

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

export function ProductSeasonalAnalysisSection() {
  const [products, setProducts] = useState<string[]>([])
  const [selectedProduct, setSelectedProduct] = useState<string>("")
  const [forecastByMonth, setForecastByMonth] = useState<{ "2025": Record<string, number>; "2026": Record<string, number> } | null>(
    null,
  )
  const [suggestions, setSuggestions] = useState<SalesSuggestion[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true
    ;(async () => {
      try {
        const list = await getProductList()
        if (!isMounted) return
        setProducts(list)
        if (list.length > 0) setSelectedProduct(list[0])
      } catch (err) {
        if (isMounted) setError(err instanceof Error ? err.message : "Failed to load product list.")
      }
    })()
    return () => {
      isMounted = false
    }
  }, [])

  useEffect(() => {
    if (!selectedProduct) return

    let isMounted = true
    setLoading(true)
    setError(null)

    ;(async () => {
      try {
        const [monthly, aiSuggestions] = await Promise.all([
          getMonthlyForecastByYear(selectedProduct),
          getSalesBoosterSuggestions(selectedProduct),
        ])
        if (!isMounted) return
        setForecastByMonth(monthly)
        setSuggestions(aiSuggestions.slice(0, 3))
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Failed to load seasonal analysis.")
          setForecastByMonth(null)
          setSuggestions([])
        }
      } finally {
        if (isMounted) setLoading(false)
      }
    })()

    return () => {
      isMounted = false
    }
  }, [selectedProduct])

  const seasonalData = useMemo(
    () =>
      MONTHS.map((month) => ({
        period: month,
        sales: Number(forecastByMonth?.["2026"]?.[month] ?? 0),
      })),
    [forecastByMonth],
  )

  const comparisonData = useMemo(
    () =>
      MONTHS.map((month) => ({
        month,
        oldSales: Number(forecastByMonth?.["2025"]?.[month] ?? 0),
        newSales: Number(forecastByMonth?.["2026"]?.[month] ?? 0),
      })),
    [forecastByMonth],
  )

  return (
    <section className="py-16 px-4 bg-gradient-to-b from-[#f5f8ff] via-[#fbfdff] to-[#f2fbff]">
      <div className="container mx-auto max-w-6xl space-y-6">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold mb-2 text-[#19183b]">Product Seasonal Analysis</h2>
          <p className="text-slate-600">Deep dive into individual product performance and seasonality</p>
        </div>

        <Card className="border border-indigo-200 bg-white/95 shadow-lg">
          <CardHeader>
            <CardTitle className="text-[#19183b]">Select Product</CardTitle>
            <CardDescription className="text-slate-600">Choose a product to view detailed seasonal analysis</CardDescription>
          </CardHeader>
          <CardContent>
            <Select value={selectedProduct} onValueChange={setSelectedProduct}>
              <SelectTrigger className="w-full max-w-md">
                <SelectValue placeholder="Select a product..." />
              </SelectTrigger>
              <SelectContent>
                {products.map((product) => (
                  <SelectItem key={product} value={product}>
                    {product}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </CardContent>
        </Card>

        {loading && <p className="text-center text-slate-500">Loading product analysis...</p>}
        {error && <p className="text-center text-red-400">{error}</p>}

        {selectedProduct && forecastByMonth && (
          <>
            <Card className="border border-cyan-200 bg-white/95 shadow-lg">
              <CardHeader>
                <CardTitle className="text-[#19183b]">Seasonal Sales Breakdown</CardTitle>
                <CardDescription className="text-slate-600">Monthly 2026 forecast trend for {selectedProduct}</CardDescription>
              </CardHeader>
              <CardContent>
                <ChartContainer
                  config={{
                    sales: {
                      label: "Sales",
                      color: "#06b6d4",
                    },
                  }}
                  className="h-[300px]"
                >
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={seasonalData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#bae6fd" />
                      <XAxis dataKey="period" className="text-xs" />
                      <YAxis className="text-xs" />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Line
                        type="monotone"
                        dataKey="sales"
                        stroke="var(--color-sales)"
                        strokeWidth={3}
                        dot={{ r: 5 }}
                        name="Forecast Sales (LKR)"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </CardContent>
            </Card>

            <Card className="border border-indigo-200 bg-white/95 shadow-lg">
              <CardHeader>
                <CardTitle className="text-[#19183b]">Sales Comparison</CardTitle>
                <CardDescription className="text-slate-600">2025 historical vs 2026 projected sales</CardDescription>
              </CardHeader>
              <CardContent>
                <ChartContainer
                  config={{
                    oldSales: {
                      label: "2025 Sales",
                      color: "#6366f1",
                    },
                    newSales: {
                      label: "2026 Forecast",
                      color: "#10b981",
                    },
                  }}
                  className="h-[300px]"
                >
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={comparisonData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#c7d2fe" />
                      <XAxis dataKey="month" className="text-xs" />
                      <YAxis className="text-xs" />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Legend />
                      <Bar dataKey="oldSales" fill="var(--color-oldSales)" radius={[4, 4, 0, 0]} name="2025 Sales (LKR)" />
                      <Bar dataKey="newSales" fill="var(--color-newSales)" radius={[4, 4, 0, 0]} name="2026 Forecast (LKR)" />
                    </BarChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </CardContent>
            </Card>

            <Card className="border border-emerald-200 bg-gradient-to-br from-emerald-50 to-cyan-50 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-[#19183b]">
                  <TrendingUp className="w-5 h-5 text-emerald-600" />
                  Seasonality Improvement Suggestions
                </CardTitle>
                <CardDescription className="text-slate-600">AI-powered recommendations to boost sales</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {suggestions.map((suggestion, index) => (
                  <div key={`${suggestion.title}-${index}`} className="p-4 bg-white rounded-lg border border-emerald-200">
                    <h4 className="font-semibold mb-2 text-[#19183b]">
                      {index + 1}. {suggestion.title}
                    </h4>
                    <p className="text-sm text-slate-600 mb-2">{suggestion.desc}</p>
                    <p className="text-sm font-medium text-emerald-700">
                      Expected Impact: {suggestion.impact || "Provided by MCP model"}
                    </p>
                  </div>
                ))}
                {!suggestions.length && <p className="text-sm text-slate-500">No AI suggestions available for this product.</p>}
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </section>
  )
}
