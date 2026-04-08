# gemini_chat.py - NO PLOT, JUST FORECAST + GEMINI
import requests
import google.generativeai as genai

# === CONFIGURE GEMINI ===
# ← Get from: https://aistudio.google.com
genai.configure(api_key="GEMINI_API_KEY")

# === MCP TOOL URL ===
MCP_TOOL_URL = "http://127.0.0.1:8000/mcp/tools/get_ice_cream_forecast"

# === FETCH FORECAST ===


def get_forecast():
    try:
        r = requests.post(MCP_TOOL_URL, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


# === GEMINI MODEL ===
model = genai.GenerativeModel("gemini-1.5-flash")

# === CHAT LOOP ===
print("ICE CREAM SALES AI")
print("Ask: show forecast | what is growth | best month | exit\n")

forecast = get_forecast()
if "error" in forecast:
    print(f"Error: {forecast['error']}")
    exit()

while True:
    q = input("You: ").strip().lower()
    if q in ["exit", "quit"]:
        break

    # === SHOW FORECAST ===
    if "forecast" in q or "show" in q:
        print(f"\n2026 Forecast:")
        print(f"   Sales: {forecast['sales_2026_lkr']:,} LKR")
        print(f"   Growth: +{forecast['growth_percent']}%")
        print(f"   Peak: {forecast['peak_month']}")
        print(f"   Low: {forecast['low_month']}\n")
        continue

    # === ASK GEMINI ===
    prompt = f"""
    You are an ice cream sales expert.
    2026 Forecast:
    - Sales: {forecast['sales_2026_lkr']:,} LKR
    - Growth: +{forecast['growth_percent']}%
    - Peak: {forecast['peak_month']}
    - Low: {forecast['low_month']}

    User: {q}
    Answer in 2 short sentences.
    """

    try:
        response = model.generate_content(prompt)
        print(f"Gemini: {response.text}\n")
    except Exception as e:
        print(f"Gemini error: {e}\n")
