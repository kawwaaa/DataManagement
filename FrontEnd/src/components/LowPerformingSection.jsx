import { TrendingDown, Lightbulb } from "lucide-react"
import { Card } from "./ui/Card"

const lowProducts = [
  {
    name: "Basic Phone Case",
    currentSales: 2100,
    predictedSales: 1800,
    decline: -14.3,
    suggestions: [
      "Introduce premium materials or unique designs",
      "Bundle with screen protectors for better value",
      "Target seasonal campaigns (back-to-school, holidays)",
    ],
  },
  {
    name: "Wired Earbuds",
    currentSales: 1850,
    predictedSales: 1500,
    decline: -18.9,
    suggestions: [
      "Emphasize affordability and reliability",
      "Market to budget-conscious consumers",
      "Consider discontinuing and focusing on wireless alternatives",
    ],
  },
  {
    name: "Standard Mouse Pad",
    currentSales: 1600,
    predictedSales: 1350,
    decline: -15.6,
    suggestions: [
      "Add RGB lighting or gaming features",
      "Create limited edition designs",
      "Bundle with gaming peripherals",
    ],
  },
  {
    name: "USB 2.0 Cable",
    currentSales: 1400,
    predictedSales: 1100,
    decline: -21.4,
    suggestions: [
      "Upgrade to USB-C or USB 3.0 variants",
      "Offer multi-pack discounts",
      "Phase out in favor of modern alternatives",
    ],
  },
  {
    name: "DVD Drive",
    currentSales: 980,
    predictedSales: 700,
    decline: -28.6,
    suggestions: [
      "Target niche markets (archival, legacy systems)",
      "Offer steep discounts to clear inventory",
      "Consider discontinuing product line",
    ],
  },
]

export function LowPerformingSection() {
  return (
    <section id="low-performing" className="py-20 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center space-y-4 mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-orange-100 rounded-full text-sm font-medium text-orange-900">
              <TrendingDown className="w-4 h-4" />
              <span>Needs Attention</span>
            </div>
            <h2 className="text-4xl font-bold text-gray-900">Low Performing Products</h2>
            <p className="text-lg text-gray-600">
              Products that need strategic improvements with AI-generated recommendations
            </p>
          </div>

          <div className="grid gap-8">
            {lowProducts.map((product, index) => (
              <Card key={index} className="p-6 hover:shadow-lg transition-shadow">
                <div className="space-y-4">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-gray-200">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-xl bg-orange-500 text-white flex items-center justify-center text-xl font-bold">
                        {index + 1}
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{product.name}</h3>
                        <div className="flex gap-4 text-sm text-gray-600 mt-1">
                          <span>Current: {product.currentSales.toLocaleString()}</span>
                          <span>Predicted: {product.predictedSales.toLocaleString()}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="text-right">
                        <p className="text-2xl font-bold text-red-600">{product.decline}%</p>
                        <p className="text-xs text-gray-500">Decline</p>
                      </div>
                      <TrendingDown className="w-6 h-6 text-red-600" />
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <Lightbulb className="w-5 h-5 text-yellow-500" />
                      <h4 className="font-semibold text-gray-900">AI Recommendations</h4>
                    </div>
                    <ul className="space-y-2">
                      {product.suggestions.map((suggestion, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                          <span className="w-1.5 h-1.5 rounded-full bg-yellow-500 mt-1.5 flex-shrink-0" />
                          <span>{suggestion}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
