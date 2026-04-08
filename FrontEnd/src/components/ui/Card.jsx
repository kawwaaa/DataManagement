export function Card({ className, children }) {
  return <div className={`bg-white rounded-xl border border-gray-200 shadow-sm p-6 ${className || ""}`}>{children}</div>
}

export function CardHeader({ children, className }) {
  return <div className={`mb-4 ${className || ""}`}>{children}</div>
}

export function CardContent({ children, className }) {
  return <div className={className || ""}>{children}</div>
}
