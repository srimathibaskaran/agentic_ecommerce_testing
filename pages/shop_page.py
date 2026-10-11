from playwright.sync_api import expect

class ShopPage:
    def __init__(self, page, base_url):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def open_home(self):
        self.page.goto(self.base_url)
        expect(self.page.get_by_role("heading", name="Welcome to the Demo Shop")).to_be_visible()

    def open_login(self):
        self.page.goto(f"{self.base_url}/login")
        expect(self.page.get_by_role("heading", name="Login")).to_be_visible()

    def login_valid(self):
        self.page.locator("#username").fill("demo")
        self.page.locator("#password").fill("demo123")
        self.page.get_by_role("button", name="Sign in").click()
        expect(self.page.get_by_role("heading", name="Products")).to_be_visible()

    def login_invalid(self):
        self.open_login()
        self.page.locator("#username").fill("wrong")
        self.page.locator("#password").fill("wrong")
        self.page.get_by_role("button", name="Sign in").click()
        expect(self.page.get_by_role("alert")).to_contain_text("Invalid username or password")

    def open_products(self):
        self.page.goto(f"{self.base_url}/products")
        expect(self.page.get_by_role("heading", name="Products")).to_be_visible()

    def search_product(self, name):
        self.page.locator("#search").fill(name)
        self.page.get_by_role("button", name="Search").click()
        expect(self.page.locator("[data-product-id]")).to_have_count(1)
        expect(self.page.locator("[data-product-id] h3")).to_contain_text(name)

    def add_first_result_to_cart(self):
        self.page.locator("[data-product-id]").first.get_by_role("button", name="Add to cart").click()
        expect(self.page.get_by_role("heading", name="Your Cart")).to_be_visible()

    def open_cart(self):
        self.page.goto(f"{self.base_url}/cart")
        expect(self.page.get_by_role("heading", name="Your Cart")).to_be_visible()

    def proceed_to_checkout(self):
        self.page.get_by_role("link", name="Proceed to checkout").click()
        expect(self.page.get_by_role("heading", name="Checkout")).to_be_visible()

    def verify_text(self, value):
        expect(self.page.locator("body")).to_contain_text(value)
