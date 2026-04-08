"use client"

import { useState } from "react"
import { Send, Bot, User, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { runSalesForecast } from "@/lib/api"

interface Message {
  role: "user" | "assistant"
  content: string
}

export function AiChatSection() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hello! I'm your AI analytics assistant. Upload your CSV data and ask me anything about your product performance, trends, or get strategic recommendations.",
    },
  ])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSend = async () => {
    const userText = input.trim()
    if (!userText || loading) return

    const historyForTool = messages.slice(-10).map((m) => ({ role: m.role, content: m.content }))
    setMessages((prev) => [...prev, { role: "user", content: userText }])
    setInput("")
    setLoading(true)

    try {
      const response = await runSalesForecast(userText, historyForTool)
      const suggestionLine =
        response.did_you_mean && response.did_you_mean.length
          ? `\n\nYou can also ask about: ${response.did_you_mean.join(", ")}.`
          : ""
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: (response.answer || `Forecast ready for ${response.product}.`) + suggestionLine,
        },
      ])
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: error instanceof Error ? `Error: ${error.message}` : "Unable to reach MCP backend.",
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <section
      id="chat"
      className="py-20 bg-gradient-to-br from-[#19183B] via-[#2a2850] to-[#19183B] relative overflow-hidden"
    >
      <div className="absolute inset-0 opacity-30">
        <div className="absolute top-10 right-20 w-64 h-64 bg-[#A1C2BD] rounded-full blur-[100px] animate-pulse"></div>
        <div className="absolute bottom-10 left-20 w-80 h-80 bg-[#708993] rounded-full blur-[120px] animate-pulse delay-700"></div>
      </div>

      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-3xl mx-auto text-center space-y-4 mb-12">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Sparkles className="w-8 h-8 text-[#A1C2BD]" />
            <h2 className="text-4xl font-bold text-white">Ask AI Anything</h2>
            <Sparkles className="w-8 h-8 text-[#A1C2BD]" />
          </div>
          <p className="text-lg text-[#A1C2BD]">
            Get instant answers about your product data, trends, and strategic recommendations
          </p>
        </div>

        <Card className="max-w-4xl mx-auto shadow-2xl border-2 border-[#A1C2BD]/40 bg-white/95 backdrop-blur-md">
          {/* Chat Messages */}
          <div className="h-[500px] overflow-y-auto p-6 space-y-4 bg-gradient-to-b from-[#E7F2EF]/30 to-white/50">
            {messages.map((message, index) => (
              <div key={index} className={`flex gap-3 ${message.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg ${
                    message.role === "user"
                      ? "bg-gradient-to-br from-[#708993] to-[#19183B] text-white"
                      : "bg-gradient-to-br from-[#A1C2BD] to-[#708993] text-white"
                  }`}
                >
                  {message.role === "user" ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 shadow-md ${
                    message.role === "user"
                      ? "bg-gradient-to-br from-[#708993] to-[#19183B] text-white"
                      : "bg-gradient-to-br from-[#E7F2EF] to-white text-[#19183B] border border-[#A1C2BD]/30"
                  }`}
                >
                  <p className="text-sm leading-relaxed">{message.content}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Input Area */}
          <div className="border-t-2 border-[#A1C2BD]/30 p-4 bg-white">
            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSend()}
                placeholder="Ask about your product performance..."
                className="flex-1 border-[#A1C2BD]/40 focus:border-[#A1C2BD] focus:ring-[#A1C2BD]"
                disabled={loading}
              />
              <Button
                onClick={handleSend}
                size="icon"
                className="bg-gradient-to-br from-[#A1C2BD] to-[#708993] hover:from-[#8fb3ae] hover:to-[#5f7580] text-white shadow-lg shadow-[#A1C2BD]/30"
                disabled={loading}
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </section>
  )
}
