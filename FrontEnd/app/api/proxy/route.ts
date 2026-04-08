import { NextRequest, NextResponse } from "next/server"

const BACKEND_BASE_URL =
  process.env.MCP_BACKEND_BASE_URL ??
  process.env.NEXT_PRIVATE_MCP_BASE_URL ??
  "http://127.0.0.1:8000"

const TOOL_NAME_PATTERN = /^[a-zA-Z0-9_]+$/

export async function POST(request: NextRequest) {
  const startedAt = Date.now()
  try {
    const body = (await request.json()) as {
      tool?: string
      args?: Record<string, unknown>
    }

    if (!body?.tool || !TOOL_NAME_PATTERN.test(body.tool)) {
      return NextResponse.json({ error: "Invalid MCP tool name." }, { status: 400 })
    }

    const upstreamUrl = `${BACKEND_BASE_URL.replace(/\/$/, "")}/mcp/tools/${body.tool}`
    console.log(
      `[proxy] -> tool=${body.tool} url=${upstreamUrl} args=${JSON.stringify(body.args ?? {})}`,
    )
    const upstream = await fetch(upstreamUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
      body: JSON.stringify(body.args ?? {}),
    })

    const text = await upstream.text()
    let data: unknown = null
    try {
      data = text ? JSON.parse(text) : null
    } catch {
      data = { raw: text }
    }

    console.log(
      `[proxy] <- tool=${body.tool} status=${upstream.status} elapsed_ms=${Date.now() - startedAt}`,
    )

    return NextResponse.json(data, { status: upstream.status })
  } catch (error) {
    console.error(`[proxy] !! error elapsed_ms=${Date.now() - startedAt}`, error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Proxy request failed." },
      { status: 500 },
    )
  }
}
