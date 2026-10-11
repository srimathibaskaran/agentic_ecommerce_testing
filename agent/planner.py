import json
import os
import re
import requests

ALLOWED_ACTIONS = {
    "open_home", "open_login", "login_valid", "open_products",
    "search_product", "add_first_result_to_cart", "open_cart",
    "proceed_to_checkout", "verify_text"
}

FALLBACK_PLAN = [
    {"action": "open_login"},
    {"action": "login_valid"},
    {"action": "open_products"},
    {"action": "search_product", "value": "Wireless Mouse"},
    {"action": "add_first_result_to_cart"},
    {"action": "open_cart"},
    {"action": "proceed_to_checkout"},
    {"action": "verify_text", "value": "Checkout"},
]

SYSTEM_PROMPT = """You are a browser testing planner for a LOCAL demo e-commerce website.
Return only a JSON array of action objects. Allowed action values:
open_home, open_login, login_valid, open_products, search_product,
add_first_result_to_cart, open_cart, proceed_to_checkout, verify_text.
Use value only for search_product or verify_text. Never invent other actions.
Do not make real purchases or enter payment data. The checkout is a local simulation.
For the goal, produce a short sequence that reaches checkout after adding a product.
Example: [{"action":"open_login"},{"action":"login_valid"},{"action":"open_products"},
{"action":"search_product","value":"Wireless Mouse"},{"action":"add_first_result_to_cart"},
{"action":"open_cart"},{"action":"proceed_to_checkout"},{"action":"verify_text","value":"Checkout"}]
"""

def _extract_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    start, end = text.find("["), text.rfind("]")
    if start < 0 or end <= start:
        raise ValueError("No JSON array in planner response")
    return json.loads(text[start:end + 1])

def validate_plan(plan):
    if not isinstance(plan, list) or not plan:
        raise ValueError("Plan must be a non-empty list")
    clean = []
    for step in plan[:15]:
        if not isinstance(step, dict) or step.get("action") not in ALLOWED_ACTIONS:
            raise ValueError("Planner proposed an unsupported action")
        item = {"action": step["action"]}
        if item["action"] in {"search_product", "verify_text"}:
            value = step.get("value", "")
            if not isinstance(value, str) or not value.strip() or len(value) > 100:
                raise ValueError("Invalid action value")
            item["value"] = value.strip()
        clean.append(item)
    return clean

def create_plan(goal):
    use_ollama = os.getenv("USE_OLLAMA", "1").lower() not in {"0", "false", "no"}
    if use_ollama:
        model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
        endpoint = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
        try:
            response = requests.post(
                endpoint,
                json={"model": model, "prompt": SYSTEM_PROMPT + "\nGoal: " + goal,
                      "stream": False, "format": "json"},
                timeout=90,
            )
            response.raise_for_status()
            raw = response.json().get("response", "")
            plan = validate_plan(_extract_json(raw))
            return plan, f"Ollama model: {model}"
        except Exception as exc:
            return validate_plan(FALLBACK_PLAN), f"Fallback planner used ({type(exc).__name__}: {exc})"
    return validate_plan(FALLBACK_PLAN), "Deterministic fallback planner (USE_OLLAMA=0)"
