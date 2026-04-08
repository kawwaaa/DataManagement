"use client"

import { useState } from "react"
import { HeroSection } from "@/components/hero-section"
import { CsvUploadSection } from "@/components/csv-upload-section"
import { AiChatSection } from "@/components/ai-chat-section"
import { TopProductsSection } from "@/components/top-products-section"
import { LowPerformingSection } from "@/components/low-performing-section"
import { BusinessSuggestionsSection } from "@/components/business-suggestions-section"
import { OverallSalesTrendSection } from "@/components/overall-sales-trend-section"
import { ProductSeasonalAnalysisSection } from "@/components/product-seasonal-analysis-section"
import { NextBuyForecastSection } from "@/components/next-buy-forecast-section"
import { PairwiseSection } from "@/components/pairwise-section"
import { Button } from "@/components/ui/button"
import { TrendingUp, TrendingDown, BarChart3, Calendar, PackageCheck, Network } from "lucide-react"

export default function Home() {
  const [activeSection, setActiveSection] = useState<string | null>(null)

  const toggleSection = (section: string) => {
    setActiveSection((prev) => (prev === section ? null : section))
  }

  return (
    <main className="min-h-screen">
      <HeroSection />
      <CsvUploadSection />
      <AiChatSection />

      <section className="py-20 px-4 bg-gradient-to-br from-[#0a0a1f] via-[#19183B] to-[#2a2850] relative overflow-hidden">
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-20 left-10 w-96 h-96 bg-gradient-to-r from-[#A1C2BD] to-[#708993] rounded-full blur-[150px] animate-pulse"></div>
          <div
            className="absolute bottom-20 right-10 w-[500px] h-[500px] bg-gradient-to-l from-[#708993] to-[#A1C2BD] rounded-full blur-[150px] animate-pulse"
            style={{ animationDelay: "1s" }}
          ></div>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-tr from-[#A1C2BD]/20 to-transparent rounded-full blur-[100px]"></div>
        </div>

        <div className="container mx-auto max-w-6xl relative z-10">
          <h2 className="text-4xl font-bold text-center mb-12 text-transparent bg-clip-text bg-gradient-to-r from-[#E7F2EF] via-[#A1C2BD] to-[#708993]">
            View Insights
          </h2>
          <div className="flex flex-wrap gap-6 justify-center">
            <Button
              onClick={() => toggleSection("topProducts")}
              size="lg"
              className={`group relative flex items-center gap-3 px-8 py-6 text-lg font-semibold overflow-hidden transition-all duration-300 ${
                activeSection === "topProducts"
                  ? "bg-gradient-to-r from-[#A1C2BD] via-[#8fb3ae] to-[#A1C2BD] text-[#19183B] shadow-[0_0_30px_rgba(161,194,189,0.6)] scale-105"
                  : "bg-gradient-to-r from-[#19183B] to-[#2a2850] text-[#A1C2BD] border-2 border-[#A1C2BD] hover:border-[#8fb3ae] hover:shadow-[0_0_25px_rgba(161,194,189,0.4)] hover:scale-105"
              }`}
            >
              <div
                className={`absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-700`}
              ></div>
              <TrendingUp className="w-6 h-6 relative z-10" />
              <span className="relative z-10">Top 5 Products</span>
            </Button>

            <Button
              onClick={() => toggleSection("lowPerforming")}
              size="lg"
              className={`group relative flex items-center gap-3 px-8 py-6 text-lg font-semibold overflow-hidden transition-all duration-300 ${
                activeSection === "lowPerforming"
                  ? "bg-gradient-to-r from-[#708993] via-[#5f7580] to-[#708993] text-white shadow-[0_0_30px_rgba(112,137,147,0.6)] scale-105"
                  : "bg-gradient-to-r from-[#19183B] to-[#2a2850] text-[#708993] border-2 border-[#708993] hover:border-[#5f7580] hover:shadow-[0_0_25px_rgba(112,137,147,0.4)] hover:scale-105"
              }`}
            >
              <div
                className={`absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-700`}
              ></div>
              <TrendingDown className="w-6 h-6 relative z-10" />
              <span className="relative z-10">Low Performing Products</span>
            </Button>

            <Button
              onClick={() => toggleSection("salesTrend")}
              size="lg"
              className={`group relative flex items-center gap-3 px-8 py-6 text-lg font-semibold overflow-hidden transition-all duration-300 ${
                activeSection === "salesTrend"
                  ? "bg-gradient-to-r from-[#6dd5ed] via-[#2193b0] to-[#6dd5ed] text-white shadow-[0_0_30px_rgba(109,213,237,0.6)] scale-105"
                  : "bg-gradient-to-r from-[#19183B] to-[#2a2850] text-[#6dd5ed] border-2 border-[#6dd5ed] hover:border-[#2193b0] hover:shadow-[0_0_25px_rgba(109,213,237,0.4)] hover:scale-105"
              }`}
            >
              <div
                className={`absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-700`}
              ></div>
              <BarChart3 className="w-6 h-6 relative z-10" />
              <span className="relative z-10">Overall Sales Trend</span>
            </Button>

            <Button
              onClick={() => toggleSection("seasonalAnalysis")}
              size="lg"
              className={`group relative flex items-center gap-3 px-8 py-6 text-lg font-semibold overflow-hidden transition-all duration-300 ${
                activeSection === "seasonalAnalysis"
                  ? "bg-gradient-to-r from-[#f093fb] via-[#f5576c] to-[#f093fb] text-white shadow-[0_0_30px_rgba(240,147,251,0.6)] scale-105"
                  : "bg-gradient-to-r from-[#19183B] to-[#2a2850] text-[#f093fb] border-2 border-[#f093fb] hover:border-[#f5576c] hover:shadow-[0_0_25px_rgba(240,147,251,0.4)] hover:scale-105"
              }`}
            >
              <div
                className={`absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-700`}
              ></div>
              <Calendar className="w-6 h-6 relative z-10" />
              <span className="relative z-10">Product Seasonal Analysis</span>
            </Button>

              <Button
                onClick={() => toggleSection("nextBuy")}
                size="lg"
                className={`group relative flex items-center gap-3 px-8 py-6 text-lg font-semibold overflow-hidden transition-all duration-300 ${
                  activeSection === "nextBuy"
                    ? "bg-gradient-to-r from-[#f6c453] via-[#f2a93b] to-[#f6c453] text-[#19183B] shadow-[0_0_30px_rgba(246,196,83,0.55)] scale-105"
                    : "bg-gradient-to-r from-[#19183B] to-[#2a2850] text-[#f6c453] border-2 border-[#f6c453] hover:border-[#f2a93b] hover:shadow-[0_0_25px_rgba(246,196,83,0.35)] hover:scale-105"
                }`}
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-700"></div>
                  <PackageCheck className="w-6 h-6 relative z-10" />
                  <span className="relative z-10">Next Buy</span>
                </Button>

            <Button
              onClick={() => toggleSection("pairwise")}
              size="lg"
              className={`group relative flex items-center gap-3 px-8 py-6 text-lg font-semibold overflow-hidden transition-all duration-300 ${
                activeSection === "pairwise"
                  ? "bg-gradient-to-r from-[#7dd3fc] via-[#38bdf8] to-[#7dd3fc] text-[#19183B] shadow-[0_0_30px_rgba(56,189,248,0.5)] scale-105"
                  : "bg-gradient-to-r from-[#19183B] to-[#2a2850] text-[#7dd3fc] border-2 border-[#7dd3fc] hover:border-[#38bdf8] hover:shadow-[0_0_25px_rgba(56,189,248,0.35)] hover:scale-105"
              }`}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-700"></div>
              <Network className="w-6 h-6 relative z-10" />
              <span className="relative z-10">Pairwise</span>
            </Button>
          </div>
        </div>
      </section>

      {activeSection === "topProducts" && (
        <div className="bg-gradient-to-b from-[#2a2850] via-[#19183B] to-[#0a0a1f]">
          <TopProductsSection />
        </div>
      )}
      {activeSection === "lowPerforming" && (
        <div className="bg-gradient-to-b from-[#2a2850] via-[#1a2530] to-[#0a0a1f]">
          <LowPerformingSection />
        </div>
      )}
      {activeSection === "salesTrend" && (
        <div className="bg-gradient-to-b from-[#2a2850] via-[#1a2a3a] to-[#0a0a1f]">
          <OverallSalesTrendSection />
        </div>
      )}
      {activeSection === "seasonalAnalysis" && (
        <div className="bg-gradient-to-b from-[#2a2850] via-[#2a1a30] to-[#0a0a1f]">
          <ProductSeasonalAnalysisSection />
        </div>
      )}
      {activeSection === "nextBuy" && (
        <div className="bg-gradient-to-b from-[#2a2850] via-[#2a2a24] to-[#0a0a1f]">
          <NextBuyForecastSection />
        </div>
      )}
      {activeSection === "pairwise" && (
        <div className="bg-gradient-to-b from-[#2a2850] via-[#1c2c3b] to-[#0a0a1f]">
          <PairwiseSection />
        </div>
      )}

      <BusinessSuggestionsSection />
    </main>
  )
}
