"use client"

import { useEffect, useState } from "react"
import { TrendingUp, DollarSign, Target } from "lucide-react"
import { Card } from "@/components/ui/card"
import { getTopProducts, type TopProduct } from "@/lib/api"

export function TopProductsSection() {
  const [topProducts, setTopProducts] = useState<TopProduct[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true
    ;(async () => {
      try {
        const data = await getTopProducts()
        if (isMounted) {
          setTopProducts(data)
          setError(null)
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Failed to load top products.")
        }
      } finally {
        if (isMounted) setLoading(false)
      }
    })()

    return () => {
      isMounted = false
    }
  }, [])

  return (
    <section id="top-products" className="py-20 bg-gradient-to-b from-[#f3fbf9] via-[#ffffff] to-[#edf6ff]">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center space-y-4 mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-100 rounded-full text-sm font-medium text-emerald-800 border border-emerald-200">
              <TrendingUp className="w-4 h-4 text-emerald-600" />
              <span>Best Performers</span>
            </div>
            <h2 className="text-4xl font-bold text-[#19183b]">Top 5 Products</h2>
            <p className="text-lg text-slate-600">
              Your best-performing products based on AI-powered sales predictions
            </p>
          </div>

          {loading && <p className="text-center text-slate-500">Loading top products...</p>}
          {error && <p className="text-center text-red-400">{error}</p>}

          <div className="grid gap-6">
            {topProducts.map((product, index) => (
              <Card
                key={index}
                className="p-6 hover:shadow-xl transition-all hover:scale-[1.02] group border border-emerald-100/80 bg-white/95"
              >
                <div className="flex flex-col md:flex-row md:items-center gap-6">
                  <div className="flex items-center gap-4 flex-1">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#19183b] to-[#334155] text-white flex items-center justify-center text-xl font-bold group-hover:scale-110 transition-transform">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-[#19183b] mb-1">{product.name}</h3>
                      <div className="flex flex-wrap gap-4 text-sm text-slate-600">
                        <div className="flex items-center gap-1">
                          <DollarSign className="w-4 h-4" />
                          <span>Current: {product.currentSales.toLocaleString()}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Target className="w-4 h-4" />
                          <span>Predicted: {product.predictedSales.toLocaleString()}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <p className="text-2xl font-bold text-emerald-600">+{product.growth}%</p>
                      <p className="text-xs text-emerald-700">Growth</p>
                    </div>
                    <TrendingUp className="w-6 h-6 text-emerald-600" />
                  </div>
                </div>
              </Card>
            ))}
          </div>
          {!loading && !error && topProducts.length === 0 && (
            <p className="text-center text-slate-500">No top product data available.</p>
          )}
        </div>
      </div>
    </section>
  )
}
