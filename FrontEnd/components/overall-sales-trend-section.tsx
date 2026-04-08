"use client"

import { useEffect, useMemo, useState } from "react"
import { Line, LineChart, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Legend } from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { getMonthlyForecastByYear, getProductList } from "@/lib/api"

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

export function OverallSalesTrendSection() {
  const [salesTrendData, setSalesTrendData] = useState<
    { month: string; oldSales: number; expectedSales: number }[]
  >([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true
    ;(async () => {
      try {
        const products = await getProductList()
        const scopedProducts = products.slice(0, 12)
        const byProduct = await Promise.all(scopedProducts.map((name) => getMonthlyForecastByYear(name)))

        const totals = MONTHS.map((month) => ({ month, oldSales: 0, expectedSales: 0 }))
        for (const yearData of byProduct) {
          for (const row of totals) {
            row.oldSales += Number(yearData["2025"]?.[row.month] ?? 0)
            row.expectedSales += Number(yearData["2026"]?.[row.month] ?? 0)
          }
        }

        if (isMounted) {
          setSalesTrendData(totals)
          setError(null)
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Failed to load overall sales trend.")
        }
      } finally {
        if (isMounted) setLoading(false)
      }
    })()

    return () => {
      isMounted = false
    }
  }, [])

  const insightText = useMemo(() => {
    if (!salesTrendData.length) return []
    const oldTotal = salesTrendData.reduce((sum, m) => sum + m.oldSales, 0)
    const expectedTotal = salesTrendData.reduce((sum, m) => sum + m.expectedSales, 0)
    const growthPct = oldTotal ? ((expectedTotal - oldTotal) / oldTotal) * 100 : 0
    const peak = salesTrendData.reduce((best, row) => (row.expectedSales > best.expectedSales ? row : best), salesTrendData[0])
    return [
      `Projected yearly growth is ${growthPct.toFixed(1)}% versus 2025 baseline.`,
      `Peak projected month is ${peak.month} with ${peak.expectedSales.toLocaleString()} LKR.`,
      "Trend line is aggregated from the first 12 products returned by MCP.",
    ]
  }, [salesTrendData])

  return (
    <section className="py-16 px-4 bg-gradient-to-b from-[#eff6ff] via-[#f8fbff] to-[#ffffff]">
      <div className="container mx-auto max-w-6xl">
        <Card className="border border-blue-200 bg-white/95 shadow-lg">
          <CardHeader>
            <CardTitle className="text-2xl text-[#19183b]">Overall Sales Trend Analysis</CardTitle>
            <CardDescription className="text-slate-600">
              Comparison of 2025 vs 2026 monthly totals from MCP forecast tools
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading && <p className="text-center text-slate-500 mb-4">Loading overall trend...</p>}
            {error && <p className="text-center text-red-400 mb-4">{error}</p>}

            <ChartContainer
              config={{
                oldSales: {
                  label: "2025 Sales",
                  color: "#64748b",
                },
                expectedSales: {
                  label: "2026 Forecast",
                  color: "#10b981",
                },
              }}
              className="h-[400px]"
            >
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={salesTrendData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#dbeafe" />
                  <XAxis dataKey="month" className="text-xs" />
                  <YAxis className="text-xs" />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="oldSales"
                    stroke="var(--color-oldSales)"
                    strokeWidth={2}
                    dot={{ r: 4 }}
                    name="2025 Sales (LKR)"
                  />
                  <Line
                    type="monotone"
                    dataKey="expectedSales"
                    stroke="var(--color-expectedSales)"
                    strokeWidth={2}
                    dot={{ r: 4 }}
                    name="2026 Forecast (LKR)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </ChartContainer>

            <div className="mt-6 p-4 bg-gradient-to-r from-emerald-50 to-cyan-50 rounded-lg border border-emerald-200">
              <h3 className="font-semibold text-lg mb-2 text-[#19183b]">Key Insights</h3>
              <ul className="space-y-2 text-sm text-slate-700">
                {insightText.map((line) => (
                  <li key={line}>- {line}</li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  )
}
