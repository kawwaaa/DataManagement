import { BarChart3, TrendingUp, Brain } from "lucide-react"

export function HeroSection() {
  return (
    <section className="relative min-h-[600px] bg-[#19183B] text-white overflow-hidden">
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-20 left-10 w-64 h-64 bg-[#A1C2BD] rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-[#708993] rounded-full blur-3xl" />
      </div>

      <div className="container mx-auto px-4 py-20 relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-[#A1C2BD]/20 rounded-full text-sm font-medium">
              <Brain className="w-4 h-4" />
              <span>AI-Powered Analytics</span>
            </div>

            <h1 className="text-5xl lg:text-6xl font-bold leading-tight">
              Transform Your Product Data Into <span className="text-[#A1C2BD]">Actionable Insights</span>
            </h1>

            <p className="text-lg text-white/80 leading-relaxed">
              Upload your product sales data and let our AI analyze performance, predict trends, and provide strategic
              recommendations to boost your business growth.
            </p>

            <div className="flex flex-wrap gap-4 pt-4">
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 rounded-lg bg-[#A1C2BD]/20 flex items-center justify-center">
                  <BarChart3 className="w-5 h-5" />
                </div>
                <div>
                  <p className="font-semibold">Real-time Analysis</p>
                  <p className="text-sm text-white/70">Instant insights</p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <div className="w-10 h-10 rounded-lg bg-[#A1C2BD]/20 flex items-center justify-center">
                  <TrendingUp className="w-5 h-5" />
                </div>
                <div>
                  <p className="font-semibold">Predictive Forecasting</p>
                  <p className="text-sm text-white/70">Future trends</p>
                </div>
              </div>
            </div>
          </div>

          <div className="relative">
            <div className="relative w-full aspect-square max-w-md mx-auto">
              <img
                src="/data-analytics-dashboard.png"
                alt="Data Analytics Dashboard"
                className="w-full h-full object-contain rounded-2xl"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="absolute bottom-0 left-0 right-0">
        <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path
            d="M0 120L60 105C120 90 240 60 360 45C480 30 600 30 720 37.5C840 45 960 60 1080 67.5C1200 75 1320 75 1380 75L1440 75V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z"
            fill="#E7F2EF"
          />
        </svg>
      </div>
    </section>
  )
}
