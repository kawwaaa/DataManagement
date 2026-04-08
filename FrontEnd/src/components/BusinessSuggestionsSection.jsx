import { Sparkles, Calendar, DollarSign, Target, Users } from "lucide-react"
import { Card } from "./ui/Card"

const suggestions = [
  {
    icon: Calendar,
    title: "Seasonal Strategy",
    description:
      "Focus on Q4 holiday campaigns. Historical data shows 35% sales increase during November-December. Prepare inventory and marketing materials early.",
    priority: "High",
  },
  {
    icon: DollarSign,
    title: "Dynamic Pricing",
    description:
      "Implement competitive pricing for top 3 products. Consider 10-15% discount bundles to increase average order value and customer retention.",
    priority: "High",
  },
  {
    icon: Target,
    title: "Product Portfolio",
    description:
      "Expand wireless audio category - showing 45% YoY growth. Consider adding mid-range options to capture broader market segment.",
    priority: "Medium",
  },
  {
    icon: Users,
    title: "Customer Retention",
    description:
      "Launch loyalty program for repeat customers. Data shows 60% of revenue comes from 20% of customers. Reward high-value segments.",
    priority: "Medium",
  },
]

export function BusinessSuggestionsSection() {
  return (
    <section id="suggestions" className="py-20 bg-white">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center space-y-4 mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-100 rounded-full text-sm font-medium text-purple-900">
              <Sparkles className="w-4 h-4" />
              <span>Strategic Insights</span>
            </div>
            <h2 className="text-4xl font-bold text-gray-900">Overall Business Recommendations</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              AI-powered strategic suggestions to optimize your business performance and maximize growth opportunities
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {suggestions.map((suggestion, index) => {
              const Icon = suggestion.icon
              return (
                <Card key={index} className="p-6 hover:shadow-xl transition-all hover:scale-[1.02]">
                  <div className="space-y-4">
                    <div className="flex items-start justify-between">
                      <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center group-hover:scale-110 transition-transform">
                        <Icon className="w-6 h-6 text-blue-600" />
                      </div>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium ${
                          suggestion.priority === "High" ? "bg-red-100 text-red-900" : "bg-yellow-100 text-yellow-900"
                        }`}
                      >
                        {suggestion.priority} Priority
                      </span>
                    </div>

                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">{suggestion.title}</h3>
                      <p className="text-gray-600 leading-relaxed">{suggestion.description}</p>
                    </div>
                  </div>
                </Card>
              )
            })}
          </div>

          <div className="mt-16 text-center">
            <Card className="p-8 bg-blue-600 text-white">
              <div className="max-w-2xl mx-auto space-y-4">
                <h3 className="text-2xl font-bold">Ready to Transform Your Business?</h3>
                <p className="text-blue-100">
                  Upload your product data now and get instant AI-powered insights to drive growth and optimize
                  performance.
                </p>
                <div className="pt-4">
                  <a
                    href="#upload"
                    className="inline-flex items-center justify-center px-8 py-3 bg-white text-blue-600 rounded-lg font-semibold hover:scale-105 transition-transform"
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
