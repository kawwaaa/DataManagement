"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { BadgePercent, Lightbulb, Link2, ShoppingBasket, TrendingUp } from "lucide-react"
import { getPairwiseAssociations, getPairwiseProductList, type PairwiseAssociationResponse } from "@/lib/api"

export function PairwiseSection() {
  const [products, setProducts] = useState<string[]>([])
  const [selectedProduct, setSelectedProduct] = useState("")
  const [data, setData] = useState<PairwiseAssociationResponse | null>(null)
  const [loadingProducts, setLoadingProducts] = useState(true)
  const [loadingPairs, setLoadingPairs] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true
    ;(async () => {
      try {
        const list = await getPairwiseProductList()
        if (!isMounted) return
        setProducts(list)
        if (list.length > 0) {
          setSelectedProduct((prev) => prev || list[0])
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Failed to load pairwise products.")
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
    setLoadingPairs(true)
    setError(null)

    ;(async () => {
      try {
        const response = await getPairwiseAssociations(selectedProduct, 5)
        if (!isMounted) return
        setData(response)
      } catch (err) {
        if (isMounted) {
          setData(null)
          setError(err instanceof Error ? err.message : "Failed to load pairwise associations.")
        }
      } finally {
        if (isMounted) setLoadingPairs(false)
      }
    })()

    return () => {
      isMounted = false
    }
  }, [selectedProduct])

  return (
    <section className="py-16 px-4 bg-gradient-to-b from-[#f6fbff] via-[#fbfdff] to-[#eef7ff]">
      <div className="container mx-auto max-w-6xl space-y-8">
        <div className="text-center space-y-4">
          <div className="inline-flex items-center gap-2 rounded-full border border-cyan-100 bg-cyan-50 px-4 py-2 text-sm font-medium text-cyan-800">
            <Link2 className="h-4 w-4 text-cyan-600" />
            <span>Apriori Pairwise View</span>
          </div>
          <div className="space-y-2">
            <h2 className="text-3xl font-bold text-[#19183b]">Pairwise Product Analysis</h2>
            <p className="text-slate-600">Select one product to see the top 5 items most frequently purchased with it, plus Gemini-generated sales strategies for each duo.</p>
          </div>
        </div>

        <Card className="border border-cyan-100 bg-white/95 shadow-lg">
          <CardHeader>
            <CardTitle className="text-[#19183b]">Select Product</CardTitle>
            <CardDescription className="text-slate-600">
              Live association results from the apriori transaction dataset
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
        {loadingPairs && <p className="text-center text-slate-500">Loading pairwise associations...</p>}
        {error && <p className="text-center text-red-400">{error}</p>}

        {data && (
          <>
            <div className="rounded-2xl border border-cyan-100 bg-white/80 px-5 py-4 text-sm text-slate-600 shadow-sm">
              Based on <span className="font-semibold text-[#19183b]">{data.totalBills.toLocaleString()}</span> transaction baskets
              from <span className="font-semibold text-[#19183b]">{data.source ?? "pairwise source"}</span>.
            </div>

            <div className="grid gap-5">
              {data.pairs.map((pair, index) => (
                <Card
                  key={`${data.product}-${pair.partner}`}
                  className="border border-slate-200 bg-white/95 shadow-lg shadow-slate-200/40 transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl"
                >
                  <CardContent className="p-6">
                    <div className="flex flex-col gap-5">
                      <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
                        <div className="flex items-start gap-4">
                          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-[#19183b] to-[#2176ae] text-lg font-bold text-white">
                            {index + 1}
                          </div>
                          <div className="space-y-2">
                            <div className="flex flex-wrap items-center gap-3">
                              <h3 className="text-xl font-semibold text-[#19183b]">{data.product} + {pair.partner}</h3>
                              <span className="rounded-full bg-cyan-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-cyan-700">
                                Top Match
                              </span>
                            </div>
                            <p className="max-w-2xl text-sm leading-6 text-slate-600">{pair.reason}</p>
                          </div>
                        </div>

                        <div className="grid gap-3 sm:grid-cols-3">
                          <div className="rounded-2xl border border-slate-100 bg-slate-50 px-4 py-3 text-center">
                            <div className="mb-2 flex items-center justify-center gap-2 text-slate-500">
                              <ShoppingBasket className="h-4 w-4" />
                              <span className="text-xs font-semibold uppercase tracking-[0.18em]">Support</span>
                            </div>
                            <p className="text-2xl font-bold text-[#19183b]">{pair.support}%</p>
                          </div>
                          <div className="rounded-2xl border border-slate-100 bg-slate-50 px-4 py-3 text-center">
                            <div className="mb-2 flex items-center justify-center gap-2 text-slate-500">
                              <BadgePercent className="h-4 w-4" />
                              <span className="text-xs font-semibold uppercase tracking-[0.18em]">Confidence</span>
                            </div>
                            <p className="text-2xl font-bold text-[#19183b]">{pair.confidence}%</p>
                          </div>
                          <div className="rounded-2xl border border-slate-100 bg-slate-50 px-4 py-3 text-center">
                            <div className="mb-2 flex items-center justify-center gap-2 text-slate-500">
                              <Link2 className="h-4 w-4" />
                              <span className="text-xs font-semibold uppercase tracking-[0.18em]">Lift</span>
                            </div>
                            <p className="text-2xl font-bold text-cyan-700">{pair.lift}x</p>
                          </div>
                        </div>
                      </div>

                      <div className="grid gap-4 xl:grid-cols-[1.6fr_0.9fr]">
                        <div className="rounded-2xl border border-cyan-100 bg-gradient-to-br from-cyan-50 via-white to-sky-50 p-5">
                          <div className="mb-4 flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.18em] text-cyan-800">
                            <Lightbulb className="h-4 w-4" />
                            <span>Gemini Strategies</span>
                          </div>
                          <div className="grid gap-3">
                            {pair.strategies.map((strategy, strategyIndex) => (
                              <div
                                key={`${pair.partner}-strategy-${strategyIndex}`}
                                className="rounded-xl border border-white/80 bg-white/90 px-4 py-3 text-sm leading-6 text-slate-700 shadow-sm"
                              >
                                <span className="mr-2 inline-flex h-6 w-6 items-center justify-center rounded-full bg-cyan-100 text-xs font-bold text-cyan-800">
                                  {strategyIndex + 1}
                                </span>
                                {strategy}
                              </div>
                            ))}
                          </div>
                        </div>

                        <div className="grid gap-4">
                          <div className="rounded-2xl border border-emerald-100 bg-emerald-50/80 px-5 py-4">
                            <div className="mb-2 flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.18em] text-emerald-800">
                              <TrendingUp className="h-4 w-4" />
                              <span>Predicted Gain</span>
                            </div>
                            <p className="text-3xl font-bold text-emerald-700">+{pair.expectedSalesIncrease}%</p>
                            <p className="mt-2 text-sm leading-6 text-slate-600">
                              Estimated monthly uplift:{" "}
                              <span className="font-semibold text-[#19183b]">
                                LKR {pair.projectedRevenueLiftLkr.toLocaleString()}
                              </span>
                            </p>
                          </div>

                          <div className="rounded-2xl border border-slate-100 bg-slate-50 px-5 py-4 text-sm leading-6 text-slate-600">
                            Apply all three strategies together to capture more duo purchases from the same basket.
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {!loadingPairs && data.pairs.length === 0 && (
              <p className="text-center text-slate-500">No strong pairwise associations available for this product.</p>
            )}
          </>
        )}
      </div>
    </section>
  )
}
