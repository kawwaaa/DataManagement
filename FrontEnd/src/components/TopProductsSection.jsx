import { TrendingUp, DollarSign, Target } from "lucide-react"
import { Card } from "./ui/Card"

const topProducts = [
  { name: "Premium Wireless Headphones", currentSales: 15420, predictedSales: 18900, growth: 22.5 },
  { name: "Smart Fitness Tracker", currentSales: 12350, predictedSales: 15200, growth: 23.1 },
  { name: "Portable Power Bank", currentSales: 11200, predictedSales: 13500, growth: 20.5 },
  { name: "Bluetooth Speaker Pro", currentSales: 9800, predictedSales: 11600, growth: 18.4 },
  { name: "USB-C Hub Adapter", currentSales: 8900, predictedSales: 10400, growth: 16.9 },
]

export function TopProductsSection() {
  return (
    <section id="top-products" className="py-20 bg-white">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center space-y-4 mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 rounded-full text-sm font-medium text-blue-900">
              <TrendingUp className="w-4 h-4" />
              <span>Best Performers</span>
            </div>
            <h2 className="text-4xl font-bold text-gray-900">Top 5 Products</h2>
            <p className="text-lg text-gray-600">Your best-performing products based on AI-powered sales predictions</p>
          </div>

          <div className="grid gap-6">
            {topProducts.map((product, index) => (
              <Card key={index} className="p-6 hover:shadow-lg transition-all hover:scale-[1.02]">
                <div className="flex flex-col md:flex-row md:items-center gap-6">
                  <div className="flex items-center gap-4 flex-1">
                    <div className="w-12 h-12 rounded-xl bg-blue-600 text-white flex items-center justify-center text-xl font-bold">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">{product.name}</h3>
                      <div className="flex flex-wrap gap-4 text-sm text-gray-600">
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
                      <p className="text-2xl font-bold text-green-600">+{product.growth}%</p>
                      <p className="text-xs text-gray-500">Growth</p>
                    </div>
                    <TrendingUp className="w-6 h-6 text-green-600" />
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
