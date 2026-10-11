from pages.shop_page import ShopPage

class AgentExecutor:
    """Executes only validated, pre-defined actions; no arbitrary code execution."""
    def __init__(self, page, base_url):
        self.page = page
        self.shop = ShopPage(page, base_url)
        self.log = []

    def execute(self, plan):
        for index, step in enumerate(plan, start=1):
            action = step["action"]
            value = step.get("value")
            try:
                if action == "open_home":
                    self.shop.open_home()
                elif action == "open_login":
                    self.shop.open_login()
                elif action == "login_valid":
                    self.shop.login_valid()
                elif action == "open_products":
                    self.shop.open_products()
                elif action == "search_product":
                    self.shop.open_products()
                    self.shop.search_product(value)
                elif action == "add_first_result_to_cart":
                    self.shop.add_first_result_to_cart()
                elif action == "open_cart":
                    self.shop.open_cart()
                elif action == "proceed_to_checkout":
                    self.shop.proceed_to_checkout()
                elif action == "verify_text":
                    self.shop.verify_text(value)
                else:
                    raise ValueError(f"Blocked unsupported action: {action}")
                self.log.append({"step": index, "action": action, "value": value, "status": "PASS"})
            except Exception as exc:
                self.log.append({"step": index, "action": action, "value": value,
                                 "status": "FAIL", "error": str(exc)})
                raise
        return self.log
