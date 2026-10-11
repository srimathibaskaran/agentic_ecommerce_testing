from agent.planner import create_plan
from agent.executor import AgentExecutor

def test_agentic_shopping_objective(browser_page, base_url, record_property):
    goal = "Test a safe local shopping journey: sign in with demo credentials, find Wireless Mouse, add it to the cart, and reach simulated checkout."
    plan, planner_source = create_plan(goal)
    record_property("Planner", planner_source)
    record_property("Goal", goal)
    record_property("Plan", str(plan))

    agent = AgentExecutor(browser_page, base_url)
    steps = agent.execute(plan)
    record_property("Executed steps", str(steps))

    assert steps, "Agent should execute at least one step"
    assert all(step["status"] == "PASS" for step in steps), "Every agent step should pass"
    assert "checkout" in browser_page.url.lower(), f"Expected checkout URL, got {browser_page.url}"
