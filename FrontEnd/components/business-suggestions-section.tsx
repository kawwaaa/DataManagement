"use client"

import { useEffect, useState } from "react"
import { Sparkles, Calendar, DollarSign, Target, Users } from "lucide-react"
import { Card } from "@/components/ui/card"
import { getBundleSriLanka, type BundleSuggestion } from "@/lib/api"

const suggestionIcons = [Calendar, DollarSign, Target, Users]

export function BusinessSuggestionsSection() {
  const [suggestions, setSuggestions] = useState<BundleSuggestion[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true
    ;(async () => {
      try {
        const data = await getBundleSriLanka()
        if (isMounted) {
          setSuggestions(data.slice(0, 4))
          setError(null)
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Failed to load business suggestions.")
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
    <section id="suggestions" className="py-20 bg-background">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center space-y-4 mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-accent/20 rounded-full text-sm font-medium text-foreground">
              <Sparkles className="w-4 h-4" />
              <span>Strategic Insights</span>
            </div>
            <h2 className="text-4xl font-bold text-foreground text-balance">Overall Business Recommendations</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              AI-powered strategic suggestions to optimize your business performance and maximize growth opportunities
            </p>
          </div>

          {loading && <p className="text-center text-muted-foreground">Loading bundle suggestions...</p>}
          {error && <p className="text-center text-red-400">{error}</p>}

          <div className="grid md:grid-cols-2 gap-6">
            {suggestions.map((suggestion, index) => {
              const Icon = suggestionIcons[index % suggestionIcons.length]
              const preview = suggestion.suggestions?.[0] ?? "No detail provided."
              return (
                <Card key={`${suggestion.primary}-${suggestion.bundle}-${index}`} className="p-6 hover:shadow-xl transition-all hover:scale-[1.02] group">
                  <div className="space-y-4">
                    <div className="flex items-start justify-between">
                      <div className="w-12 h-12 rounded-xl bg-accent/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                        <Icon className="w-6 h-6 text-primary" />
                      </div>
                      <span className="px-3 py-1 rounded-full text-xs font-medium bg-primary/10 text-primary">
                        Lift {suggestion.lift}x
                      </span>
                    </div>

                    <div>
                      <h3 className="text-xl font-semibold text-foreground mb-2">
                        {suggestion.primary} + {suggestion.bundle}
                      </h3>
                      <p className="text-muted-foreground leading-relaxed">{preview}</p>
                      <p className="text-sm text-accent mt-3">
                        Expected Sales Increase: +{suggestion.expectedSalesIncrease}%
                      </p>
                    </div>
                  </div>
                </Card>
              )
            })}
          </div>

          {!loading && !error && suggestions.length === 0 && (
            <p className="text-center text-muted-foreground">No bundle suggestions available.</p>
          )}

          <div className="mt-16 text-center">
            <Card className="p-8 bg-primary text-primary-foreground">
              <div className="max-w-2xl mx-auto space-y-4">
                <h3 className="text-2xl font-bold">Ready to Transform Your Business?</h3>
                <p className="text-primary-foreground/80">
                  Upload your product data now and get instant AI-powered insights to drive growth and optimize
                  performance.
                </p>
                <div className="pt-4">
                  <a
                    href="#upload"
                    className="inline-flex items-center justify-center px-8 py-3 bg-accent text-accent-foreground rounded-lg font-semibold hover:scale-105 transition-transform"
                  >
                    Get Started Now
                  </a>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </section>
  )
}
