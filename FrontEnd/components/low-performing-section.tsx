"use client"

import { useEffect, useState } from "react"
import { TrendingDown, Lightbulb } from "lucide-react"
import { Card } from "@/components/ui/card"
import { getLowerProducts, type LowProduct } from "@/lib/api"

export function LowPerformingSection() {
  const [lowProducts, setLowProducts] = useState<LowProduct[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true
    ;(async () => {
      try {
        const data = await getLowerProducts()
        if (isMounted) {
          setLowProducts(data)
          setError(null)
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Failed to load low-performing products.")
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
    <section id="low-performing" className="py-20 bg-gradient-to-b from-[#fff5f5] via-[#fffaf5] to-[#ffffff]">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center space-y-4 mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-red-100 rounded-full text-sm font-medium text-red-800 border border-red-200">
              <TrendingDown className="w-4 h-4 text-red-600" />
              <span>Needs Attention</span>
            </div>
            <h2 className="text-4xl font-bold text-[#19183b]">Low Performing Products</h2>
            <p className="text-lg text-slate-600">
              Products that need strategic improvements with AI-generated recommendations
            </p>
          </div>

          {loading && <p className="text-center text-slate-500">Loading low-performing products...</p>}
          {error && <p className="text-center text-red-400">{error}</p>}

          <div className="grid gap-8">
            {lowProducts.map((product, index) => (
              <Card key={index} className="p-6 hover:shadow-xl transition-shadow border border-red-100/80 bg-white/95">
                <div className="space-y-4">
                  {/* Product Header */}
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-red-100">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500 to-orange-500 text-white flex items-center justify-center text-xl font-bold">
                        {index + 1}
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-[#19183b]">{product.name}</h3>
                        <div className="flex gap-4 text-sm text-slate-600 mt-1">
                          <span>Current: {product.currentSales.toLocaleString()}</span>
                          <span>Predicted: {product.predictedSales.toLocaleString()}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="text-right">
                        <p className="text-2xl font-bold text-red-600">-{product.decline}%</p>
                        <p className="text-xs text-red-700">Decline</p>
                      </div>
                      <TrendingDown className="w-6 h-6 text-red-600" />
                    </div>
                  </div>

                  {/* Suggestions */}
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <Lightbulb className="w-5 h-5 text-amber-500" />
                      <h4 className="font-semibold text-[#19183b]">AI Recommendations</h4>
                    </div>
                    <ul className="space-y-2">
                      {product.suggestions.map((suggestion, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-sm text-slate-600">
                          <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 flex-shrink-0" />
                          <span>{suggestion}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </Card>
            ))}
          </div>
          {!loading && !error && lowProducts.length === 0 && (
            <p className="text-center text-slate-500">No low-performing product data available.</p>
          )}
        </div>
      </div>
    </section>
  )
}
