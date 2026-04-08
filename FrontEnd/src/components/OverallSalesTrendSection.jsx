import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Legend, Tooltip } from "recharts"
import { Card, CardContent, CardHeader } from "./ui/Card"

const salesTrendData = [
  { month: "Jan", oldSales: 45000, expectedSales: 52000 },
  { month: "Feb", oldSales: 48000, expectedSales: 56000 },
  { month: "Mar", oldSales: 52000, expectedSales: 61000 },
  { month: "Apr", oldSales: 49000, expectedSales: 58000 },
  { month: "May", oldSales: 55000, expectedSales: 65000 },
  { month: "Jun", oldSales: 58000, expectedSales: 70000 },
  { month: "Jul", oldSales: 62000, expectedSales: 75000 },
  { month: "Aug", oldSales: 60000, expectedSales: 73000 },
  { month: "Sep", oldSales: 57000, expectedSales: 68000 },
  { month: "Oct", oldSales: 63000, expectedSales: 76000 },
  { month: "Nov", oldSales: 68000, expectedSales: 82000 },
  { month: "Dec", oldSales: 75000, expectedSales: 90000 },
]

export function OverallSalesTrendSection() {
  return (
    <section className="py-16 px-4 bg-white">
      <div className="container mx-auto max-w-6xl">
        <Card className="border-2 border-blue-200">
          <CardHeader>
            <h2 className="text-2xl font-bold text-gray-900">Overall Sales Trend Analysis</h2>
            <p className="text-gray-600 text-sm">Comparison of historical sales vs AI-predicted expected sales</p>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={salesTrendData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
                <Legend />
                <Line type="monotone" dataKey="oldSales" stroke="#708993" strokeWidth={2} name="Old Sales ($)" />
                <Line
                  type="monotone"
                  dataKey="expectedSales"
                  stroke="#A1C2BD"
                  strokeWidth={2}
                  name="Expected Sales ($)"
                />
              </LineChart>
            </ResponsiveContainer>

            <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <h3 className="font-semibold text-lg text-gray-900 mb-2">Key Insights</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>• Expected sales show a consistent 15-20% growth trend compared to historical data</li>
                <li>• Peak season (Nov-Dec) shows the highest growth potential</li>
                <li>• Q2 (Apr-Jun) presents opportunities for targeted marketing campaigns</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  )
}
