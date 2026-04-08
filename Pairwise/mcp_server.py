# mcp_server.py - FINAL, NO app=app, WORKS 100%
from math import e
from typing import AsyncGenerator
import difflib
import re
from unittest import result
from fastmcp import FastMCP
import json
import os
from functools import lru_cache
from datetime import date, timedelta
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()  # ← ADD THIS LINE

print("Current working directory:", os.getcwd())
print("Does .env exist?", os.path.exists(".env"))
print("GEMINI_API_KEY from os.getenv:", os.getenv("GEMINI_API_KEY"))

if not os.getenv("GEMINI_API_KEY"):
    print("ERROR: GEMINI_API_KEY not found!")
    print("Check .env file in:", os.getcwd())
    exit(1)

# === CREATE SERVER ===


class FastMCPWithCORS(FastMCP):
    def streamable_http_app(self) -> Starlette:
        """Return StreamableHTTP server app with CORS middleware"""
        # Get the original Starlette app
        app = super().streamable_http_app()

        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            # Allow Next.js dev server (3000), Vite (5173), and production URLs
            allow_origins=[
                "http://localhost:3000",
                "http://localhost:5173",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173",
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        return app

    def sse_app(self, mount_path: str | None = None) -> Starlette:
        """Return SSE server app with CORS middleware"""
        # Get the original Starlette app
        app = super().sse_app(mount_path)

        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            # Allow Next.js dev server (3000), Vite (5173), and production URLs
            allow_origins=[
                "http://localhost:3000",
                "http://localhost:5173",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173",
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        return app


# === TOOL ===
mcp = FastMCPWithCORS("Ice Cream Forecast", port=8000, host="0.0.0.0")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FORECAST_DATA_PATH = os.path.join(BASE_DIR, "forecasts", "all_2026.json")
HISTORICAL_ALL_PATH = os.path.join(BASE_DIR, "data", "historical_all.csv")
NEXT_BUY_OVERRIDES_PATH = os.path.join(BASE_DIR, "data", "next_buy_overrides.json")
PAIRWISE_TRANSACTIONS_PATH = os.path.join(BASE_DIR, "transaction_apriori.csv")
MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


def _extract_tool_result_payload(tool_result):
    """Convert FastMCP ToolResult into plain JSON payload for REST compatibility."""
    structured = getattr(tool_result, "structured_content", None)
    if isinstance(structured, dict):
        # Non-object outputs are wrapped as {"result": ...} by FastMCP.
        if "result" in structured and len(structured) == 1:
            return structured["result"]
        return structured

    content = getattr(tool_result, "content", None) or []
    if len(content) == 1 and getattr(content[0], "type", None) == "text":
        text = getattr(content[0], "text", "")
        if isinstance(text, str):
            try:
                return json.loads(text)
            except Exception:
                return text

    serializable = []
    for block in content:
        serializable.append({
            "type": getattr(block, "type", None),
            "text": getattr(block, "text", None),
        })
    return {"content": serializable}


def _normalize_product_name(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


@lru_cache(maxsize=1)
def _load_forecast_rows() -> list:
    if not os.path.exists(FORECAST_DATA_PATH):
        return []
    with open(FORECAST_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _find_forecast_product(product_name: str) -> dict | None:
    wanted = _normalize_product_name(product_name)
    rows = _load_forecast_rows()

    for row in rows:
        candidate = str(row.get("product", ""))
        if _normalize_product_name(candidate) == wanted:
            return row

    for row in rows:
        candidate = str(row.get("product", ""))
        normalized = _normalize_product_name(candidate)
        if wanted in normalized or normalized in wanted:
            return row

    return None


def _estimate_pair_monthly_revenue_lkr(primary: str, partner: str) -> float:
    primary_row = _find_forecast_product(primary) or {}
    partner_row = _find_forecast_product(partner) or {}

    primary_2026 = float(primary_row.get("sales_2026_lkr", 0) or 0)
    partner_2026 = float(partner_row.get("sales_2026_lkr", 0) or 0)

    if primary_2026 and partner_2026:
        return (primary_2026 + partner_2026) / 12.0
    if primary_2026:
        return primary_2026 / 12.0
    if partner_2026:
        return partner_2026 / 12.0
    return 0.0


@lru_cache(maxsize=256)
def _generate_pairwise_plan_with_gemini(primary: str, partner: str, pair_count: int, confidence_pct: float, lift: float) -> dict:
    monthly_pair_revenue = _estimate_pair_monthly_revenue_lkr(primary, partner)
    fallback_increase = round(max(6.0, min(24.0, lift * 5.5 + confidence_pct * 0.04)), 1)
    fallback_lkr = int(round(monthly_pair_revenue * (fallback_increase / 100.0)))

    prompt = f"""
You are the best supermarket cross-sell strategist for Sri Lankan retail.

Product duo:
- Primary: {primary}
- Partner: {partner}
- Pair count: {pair_count}
- Confidence: {confidence_pct:.2f}%
- Lift: {lift:.2f}x
- Estimated combined monthly sales baseline: LKR {monthly_pair_revenue:,.0f}

Task:
Give exactly 3 different, practical strategies to maximize sales of this duo in-store and digitally.

Rules:
- Keep each strategy under 18 words
- Make them specific and actionable
- Cover different tactics such as display, pricing, cashier prompt, sampling, WhatsApp, weekend offer, end-cap, etc.
- Predict a realistic sales increase percent for applying the full 3-strategy plan together
- Do not mention AI, Gemini, assumptions, or confidence

Return ONLY valid JSON in this shape:
{{
  "strategies": [
    "Strategy 1",
    "Strategy 2",
    "Strategy 3"
  ],
  "expectedSalesIncrease": 12.5
}}
"""

    try:
        response = model.generate_content(prompt)
        raw = (response.text or "").strip().replace("```json", "").replace("```", "").strip()
        parsed = json.loads(raw)
        strategies = parsed.get("strategies", []) if isinstance(parsed, dict) else []
        expected = float(parsed.get("expectedSalesIncrease", fallback_increase)) if isinstance(parsed, dict) else fallback_increase

        clean_strategies = [
            str(item).strip()
            for item in strategies
            if str(item).strip()
        ][:3]

        if len(clean_strategies) < 3:
            raise ValueError("Gemini returned fewer than 3 strategies")

        expected = round(max(3.0, min(35.0, expected)), 1)
        return {
            "strategies": clean_strategies,
            "expectedSalesIncrease": expected,
            "projectedRevenueLiftLkr": int(round(monthly_pair_revenue * (expected / 100.0))),
        }
    except Exception as e:
        print(f"Pairwise Gemini fallback for {primary} + {partner}: {e}")
        return {
            "strategies": [
                f"Place {primary} beside {partner} with a bold 'Most Bought Together' shelf strip.",
                f"Offer a weekend duo discount on {primary} + {partner} to trigger basket upgrades.",
                f"Prompt cashiers and WhatsApp promos to recommend {partner} when shoppers pick {primary}.",
            ],
            "expectedSalesIncrease": fallback_increase,
            "projectedRevenueLiftLkr": fallback_lkr,
        }


@lru_cache(maxsize=1)
def _load_historical_metrics() -> dict:
    if not os.path.exists(HISTORICAL_ALL_PATH):
        return {}

    df = pd.read_csv(HISTORICAL_ALL_PATH)
    if df.empty:
        return {}

    df["ds"] = pd.to_datetime(df["ds"])
    metrics = {}
    for product, group in df.groupby("product"):
        total_units = float(group["units"].sum())
        total_amount = float(group["amount"].sum())
        price = (total_amount / total_units) if total_units else 0.0

        last_90_cutoff = group["ds"].max() - pd.Timedelta(days=89)
        recent = group[group["ds"] >= last_90_cutoff]
        recent_units = float(recent["units"].sum())
        recent_daily_units = (recent_units / 90.0) if recent_units else 0.0

        metrics[product] = {
            "avg_unit_price": round(price, 2),
            "recent_daily_units": round(recent_daily_units, 2),
            "avg_monthly_units": round(total_units / max(group["ds"].dt.to_period("M").nunique(), 1), 2),
        }

    return metrics


@lru_cache(maxsize=1)
def _load_product_daily_history() -> dict:
    if not os.path.exists(HISTORICAL_ALL_PATH):
        return {}

    df = pd.read_csv(HISTORICAL_ALL_PATH)
    if df.empty:
        return {}

    df["ds"] = pd.to_datetime(df["ds"])
    df["dow"] = df["ds"].dt.day_name()
    df["day"] = df["ds"].dt.day
    df["is_weekend"] = df["ds"].dt.dayofweek >= 5
    df["is_month_end_window"] = df["day"] >= 25

    history = {}
    for product, group in df.groupby("product"):
        recent = group.sort_values("ds").tail(180)
        if recent.empty:
            recent = group

        dow_profile = {
            dow: round(float(value), 2)
            for dow, value in recent.groupby("dow")["units"].mean().to_dict().items()
        }
        weekend_avg = float(recent[recent["is_weekend"]]["units"].mean() or 0.0)
        weekday_avg = float(recent[~recent["is_weekend"]]["units"].mean() or 0.0)
        month_end_avg = float(recent[recent["is_month_end_window"]]["units"].mean() or 0.0)
        regular_days = recent[~recent["is_month_end_window"]]
        regular_avg = float(regular_days["units"].mean() or 0.0)

        history[product] = {
            "dow_profile": dow_profile,
            "weekend_avg_units": round(weekend_avg, 2),
            "weekday_avg_units": round(weekday_avg, 2),
            "month_end_avg_units": round(month_end_avg, 2),
            "regular_avg_units": round(regular_avg, 2),
        }

    return history


@lru_cache(maxsize=1)
def _load_holidays_by_month_day() -> dict:
    holiday_path = os.path.join(BASE_DIR, "holidays.csv")
    if not os.path.exists(holiday_path):
        return {}

    try:
        holidays_df = pd.read_csv(holiday_path)
        holidays_df["ds"] = pd.to_datetime(holidays_df["ds"])
    except Exception:
        return {}

    mapping = {}
    for _, row in holidays_df.iterrows():
        month_day = row["ds"].strftime("%m-%d")
        mapping.setdefault(month_day, []).append(str(row.get("holiday", "")).strip())
    return mapping


@lru_cache(maxsize=1)
def _load_pairwise_transactions() -> tuple[list[set[str]], dict[str, int], int]:
    if not os.path.exists(PAIRWISE_TRANSACTIONS_PATH):
        return [], {}, 0

    df = pd.read_csv(PAIRWISE_TRANSACTIONS_PATH)
    if df.empty or "unique_bill_id" not in df.columns or "Descrip" not in df.columns:
        return [], {}, 0

    df["Descrip"] = df["Descrip"].fillna("").astype(str).str.strip()
    df = df[df["Descrip"] != ""]
    grouped = df.groupby("unique_bill_id")["Descrip"].apply(lambda items: sorted(set(items.tolist())))

    baskets = [set(items) for items in grouped.tolist() if items]
    counts = {}
    for basket in baskets:
        for item in basket:
            counts[item] = counts.get(item, 0) + 1

    return baskets, counts, len(baskets)


def _load_next_buy_overrides() -> dict:
    if not os.path.exists(NEXT_BUY_OVERRIDES_PATH):
        return {}
    try:
        with open(NEXT_BUY_OVERRIDES_PATH, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _save_next_buy_overrides(payload: dict) -> None:
    os.makedirs(os.path.dirname(NEXT_BUY_OVERRIDES_PATH), exist_ok=True)
    with open(NEXT_BUY_OVERRIDES_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def _find_forecast_row(product_name: str, rows: list) -> dict | None:
    wanted = _normalize_product_name(product_name)
    if not wanted:
        return None

    for row in rows:
        if _normalize_product_name(row.get("product", "")) == wanted:
            return row

    for row in rows:
        normalized = _normalize_product_name(row.get("product", ""))
        if wanted in normalized or normalized in wanted:
            return row

    return None


def _build_next_buy_reason(
    month_name: str,
    peak_month: str,
    growth_percent: float,
    recent_daily_units: float,
    safety_factor: float,
    holiday_names: list | None = None,
    salary_cycle_signal: bool = False,
    weekend_lift_ratio: float = 0.0,
) -> str:
    if holiday_names:
        holiday_text = ", ".join(holiday_names[:2])
        return f"Demand is expected to lift around {holiday_text}, so extra stock is held for higher basket sizes."
    if salary_cycle_signal and weekend_lift_ratio > 0.05:
        return f"The week overlaps the late-month weekend, which often sees stronger salary-cycle shopping and higher weekend take-up."
    if month_name == peak_month:
        return f"Projected demand peaks in {month_name}, so a {round((safety_factor - 1) * 100)}% buffer is added to protect availability."
    if growth_percent > 0:
        return f"Recent sales momentum is positive at {growth_percent:+.1f}%, so stock is lifted above the baseline weekly run rate."
    if recent_daily_units > 0:
        return f"Suggested stock tracks the recent sell-through pace of about {recent_daily_units:.1f} units per day with a safety buffer."
    return f"Suggested stock is derived from the monthly 2026 forecast for {month_name} with a conservative replenishment buffer."


def _generate_week_reasoning_with_gemini(product_name: str, insight: str, week_contexts: list) -> list | None:
    if not week_contexts:
        return None

    compact_context = []
    for item in week_contexts:
        compact_context.append({
            "week": item["week"],
            "month": item["month"],
            "suggested_buy": item["suggested_buy"],
            "growth_percent": item["growth_percent"],
            "peak_month": item["peak_month"],
            "weekend_lift_ratio": round(item["weekend_lift_ratio"], 3),
            "month_end_lift_ratio": round(item["month_end_lift_ratio"], 3),
            "salary_cycle_signal": item["salary_cycle_signal"],
            "holidays": item["holidays"],
            "weekdays": item["weekdays"],
        })

    prompt = f"""
You are generating weekly replenishment reasons for a Sri Lankan retail dashboard.
Write one short, concrete reason per week for the product below.

Product: {product_name}
Forecast method: {insight}
Week contexts: {json.dumps(compact_context, ensure_ascii=True)}

Rules:
- Return JSON only
- Format: {{"reasons":[{{"week":"Week 1","reason":"..."}}, ...]}}
- 1 sentence per week
- Use actual signals from the context, not generic wording
- If `salary_cycle_signal` is true, you may mention month-end salary shopping or stronger late-month basket sizes
- If holidays are present, mention the holiday by name
- If weekend_lift_ratio is strong, mention weekend demand
- Do not mention Gemini, models, or probabilities
"""

    try:
        response = model.generate_content(prompt)
        text = (response.text or "").strip()
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None
        parsed = json.loads(match.group(0))
        rows = parsed.get("reasons", [])
        if not isinstance(rows, list):
            return None
        by_week = {}
        for row in rows:
            if isinstance(row, dict) and row.get("week") and row.get("reason"):
                by_week[str(row["week"])] = str(row["reason"]).strip()
        return [by_week.get(item["week"], "") for item in week_contexts]
    except Exception:
        return None


def _generate_next_buy_forecast(product_name: str) -> dict:
    rows = _load_forecast_rows()
    row = _find_forecast_row(product_name, rows)
    if not row:
        return {"error": f"Product '{product_name}' not found in forecast data."}

    metrics = _load_historical_metrics().get(row["product"], {})
    history = _load_product_daily_history().get(row["product"], {})
    holiday_lookup = _load_holidays_by_month_day()
    avg_unit_price = float(metrics.get("avg_unit_price") or 0.0)
    recent_daily_units = float(metrics.get("recent_daily_units") or 0.0)
    monthly_2026 = row.get("monthly_2026_lkr", {})
    growth_percent = float(row.get("growth_percent") or 0.0)
    peak_month = row.get("peak_month", "")
    peak_month_index = MONTH_NAMES.index(peak_month) if peak_month in MONTH_NAMES else -1
    weekend_avg_units = float(history.get("weekend_avg_units") or 0.0)
    weekday_avg_units = float(history.get("weekday_avg_units") or 0.0)
    month_end_avg_units = float(history.get("month_end_avg_units") or 0.0)
    regular_avg_units = float(history.get("regular_avg_units") or 0.0)

    if avg_unit_price <= 0:
        avg_unit_price = 1.0

    today = date.today()
    weekly_forecast = []
    week_contexts = []

    for index in range(4):
        week_start = today + timedelta(days=index * 7)
        week_dates = [week_start + timedelta(days=offset) for offset in range(7)]
        month_name = week_start.strftime("%B")
        monthly_sales_lkr = float(monthly_2026.get(month_name, 0) or 0)
        estimated_monthly_units = monthly_sales_lkr / avg_unit_price if avg_unit_price else 0
        base_week_units = estimated_monthly_units / 4.33 if estimated_monthly_units else max(recent_daily_units * 7, 0)
        holiday_names = []
        for day_value in week_dates:
            holiday_names.extend(holiday_lookup.get(day_value.strftime("%m-%d"), []))
        holiday_names = list(dict.fromkeys(holiday_names))
        salary_cycle_signal = any(day_value.day >= 25 and day_value.weekday() >= 4 for day_value in week_dates)
        weekend_lift_ratio = ((weekend_avg_units - weekday_avg_units) / weekday_avg_units) if weekday_avg_units > 0 else 0.0
        month_end_lift_ratio = ((month_end_avg_units - regular_avg_units) / regular_avg_units) if regular_avg_units > 0 else 0.0

        safety_factor = 1.10
        if growth_percent > 0:
            safety_factor += min(growth_percent / 100.0, 0.12)
        if month_name == peak_month:
            safety_factor += 0.08
        elif peak_month_index >= 0 and MONTH_NAMES.index(month_name) + 1 == peak_month_index:
            safety_factor += 0.04
        if holiday_names:
            safety_factor += 0.06
        if salary_cycle_signal and month_end_lift_ratio > 0.05:
            safety_factor += 0.05
        if weekend_lift_ratio > 0.08:
            safety_factor += min(weekend_lift_ratio, 0.06)

        suggested_buy = max(1, int(round(base_week_units * safety_factor)))
        week_label = f"Week {index + 1}"
        weekly_forecast.append({
            "week": week_label,
            "suggestedBuy": suggested_buy,
            "reason": _build_next_buy_reason(
                month_name=month_name,
                peak_month=peak_month,
                growth_percent=growth_percent,
                recent_daily_units=recent_daily_units,
                safety_factor=safety_factor,
                holiday_names=holiday_names,
                salary_cycle_signal=salary_cycle_signal,
                weekend_lift_ratio=weekend_lift_ratio,
            ),
        })
        week_contexts.append({
            "week": week_label,
            "month": month_name,
            "suggested_buy": suggested_buy,
            "growth_percent": growth_percent,
            "peak_month": peak_month,
            "holidays": holiday_names,
            "salary_cycle_signal": salary_cycle_signal,
            "weekend_lift_ratio": weekend_lift_ratio,
            "month_end_lift_ratio": month_end_lift_ratio,
            "weekdays": [day_value.strftime("%A") for day_value in week_dates],
        })

    insight = (
        f"Generated from 2026 monthly forecast revenue, converted to units using an estimated average selling price of "
        f"{avg_unit_price:.2f} LKR from historical sales, then adjusted with recent sell-through and seasonality signals."
    )

    generated_reasons = _generate_week_reasoning_with_gemini(row["product"], insight, week_contexts)
    if generated_reasons:
        for item, reason in zip(weekly_forecast, generated_reasons):
            if reason:
                item["reason"] = reason

    return {
        "product": row["product"],
        "insight": insight,
        "weeklyForecast": weekly_forecast,
        "source": {
            "forecast_file": "forecasts/all_2026.json",
            "history_file": "data/historical_all.csv",
            "override_file": "data/next_buy_overrides.json",
        },
    }


@mcp.custom_route("/mcp/tools/{tool_name}", methods=["POST"])
async def call_tool_by_name(request: Request) -> JSONResponse:
    """Compatibility route: call MCP tool directly by name via REST path."""
    tool_name = request.path_params.get("tool_name", "")
    if not tool_name:
        return JSONResponse({"error": "Missing tool name."}, status_code=400)

    try:
        args = await request.json()
        if not isinstance(args, dict):
            return JSONResponse({"error": "Request body must be a JSON object."}, status_code=400)
    except Exception:
        args = {}

    print(f"[mcp-http] -> tool={tool_name} args={args}")

    try:
        tool_result = await mcp._tool_manager.call_tool(tool_name, args)
    except Exception as e:
        print(f"[mcp-http] !! tool={tool_name} error={e}")
        return JSONResponse({"error": f"Tool call failed: {str(e)}"}, status_code=404)

    payload = _extract_tool_result_payload(tool_result)
    print(f"[mcp-http] <- tool={tool_name} ok type={type(payload).__name__}")
    return JSONResponse(payload, status_code=200)


# @mcp.tool()
# def get_ice_cream_forecast() -> dict:
#     path = "forecasts/all_2026.json"
#     if not os.path.exists(path):
#         return {"error": "Run forecast_product.py first!"}
#     with open(path) as f:
#         return json.load(f)
# === TOOL: SALES FORECAST WITH GEMINI + HOLIDAYS ===
# === FIXED TOOL: sales_forecast ===
# @mcp.tool()
# def sales_forecast(prompt: str) -> dict:
#     """
#     Ask about any product in 2026.
#     Example: "How will Coconut sales be in 2026?"
#     """
#     try:
#         # --- 1. Load Data ---
#         forecast_path = "forecasts/all_2026.json"
#         if not os.path.exists(forecast_path):
#             return {"error": "Forecast data not found. Run forecast_product.py first."}

#         with open(forecast_path) as f:
#             data = json.load(f)

#         # --- 2. Find Product ---
#         prompt_lower = prompt.lower()
#         product = None
#         for item in data:
#             if item["product"].lower() in prompt_lower or any(word in prompt_lower for word in item["product"].lower().split()):
#                 product = item
#                 break

#         if not product:
#             similar = [p["product"] for p in data if any(
#                 word in p["product"].lower() for word in prompt_lower.split())]
#             return {
#                 "error": "Product not found.",
#                 "did_you_mean": similar[:3] if similar else None,
#                 "available": [p["product"] for p in data[:5]]
#             }

#         prod_name = product["product"]

#         # --- 3. Build Insight ---
#         growth = product["growth_percent"]
#         peak = product["peak_month"]
#         sales_2026 = f"{product['sales_2026_lkr']:,} LKR"
#         sales_2025 = f"{product['sales_2025_lkr']:,} LKR"

#         # Simple logic for peak reason
#         peak_reasons = {
#             "April": "Sinhala/Tamil New Year + summer demand",
#             "December": "Christmas + year-end gifting",
#             "October": "Post-monsoon recovery + festival prep",
#             "August": "Asala Perahera (for non-meat), recovery for others"
#         }
#         reason = peak_reasons.get(peak, "seasonal demand patterns")

#         # --- 4. Gemini (Optional - Fast Fallback) ---
#         try:
#             gemini_prompt = f"""
#             Product: {prod_name}
#             2026 Sales: {sales_2026} (+{growth:+.1f}%)
#             Peak: {peak} ({reason})
#             Question: {prompt}
#             Answer in 2 short, confident sentences.
#             """
#             response = model.generate_content(gemini_prompt)
#             insight = response.text.strip()
#         except:
#             insight = f"{prod_name} is projected to earn {sales_2026} in 2026, a {growth:+.1f}% change from {sales_2025}. Peak demand hits in {peak} due to {reason}."

#         # --- 5. Return ---
#         return {
#             "product": prod_name,
#             "your_question": prompt,
#             "answer": insight,
#             "2026_sales_lkr": product["sales_2026_lkr"],
#             "growth_percent": growth,
#             "peak_month": peak,
#             "peak_reason": reason,
#             "monthly_2026": product["monthly_2026_lkr"]
#         }

#     except Exception as e:
#         return {"error": f"Tool error: {str(e)}"}

@mcp.tool()
def sales_forecast(prompt: str, history: list = None) -> dict:
    """
    Conversational sales analytics:
    - Handles typos/partial product names
    - Uses chat history for follow-up questions
    - Answers product-level or portfolio-level questions
    """
    month_aliases = {
        "jan": "January", "january": "January",
        "feb": "February", "february": "February",
        "mar": "March", "march": "March",
        "apr": "April", "april": "April",
        "may": "May",
        "jun": "June", "june": "June",
        "jul": "July", "july": "July",
        "aug": "August", "august": "August",
        "sep": "September", "sept": "September", "september": "September",
        "oct": "October", "october": "October",
        "nov": "November", "november": "November",
        "dec": "December", "december": "December",
    }

    def normalize(text: str) -> str:
        return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()

    def extract_month(text: str):
        words = normalize(text).split()
        for w in words:
            if w in month_aliases:
                return month_aliases[w]
        return None

    def load_forecast_data():
        forecast_path = "forecasts/all_2026.json"
        if not os.path.exists(forecast_path):
            return []
        with open(forecast_path) as f:
            return json.load(f)

    def find_product_from_text(text: str, rows: list):
        text_norm = normalize(text)
        if not text_norm:
            return None

        for row in rows:
            pname = row.get("product", "")
            pname_norm = normalize(pname)
            if pname_norm and pname_norm in text_norm:
                return row

        prompt_tokens = set(text_norm.split())
        best_row = None
        best_score = 0
        for row in rows:
            tokens = [t for t in normalize(row.get("product", "")).split() if len(t) > 2]
            if not tokens:
                continue
            overlap = sum(1 for t in tokens if t in prompt_tokens)
            score = overlap / len(tokens)
            if score > best_score and overlap > 0:
                best_score = score
                best_row = row
        if best_row and best_score >= 0.5:
            return best_row

        # token-level fuzzy match (helps with misspellings like "buttter")
        best_row = None
        best_ratio = 0.0
        for row in rows:
            tokens = [t for t in normalize(row.get("product", "")).split() if len(t) > 2]
            if not tokens:
                continue
            row_best = 0.0
            for p_tok in prompt_tokens:
                if len(p_tok) < 4:
                    continue
                for t in tokens:
                    ratio = difflib.SequenceMatcher(None, p_tok, t).ratio()
                    if ratio > row_best:
                        row_best = ratio
            if row_best > best_ratio:
                best_ratio = row_best
                best_row = row
        if best_row and best_ratio >= 0.82:
            return best_row

        names = [row.get("product", "") for row in rows if row.get("product")]
        if names:
            normalized_names = [normalize(n) for n in names]
            close = difflib.get_close_matches(text_norm, normalized_names, n=1, cutoff=0.72)
            if close:
                wanted_norm = close[0]
                for row in rows:
                    if normalize(row.get("product", "")) == wanted_norm:
                        return row
        return None

    def find_product_with_history(user_prompt: str, rows: list, hist: list):
        hit = find_product_from_text(user_prompt, rows)
        if hit:
            return hit

        for msg in reversed(hist or []):
            content = msg.get("content", "") if isinstance(msg, dict) else ""
            hit = find_product_from_text(content, rows)
            if hit:
                return hit
        return None

    try:
        data = load_forecast_data()
        if not data:
            return {"error": "Forecast data not found. Run forecast_product.py first."}

        history_safe = history if isinstance(history, list) else []
        product = find_product_with_history(prompt, data, history_safe)
        asked_month = extract_month(prompt)

        if product:
            prod_name = product.get("product", "Unknown Product")
            growth = float(product.get("growth_percent", 0))
            peak = product.get("peak_month", "Unknown")
            sales_2026 = int(product.get("sales_2026_lkr", 0))
            sales_2025 = int(product.get("sales_2025_lkr", 0))
            m2026 = product.get("monthly_2026_lkr", {}) or {}
            m2025 = product.get("monthly_2025_lkr", {}) or {}

            month_line = ""
            if asked_month:
                v26 = int(m2026.get(asked_month, 0) or 0)
                v25 = int(m2025.get(asked_month, 0) or 0)
                yoy = ((v26 - v25) / v25 * 100) if v25 else 0
                month_line = f"\nFocused Month: {asked_month} | 2026: {v26:,} LKR | 2025: {v25:,} LKR | YoY: {yoy:+.1f}%"

            context_block = f"""
Dataset scope: supermarket product forecasts from Prophet (2025 baseline + 2026 forecast).
Matched Product: {prod_name}
2025 Total: {sales_2025:,} LKR
2026 Forecast Total: {sales_2026:,} LKR
Growth: {growth:+.1f}%
Peak Month: {peak}{month_line}
"""

            user_history = "\n".join(
                [f"{m.get('role', 'user')}: {m.get('content', '')}" for m in history_safe[-8:] if isinstance(m, dict)]
            )

            gemini_prompt = f"""
You are a conversational retail analytics copilot.
Use only the supplied forecast context. Be clear, practical, and natural.
If user asks follow-up (like 'what about March?'), continue using the same product context unless user changed product.

{context_block}

Recent conversation:
{user_history}

User: {prompt}

Instructions:
- Respond in 3-6 short lines
- Include numbers in LKR where relevant
- If trend is positive, mention growth opportunity; if negative, mention mitigation
- If the question is ambiguous, answer with best assumption and ask one short clarifying question at the end
"""

            try:
                response = model.generate_content(gemini_prompt)
                insight = (response.text or "").strip()
            except Exception:
                if asked_month:
                    v26 = int(m2026.get(asked_month, 0) or 0)
                    insight = (
                        f"For {prod_name}, {asked_month} 2026 is forecast at {v26:,} LKR. "
                        f"Full-year 2026 is {sales_2026:,} LKR ({growth:+.1f}% vs 2025), with peak demand in {peak}."
                    )
                else:
                    insight = (
                        f"{prod_name} is forecast at {sales_2026:,} LKR in 2026 ({growth:+.1f}% vs 2025). "
                        f"Peak month is {peak}; run targeted promotions 2-3 weeks before peak demand."
                    )

            return {
                "product": prod_name,
                "your_question": prompt,
                "answer": insight,
                "2026_sales_lkr": sales_2026,
                "growth_percent": growth,
                "peak_month": peak,
                "peak_reason": "seasonal demand pattern",
                "monthly_2026": m2026,
                "month_context": asked_month,
            }

        ranked = sorted(data, key=lambda x: float(x.get("growth_percent", 0)), reverse=True)
        top = ranked[:3]
        low = ranked[-3:] if len(ranked) >= 3 else ranked
        total_2026 = sum(int(x.get("sales_2026_lkr", 0) or 0) for x in data)
        total_2025 = sum(int(x.get("sales_2025_lkr", 0) or 0) for x in data)
        total_growth = ((total_2026 - total_2025) / total_2025 * 100) if total_2025 else 0

        top_txt = ", ".join([f"{x.get('product', '?')} ({float(x.get('growth_percent', 0)):+.1f}%)" for x in top])
        low_txt = ", ".join([f"{x.get('product', '?')} ({float(x.get('growth_percent', 0)):+.1f}%)" for x in low])
        portfolio_context = f"""
Portfolio 2026 total: {total_2026:,} LKR
Portfolio growth vs 2025: {total_growth:+.1f}%
Top growers: {top_txt}
Lowest growers: {low_txt}
"""

        user_history = "\n".join(
            [f"{m.get('role', 'user')}: {m.get('content', '')}" for m in history_safe[-8:] if isinstance(m, dict)]
        )

        prompt_no_product = f"""
You are a conversational retail analytics copilot.
No exact product was detected in the latest user message.
Answer using portfolio-level forecast context, then ask a short follow-up to identify product if needed.

{portfolio_context}

Recent conversation:
{user_history}

User: {prompt}

Instructions:
- 3-6 short lines
- Include numeric anchors in LKR or %
- End with one clarifying question that asks which product they want
"""

        try:
            response = model.generate_content(prompt_no_product)
            portfolio_answer = (response.text or "").strip()
        except Exception:
            portfolio_answer = (
                f"Across all forecasted products, 2026 is projected at {total_2026:,} LKR ({total_growth:+.1f}% vs 2025). "
                f"Top growth items are {top_txt}. Which exact product should I break down next?"
            )

        return {
            "product": "Portfolio Overview",
            "your_question": prompt,
            "answer": portfolio_answer,
            "2026_sales_lkr": total_2026,
            "growth_percent": round(total_growth, 2),
            "peak_month": "",
            "peak_reason": "",
            "monthly_2026": {},
            "did_you_mean": [p.get("product") for p in top],
        }

    except Exception as e:
        return {"error": f"Tool error: {str(e)}"}

@mcp.tool()
def product_list() -> list:
    """
    Returns list of all products in forecast data.
    Used in frontend dropdown.
    """
    return [p["product"] for p in _load_forecast_rows() if p.get("product")]


@mcp.tool()
def get_next_buy_forecast(product_name: str) -> dict:
    """
    Returns a 4-week next-buy plan for the selected product.
    If manual overrides exist, they take precedence over generated defaults.
    """
    generated = _generate_next_buy_forecast(product_name)
    if generated.get("error"):
        return generated

    overrides = _load_next_buy_overrides()
    normalized = _normalize_product_name(generated["product"])
    override = overrides.get(normalized)

    if not override:
        return generated

    weekly_by_label = {
        str(item.get("week")): item
        for item in generated.get("weeklyForecast", [])
        if isinstance(item, dict)
    }

    for item in override.get("weeklyForecast", []):
        if not isinstance(item, dict) or not item.get("week"):
            continue
        weekly_by_label[str(item["week"])] = {
            "week": str(item["week"]),
            "suggestedBuy": int(item.get("suggestedBuy", weekly_by_label.get(str(item["week"]), {}).get("suggestedBuy", 0))),
            "reason": str(item.get("reason", weekly_by_label.get(str(item["week"]), {}).get("reason", ""))),
        }

    generated["weeklyForecast"] = [weekly_by_label[f"Week {i}"] for i in range(1, 5) if f"Week {i}" in weekly_by_label]
    if override.get("insight"):
        generated["insight"] = str(override["insight"])
    generated["overrideApplied"] = True
    return generated


@mcp.tool()
def pairwise_product_list() -> list:
    """
    Returns products available in the pairwise/apriori transaction dataset.
    """
    _, counts, _ = _load_pairwise_transactions()
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [name for name, _ in ranked]


@mcp.tool()
def get_pairwise_associations(product_name: str, limit: int = 5) -> dict:
    """
    Return the top co-purchased products for a selected product using pairwise
    association metrics derived from the apriori transaction dataset.
    """
    baskets, counts, total_bills = _load_pairwise_transactions()
    if not baskets or total_bills == 0:
        return {"product": product_name, "pairs": [], "totalBills": 0}

    normalized_lookup = {
        _normalize_product_name(name): name
        for name in counts.keys()
    }
    wanted = _normalize_product_name(product_name)
    canonical = normalized_lookup.get(wanted)

    if not canonical:
        for normalized_name, original in normalized_lookup.items():
            if wanted in normalized_name or normalized_name in wanted:
                canonical = original
                break

    if not canonical:
        return {
            "error": f"Product '{product_name}' not found in pairwise dataset.",
            "product": product_name,
            "pairs": [],
            "totalBills": total_bills,
        }

    product_bills = counts.get(canonical, 0)
    if product_bills == 0:
        return {"product": canonical, "pairs": [], "totalBills": total_bills}

    if product_bills >= 3000:
        min_pair_count = 8
    elif product_bills >= 1000:
        min_pair_count = 5
    else:
        min_pair_count = 2
    min_support_pct = 0.05

    pair_counts = {}
    for basket in baskets:
        if canonical not in basket:
            continue
        for item in basket:
            if item == canonical:
                continue
            pair_counts[item] = pair_counts.get(item, 0) + 1

    ranked_pairs = []
    for partner, pair_count in pair_counts.items():
        partner_bills = counts.get(partner, 0)
        support = pair_count / total_bills if total_bills else 0.0
        confidence = pair_count / product_bills if product_bills else 0.0
        partner_support = partner_bills / total_bills if total_bills else 0.0
        lift = (support / ((product_bills / total_bills) * partner_support)) if partner_support and total_bills else 0.0
        support_pct = support * 100

        # Raw lift over-ranks very rare pairs. Filter weak rules first.
        if pair_count < min_pair_count or support_pct < min_support_pct:
            continue

        duo_plan = _generate_pairwise_plan_with_gemini(
            canonical,
            partner,
            int(pair_count),
            confidence * 100,
            lift,
        )

        ranked_pairs.append({
            "partner": partner,
            "support": round(support_pct, 2),
            "confidence": round(confidence * 100, 2),
            "lift": round(lift, 2),
            "pairCount": int(pair_count),
            "reason": (
                f"Appears together in {pair_count:,} baskets. "
                f"{confidence * 100:.1f}% of baskets containing {canonical} also include {partner}."
            ),
            "strategies": duo_plan["strategies"],
            "expectedSalesIncrease": duo_plan["expectedSalesIncrease"],
            "projectedRevenueLiftLkr": duo_plan["projectedRevenueLiftLkr"],
        })

    ranked_pairs.sort(key=lambda item: (-item["lift"], -item["pairCount"], -item["confidence"], -item["support"], item["partner"]))
    return {
        "product": canonical,
        "pairs": ranked_pairs[: max(1, int(limit))],
        "totalBills": total_bills,
        "source": "transaction_apriori.csv",
        "filters": {
            "minPairCount": min_pair_count,
            "minSupportPct": min_support_pct,
        },
    }


@mcp.tool()
def save_next_buy_forecast_input(product_name: str, week: str, suggested_buy: int, reason: str, insight: str = "") -> dict:
    """
    Save or update manual next-buy input for one week of a product.
    Persists the override in data/next_buy_overrides.json.
    """
    generated = _generate_next_buy_forecast(product_name)
    if generated.get("error"):
        return generated

    week_label = week.strip()
    if week_label not in {"Week 1", "Week 2", "Week 3", "Week 4"}:
        return {"error": "week must be one of: Week 1, Week 2, Week 3, Week 4"}

    overrides = _load_next_buy_overrides()
    normalized = _normalize_product_name(generated["product"])
    product_override = overrides.get(normalized, {
        "product": generated["product"],
        "weeklyForecast": generated["weeklyForecast"],
    })

    weekly_rows = []
    found = False
    for item in product_override.get("weeklyForecast", []):
        if not isinstance(item, dict) or not item.get("week"):
            continue
        if item["week"] == week_label:
            weekly_rows.append({
                "week": week_label,
                "suggestedBuy": int(suggested_buy),
                "reason": reason.strip(),
            })
            found = True
        else:
            weekly_rows.append({
                "week": str(item["week"]),
                "suggestedBuy": int(item.get("suggestedBuy", 0)),
                "reason": str(item.get("reason", "")),
            })

    if not found:
        weekly_rows.append({
            "week": week_label,
            "suggestedBuy": int(suggested_buy),
            "reason": reason.strip(),
        })

    weekly_rows.sort(key=lambda item: item["week"])
    overrides[normalized] = {
        "product": generated["product"],
        "insight": insight.strip() or product_override.get("insight") or generated["insight"],
        "weeklyForecast": weekly_rows,
        "updated_at": date.today().isoformat(),
    }
    _save_next_buy_overrides(overrides)

    return {
        "ok": True,
        "product": generated["product"],
        "savedWeek": week_label,
        "savedSuggestedBuy": int(suggested_buy),
        "savedReason": reason.strip(),
        "overrideFile": "data/next_buy_overrides.json",
    }


@mcp.tool()
def get_monthly_forecast(product_name: str) -> dict:
    """
    Returns 2026 monthly forecast for a product.
    Format: { "Jan": 125000, "Feb": 132000, ... }
    Used in charts: month = period, value = sales (LKR)
    """
    path = "forecasts/all_2026.json"
    if not os.path.exists(path):
        print("get_monthly_forecast: File not found")
        return {}

    try:
        with open(path) as f:
            data = json.load(f)
    except Exception as e:
        print(f"get_monthly_forecast: JSON error: {e}")
        return {}

    product_name_lower = product_name.strip().lower()

    for p in data:
        if product_name_lower in p.get("product", "").lower():
            monthly_raw = p.get("monthly_2026_lkr", {})
            # Ensure month names are short: "January" → "Jan"
            month_map = {
                "January": "Jan", "February": "Feb", "March": "Mar", "April": "Apr",
                "May": "May", "June": "Jun", "July": "Jul", "August": "Aug",
                "September": "Sep", "October": "Oct", "November": "Nov", "December": "Dec"
            }
            monthly = {}
            for full, amount in monthly_raw.items():
                short = month_map.get(full, full[:3])
                monthly[short] = int(amount) if amount else 0

            print(f"get_monthly_forecast: {p['product']} → {monthly}")
            return monthly

    print(f"get_monthly_forecast: '{product_name}' not found")
    return {}


@mcp.tool()
def get_monthly_forecast_2025_2026(product_name: str) -> dict:
    """
    Returns 2025 & 2026 monthly forecast for a product.
    Format: { "2025": { "Jan": 450000, ... }, "2026": { "Jan": 529982, ... } }
    Used in dual-year comparison chart.
    """
    path = "forecasts/all_2026.json"
    if not os.path.exists(path):
        print("get_monthly_forecast: File not found")
        return {}

    try:
        with open(path) as f:
            data = json.load(f)
    except Exception as e:
        print(f"get_monthly_forecast: JSON error: {e}")
        return {}

    product_name_lower = product_name.strip().lower()

    for p in data:
        if product_name_lower in p.get("product", "").lower():
            # Get both years
            monthly_2025_raw = p.get("monthly_2025_lkr", {})
            monthly_2026_raw = p.get("monthly_2026_lkr", {})

            month_map = {
                "January": "Jan", "February": "Feb", "March": "Mar", "April": "Apr",
                "May": "May", "June": "Jun", "July": "Jul", "August": "Aug",
                "September": "Sep", "October": "Oct", "November": "Nov", "December": "Dec"
            }

            def format_monthly(raw_dict):
                return {
                    month_map.get(full, full[:3]): int(amount) if amount else 0
                    for full, amount in raw_dict.items()
                }

            result = {
                "2025": format_monthly(monthly_2025_raw),
                "2026": format_monthly(monthly_2026_raw)
            }

            print(
                f"get_monthly_forecast: {p['product']} → {len(result['2025'])} months per year")
            return result

    print(f"get_monthly_forecast: '{product_name}' not found")
    return {}


def clean_suggestion_seasonality(text: str) -> str:
    if not text:
        return ""
    original = text
    text = text.strip().replace("**", "")
    text = text.replace("1-line strategy", "")
    if text.startswith("* "):
        text = text[2:]
    elif text.startswith("*"):
        text = text[1:]
    cleaned = text.strip()
    if original != cleaned:
        print(f"   Cleaned: '{original}' → '{cleaned}'")
    return cleaned

# ...existing code...

# ...existing code...


@mcp.tool()
def get_bundle_srilanka() -> list:
    import json
    from datetime import datetime

    try:
        with open("smart_pairs_for_app.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        # Frontend expects an array. Always return a list (even when empty).
        return []

    bundles = data.get("smart_bundles_for_top10", [])
    if not bundles:
        return []

    top_products = {p.get("product"): p.get("revenue_lkr", 0)
                    for p in data.get("top_10_products_by_revenue", [])}
    result = []

    for item in bundles:
        primary = item.get("top_product", "")
        partner = item.get("bundle_with", "")
        if not partner or partner == "No strong partner found" or item.get("lift", 0) == 0:
            continue

        chance = round(item.get("confidence", 0), 1)
        lift = round(item.get("lift", 0), 1)
        revenue = top_products.get(primary, 0)

        prompt = f"""
PAIR: {primary} + {partner} | Lift {lift:.1f}x | Revenue LKR {top_products.get(primary, 0):,}

Give exactly 3 short, powerful, different ideas to sell BOTH together.

Rules:
- Mix everyday + occasional culture (no holiday spam)
- Be specific: price, place, message
- At least one visual in-store idea

Return ONLY this JSON:

{{
  "primary": "{primary}",
  "bundle": "{partner}",
  "chance": {chance},
  "lift": {lift},
  "suggestions": [
    "Save LKR 120 when bought together – 'Complete Meal Combo!'",
    "Place side-by-side with big yellow 'Buy Both & Save' sign",
    "Weekend WhatsApp blast: 'Family Deal – Only LKR 1,380!'"
  ],
  "expectedSalesIncrease": {round(lift * 7, 1)}
}}
"""

        try:
            response = model.generate_content(prompt)
            raw = response.text.strip()

            # Clean common Gemini wrappers
            raw = raw.replace("```json", "").replace("```", "").strip()

            try:
                parsed = json.loads(raw)
                # ensure parsed is a dict representing one bundle
                if isinstance(parsed, dict):
                    result.append(parsed)
                    print(
                        f"Gemini SUCCESS → {primary} + {partner} → +{parsed.get('expectedSalesIncrease', '?')}%")
                else:
                    # if model returned a list or other, coerce to single-item dict
                    raise ValueError("Gemini returned list instead of dict")

            except Exception:
                # Fallback when parsing fails
                print(f"GEMINI FAILED for {primary} + {partner} | Error: {e}")
                print(f"   → Using SMART FALLBACK instead")
                result.append({
                    "primary": primary,
                    "bundle": partner,
                    "chance": chance,
                    "lift": lift,
                    "suggestions": [
                        f"Bundle {primary} + {partner} at 12% off",
                        f"Place next to each other with 'Most Bought Together' sign",
                        f"Promote via WhatsApp this weekend"
                    ],
                    "expectedSalesIncrease": round(10 + lift * 4, 1)
                })
        except Exception:
            # Final fallback
            print(f"   → Using SMART FALLBACK instead")
            result.append({
                "primary": primary,
                "bundle": partner,
                "chance": chance,
                "lift": lift,
                "suggestions": ["Bundle discount", "Shelf talker", "WhatsApp promo"],
                "expectedSalesIncrease": 28.0
            })

    print(f"SUCCESS: Sent {len(result)} clean bundles to frontend!")
    # IMPORTANT: return a list (JSON array) — frontend validation expects an array
    return result
# ...existing code...


@mcp.tool()
def get_sales_booster_suggestions(product_name: str) -> list:
    """
    Returns 3 AI-powered, high-impact suggestions to:
    - Maximize sales
    - Minimize waste & risk
    - Optimize resources
    Uses Gemini as the world's best sales + risk + efficiency expert.
    """
    path = "forecasts/all_2026.json"
    if not os.path.exists(path):
        print("get_sales_booster_suggestions: File not found")
        return []

    try:
        with open(path) as f:
            data = json.load(f)
    except Exception as e:
        print(f"get_sales_booster_suggestions: JSON error: {e}")
        return []

    product_name_lower = product_name.strip().lower()
    product = None
    for p in data:
        if product_name_lower in p.get("product", "").lower():
            product = p
            break

    if not product:
        print(f"get_sales_booster_suggestions: '{product_name}' not found")
        return []

    # === EXTRACT KEY METRICS ===
    sales_2025 = product.get("sales_2025_lkr", 0)
    sales_2026 = product.get("sales_2026_lkr", 0)
    growth = round(product.get("growth_percent", 0), 1)
    peak_month = product.get("peak_month", "Unknown")
    monthly = product.get("monthly_2026_lkr", {})

    # Find peak weeks (simulate from monthly)
    month_to_week = {
        "January": "1-4", "February": "5-8", "March": "9-12", "April": "13-16",
        "May": "17-20", "June": "21-24", "July": "25-28", "August": "29-32",
        "September": "33-36", "October": "37-40", "November": "41-44", "December": "45-48"
    }
    peak_weeks = month_to_week.get(peak_month, "Unknown")

    # Low months (bottom 3)
    sorted_months = sorted(monthly.items(), key=lambda x: x[1])[:3]
    low_months = ", ".join([m[0][:3] for m in sorted_months]
                           ) if sorted_months else "early months"

    # === GEMINI PROMPT: WORLD’S BEST EXPERT ===
    gemini_prompt = f"""
You are the **world's greatest supermarket sales strategist, risk manager, and resource optimizer** — trusted by Keells, Cargills, and Arpico.

PRODUCT: {product.get('product', 'Unknown')}
2025 Total Sales: {sales_2025:,} LKR
2026 Forecast: {sales_2026:,} LKR ({growth:+.1f}% growth)
Peak Month: {peak_month}

Analyze the data and give **exactly 3 high-impact, actionable suggestions** to:
- Maximize sales
- Minimize waste & stock risk
- Save resources (labor, shelf, promo budget)

Each suggestion must include:
- 1-line strategy
- 1-line explanation
- Expected Impact: [+X% sales | -X% waste | +LKR X,XXX]

Then, **calculate the total combined effect**:
TOTAL_IMPACT: [+XX% total sales increase | +LKR XX,XXX additional monthly revenue]

Rules:
- Be **realistic and data-driven**
- Use **Sri Lankan context** (Poya, festivals, culture)
- **Never make up numbers** — base on growth, peak, and 2025 sales
- **TOTAL_IMPACT must be accurate sum**

Example Output:
1. Optimize Inventory for Peak Month
Increase stock by 25% in {peak_month} to capture demand surge.
Expected Impact: +18% sales increase | +LKR 4,200

2. Run Flash Sales in Low Months
Offer 15% off in Feb/Mar to prevent overstock.
Expected Impact: +10% sales | -35% waste | +LKR 2,100

3. Bundle with Complementary Products
Pair with sugar for baking combo during festive season.
Expected Impact: +17% AOV | +LKR 2,200

TOTAL_IMPACT: [+45% total sales increase | +LKR 8,500 additional monthly revenue]
"""

    try:
        print(f"Calling Gemini for {product_name}...")
        response = model.generate_content(gemini_prompt)
        raw = response.text.strip()

        suggestions = []
        current = None
        for line in raw.split('\n'):
            line = line.strip()
            if line.startswith(('1.', '2.', '3.')):
                if current:
                    suggestions.append(current)
                current = {"title": "", "desc": "", "impact": ""}
                current["title"] = line[3:].strip()
            elif line.startswith("Expected Impact:"):
                current["impact"] = line.replace(
                    "Expected Impact:", "").strip()
            elif current and not current["desc"] and line:
                current["desc"] = line
            elif line.startswith("TOTAL_IMPACT:"):
                total_impact = line.replace("TOTAL_IMPACT:", "").strip()

                suggestions = [clean_suggestion_seasonality(
                    s) for s in suggestions if s]

        if current:
            suggestions.append(current)

        # Fallback if parsing fails
        if len(suggestions) < 3:
            fallback = [
                {
                    "title": "Optimize Inventory for Peak Demand",
                    "desc": f"Stock up 25% extra in {peak_month} to avoid lost sales.",
                    "impact": "+20% sales in peak month"
                },
                {
                    "title": "Run Flash Sales in Low Months",
                    "desc": f"Clear slow-moving stock in {low_months} with 20% off.",
                    "impact": "-30% waste, +10% sales"
                },
                {
                    "title": "Bundle with Top Sellers",
                    "desc": "Pair with high-demand items to boost visibility and value.",
                    "impact": "+15% average order value"
                }
            ]
            suggestions = fallback[:3]

        print(
            f"get_sales_booster_suggestions: {len(suggestions)} suggestions ready")
        return suggestions

    except Exception as e:
        print(f"Gemini failed: {e}")
        return [
            {
                "title": "Run Weekend Flash Sale",
                "desc": "Clear excess stock and boost traffic.",
                "impact": "+12% sales, -25% waste"
            },
            {
                "title": "Improve Shelf Placement",
                "desc": "Move to eye-level near checkout.",
                "impact": "+10% impulse buys"
            },
            {
                "title": "Bundle with Top Seller",
                "desc": "Increase perceived value and clear inventory.",
                "impact": "+15% sales per bundle"
            }
        ]


@mcp.tool()
def get_top_products() -> list:
    """
    Returns top 5 products by 2026 growth %.
    Used in frontend dashboard.
    """
    path = "forecasts/all_2026.json"
    if not os.path.exists(path):
        return []

    with open(path) as f:
        data = json.load(f)

    # Sort by growth_percent DESC
    sorted_data = sorted(data, key=lambda x: x["growth_percent"], reverse=True)
    top_5 = sorted_data[:5]

    # Format for frontend
    return [
        {
            "name": p["product"],
            "currentSales": p["sales_2025_lkr"],
            "predictedSales": p["sales_2026_lkr"],
            "growth": round(p["growth_percent"], 1)
        }
        for p in top_5
    ]


def clean_suggestion(text: str) -> str:
    if not text:
        return ""
    original = text
    text = text.strip().replace("**", "")
    if text.startswith("* "):
        text = text[2:]
    elif text.startswith("*"):
        text = text[1:]
    cleaned = text.strip()
    if original != cleaned:
        print(f"   Cleaned: '{original}' → '{cleaned}'")
    return cleaned


@mcp.tool()
def get_lower_products() -> list:
    """
    Returns bottom 5 declining products in 2026 with 3 AI-powered sales recovery suggestions.
    Used in frontend dashboard.
    """
    path = "forecasts/all_2026.json"
    if not os.path.exists(path):
        return []

    try:
        with open(path) as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading forecast file: {e}")
        return []

    # Sort by growth ASC → lowest first
    sorted_data = sorted(data, key=lambda x: x.get("growth_percent", 0))
    bottom_5 = sorted_data[:5]

    results = []

    for p in bottom_5:
        name = p.get("product", "Unknown")
        current = p.get("sales_2025_lkr", 0)
        predicted = p.get("sales_2026_lkr", 0)
        decline = round(p.get("growth_percent", 0), 1)

        gemini_prompt = f"""
You are the **world's best supermarket sales development executive in Sri Lanka** — trusted by Keells, Cargills, and Arpico.

Product: {name}
2025 Sales: {current:,} LKR
2026 Forecast: {predicted:,} LKR
Decline: {decline:+.1f}%

Give **exactly 3 short, bold, actionable suggestions** to **reverse the decline and increase sales**.
Focus on: bundling, promotions, packaging, placement, or cultural tie-ins.
Do **not** explain. Just 3 bullet points.

Example:
* Bundle with screen protectors for better value
* Launch back-to-school combo in August
* Offer limited-edition festive packaging
"""

        try:
            response = model.generate_content(gemini_prompt)
            raw_suggestions = response.text.strip()

            suggestions = []
            for line in raw_suggestions.split('\n'):
                line = line.strip()
                if line.startswith('*') or line.startswith('-'):
                    suggestions.append(line[1:].strip())
                elif line and not line.startswith(('1.', '2.', '3.', '4.', '5.')):
                    suggestions.append(line)
                if len(suggestions) >= 3:
                    break

            suggestions = [clean_suggestion(s) for s in suggestions if s]
            suggestions = suggestions[:3] or [
                "Run weekend flash sale",
                "Bundle with popular items",
                "Improve shelf placement"
            ]
        except Exception as e:
            print(f"Gemini failed for {name}: {e}")
            suggestions = [
                "Run weekend flash sale",
                "Bundle with popular items",
                "Improve shelf placement"
            ]

        results.append({
            "name": name,
            "currentSales": current,
            "predictedSales": predicted,
            "decline": decline,
            "suggestions": suggestions
        })

    return results


@mcp.tool()
async def gemini_fallback_chat(
    user_message: str,
    history: list = None,
    token: str = ""
) -> str:
    """Return full Gemini response as a single string."""
    gemini_hist = []
    if history:
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            gemini_hist.append({"role": role, "parts": msg["parts"]})

    chat = model.start_chat(history=gemini_hist)
    response = await chat.send_message_async(user_message, stream=True)
    full_text = ""
    async for chunk in response:
        full_text += chunk.text

    return full_text


# === RUN SERVER (NO app=app) ===
if __name__ == "__main__":
    print("\nMCP SERVER STARTED")
    print("   OPEN: http://localhost:8000/docs")
    print("   TOOL: POST http://127.0.0.1:8000/mcp/tools/get_ice_cream_forecast\n")
    mcp.run(transport="sse", port=8000, host="0.0.0.0")

