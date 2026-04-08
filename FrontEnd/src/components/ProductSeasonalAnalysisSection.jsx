"use client"

import { useState } from "react"
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts"
import { Card, CardContent, CardHeader } from "./ui/Card"
import { TrendingUp } from "lucide-react"

const products = [
  { id: "1", name: "Wireless Headphones" },
  { id: "2", name: "Smart Watch" },
  { id: "3", name: "Laptop Stand" },
  { id: "4", name: "USB-C Hub" },
  { id: "5", name: "Mechanical Keyboard" },
]

const seasonalData = [
  { period: "Week 1", sales: 120 },
  { period: "Week 2", sales: 145 },
  { period: "Week 3", sales: 132 },
  { period: "Week 4", sales: 168 },
  { period: "Week 5", sales: 155 },
  { period: "Week 6", sales: 189 },
  { period: "Week 7", sales: 176 },
  { period: "Week 8", sales: 198 },
]

const comparisonData = [
  { month: "Jan", oldSales: 3200, newSales: 3800 },
  { month: "Feb", oldSales: 3500, newSales: 4200 },
  { month: "Mar", oldSales: 3800, newSales: 4600 },
  { month: "Apr", oldSales: 3400, newSales: 4100 },
  { month: "May", oldSales: 4000, newSales: 4900 },
  { month: "Jun", oldSales: 4200, newSales: 5200 },
]

export function ProductSeasonalAnalysisSection() {
  const [selectedProduct, setSelectedProduct] = useState("")

  return (
    <section className="py-16 px-4 bg-white">
      <div className="container mx-auto max-w-6xl space-y-6">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold mb-2 text-gray-900">Product Seasonal Analysis</h2>
          <p className="text-gray-600">Deep dive into individual product performance and seasonality</p>
        </div>

        <Card className="border-2 border-blue-200">
          <CardHeader>
            <h3 className="text-xl font-bold text-gray-900">Select Product</h3>
            <p className="text-gray-600 text-sm">Choose a product to view detailed seasonal analysis</p>
          </CardHeader>
          <CardContent>
            <select
              value={selectedProduct}
              onChange={(e) => setSelectedProduct(e.target.value)}
              className="w-full max-w-md border-2 border-blue-300 rounded-lg px-4 py-2 text-gray-900"
            >
              <option value="">Select a product...</option>
              {products.map((product) => (
                <option key={product.id} value={product.id}>
                  {product.name}
                </option>
              ))}
            </select>
          </CardContent>
        </Card>

        {selectedProduct && (
          <>
            <Card className="border-2 border-blue-200">
              <CardHeader>
                <h3 className="text-xl font-bold text-gray-900">Seasonal Sales Breakdown</h3>
                <p className="text-gray-600 text-sm">
                  Weekly sales trend for {products.find((p) => p.id === selectedProduct)?.name}
                </p>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={seasonalData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                    <XAxis dataKey="period" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="sales" stroke="#A1C2BD" strokeWidth={3} name="Units Sold" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card className="border-2 border-blue-200">
              <CardHeader>
                <h3 className="text-xl font-bold text-gray-900">Sales Comparison</h3>
                <p className="text-gray-600 text-sm">Historical vs projected sales with AI recommendations</p>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={comparisonData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
                    <Legend />
                    <Bar dataKey="oldSales" fill="#708993" radius={[4, 4, 0, 0]} name="Old Sales ($)" />
                    <Bar dataKey="newSales" fill="#A1C2BD" radius={[4, 4, 0, 0]} name="Projected Sales ($)" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card className="border-2 border-blue-200 bg-blue-50">
              <CardHeader>
                <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-blue-600" />
                  Seasonality Improvement Suggestions
                </h3>
                <p className="text-gray-600 text-sm">AI-powered recommendations to boost sales</p>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-4 bg-white rounded-lg border border-blue-200">
                  <h4 className="font-semibold text-gray-900 mb-2">1. Optimize Inventory for Peak Weeks</h4>
                  <p className="text-sm text-gray-600 mb-2">
                    Weeks 4, 6, and 8 show peak demand. Increase inventory by 25% during these periods.
                  </p>
                  <p className="text-sm font-medium text-green-600">Expected Impact: +18% sales increase</p>
                </div>

                <div className="p-4 bg-white rounded-lg border border-blue-200">
                  <h4 className="font-semibold text-gray-900 mb-2">2. Launch Targeted Promotions</h4>
                  <p className="text-sm text-gray-600 mb-2">
                    Run email campaigns during weeks 1-3 to boost early-period sales and smooth demand curve.
                  </p>
                  <p className="text-sm font-medium text-green-600">Expected Impact: +12% sales increase</p>
                </div>

                <div className="p-4 bg-white rounded-lg border border-blue-200">
                  <h4 className="font-semibold text-gray-900 mb-2">3. Bundle with Complementary Products</h4>
                  <p className="text-sm text-gray-600 mb-2">
                    Create product bundles during mid-season to maintain momentum and increase average order value.
                  </p>
                  <p className="text-sm font-medium text-green-600">Expected Impact: +15% sales increase</p>
                </div>

                <div className="mt-6 p-4 bg-blue-100 rounded-lg border-2 border-blue-400">
                  <h3 className="font-bold text-lg text-gray-900 mb-2 flex items-center gap-2">
                    <TrendingUp className="w-6 h-6 text-blue-600" />
                    Total Projected Improvement
                  </h3>
                  <p className="text-2xl font-bold text-blue-600">+45% Sales Increase</p>
                  <p className="text-sm text-gray-600 mt-1">
                    By implementing all three recommendations, you could see an estimated $8,500 additional monthly
                    revenue for this product.
                  </p>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </section>
  )
}
