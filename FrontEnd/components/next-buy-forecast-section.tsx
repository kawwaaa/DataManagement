"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Sparkles, TrendingUp } from "lucide-react"
import { getNextBuyForecast, getProductList, type NextBuyForecast } from "@/lib/api"

export function NextBuyForecastSection() {
  const [products, setProducts] = useState<string[]>([])
  const [selectedProduct, setSelectedProduct] = useState("")
  const [forecast, setForecast] = useState<NextBuyForecast | null>(null)
  const [loadingProducts, setLoadingProducts] = useState(true)
  const [loadingForecast, setLoadingForecast] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true
    ;(async () => {
      try {
        const list = await getProductList()
        if (!isMounted) return
        setProducts(list)
        if (list.length > 0) {
          setSelectedProduct((prev) => prev || list[0])
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Failed to load products.")
        }
      } finally {
        if (isMounted) setLoadingProducts(false)
      }
    })()

    return () => {
      isMounted = false
    }
  }, [])

  useEffect(() => {
    if (!selectedProduct) return

    let isMounted = true
    setLoadingForecast(true)
    setError(null)

    ;(async () => {
      try {
        const data = await getNextBuyForecast(selectedProduct)
        if (!isMounted) return
        setForecast(data)
      } catch (err) {
        if (isMounted) {
          setForecast(null)
          setError(err instanceof Error ? err.message : "Failed to load next buy forecast.")
        }
      } finally {
        if (isMounted) setLoadingForecast(false)
      }
    })()

    return () => {
      isMounted = false
    }
  }, [selectedProduct])

  return (
    <section className="py-16 px-4 bg-gradient-to-b from-[#fdfcf6] via-[#fffdf8] to-[#eefbf7]">
      <div className="container mx-auto max-w-6xl space-y-8">
        <div className="text-center space-y-4">
          <div className="inline-flex items-center gap-2 rounded-full border border-amber-200 bg-amber-50 px-4 py-2 text-sm font-medium text-amber-800">
            <Sparkles className="h-4 w-4 text-amber-500" />
            <span>Forecasting Snapshot</span>
          </div>
          <div className="space-y-2">
            <h2 className="text-3xl font-bold text-[#19183b]">Next Buy Forecast</h2>
            <p className="text-slate-600">
              Recommended weekly replenishment plan for <span className="font-semibold text-[#19183b]">{selectedProduct}</span>
            </p>
          </div>
        </div>

        <Card className="border border-amber-100 bg-white/95 shadow-lg">
          <CardHeader>
            <CardTitle className="text-[#19183b]">Select Product</CardTitle>
            <CardDescription className="text-slate-600">
              Choose a product to view the next four weeks of purchase recommendations
            </CardDescription>
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

        {loadingProducts && <p className="text-center text-slate-500">Loading products...</p>}
        {loadingForecast && <p className="text-center text-slate-500">Loading next buy forecast...</p>}
        {error && <p className="text-center text-red-400">{error}</p>}

        {forecast && (
          <>
            <Card className="border border-emerald-100 bg-white/95 shadow-xl shadow-emerald-100/40">
              <CardHeader className="space-y-3">
                <CardTitle className="flex items-center gap-2 text-[#19183b]">
                  <TrendingUp className="h-5 w-5 text-emerald-600" />
                  Planning Insight
                </CardTitle>
                <CardDescription className="text-base leading-7 text-slate-600">{forecast.insight}</CardDescription>
              </CardHeader>
            </Card>

            <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
              {forecast.weeklyForecast.map((weekData) => (
                <Card
                  key={weekData.week}
                  className="overflow-hidden border border-slate-200 bg-white/95 shadow-lg shadow-slate-200/40 transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl"
                >
                  <div className="h-1.5 bg-gradient-to-r from-emerald-400 via-cyan-400 to-sky-500" />
                  <CardHeader className="space-y-4">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-xl text-[#19183b]">{weekData.week}</CardTitle>
                      <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium uppercase tracking-[0.2em] text-slate-500">
                        Forecast
                      </span>
                    </div>
                    <div className="rounded-2xl bg-gradient-to-br from-[#19183b] to-[#24475c] p-5 text-white shadow-lg">
                      <p className="text-sm uppercase tracking-[0.22em] text-emerald-100">Suggested Stock</p>
                      <p className="mt-3 text-3xl font-bold leading-none">Buy: {weekData.suggestedBuy} units</p>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="rounded-2xl border border-slate-100 bg-slate-50 p-4">
                      <p className="mb-2 text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">Reasoning</p>
                      <p className="text-sm leading-6 text-slate-600">{weekData.reason}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </>
        )}
      </div>
    </section>
  )
}
