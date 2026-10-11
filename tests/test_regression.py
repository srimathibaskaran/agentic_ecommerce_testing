from playwright.sync_api import expect
from pages.shop_page import ShopPage

def test_home_page_loads(browser_page, base_url):
    shop = ShopPage(browser_page, base_url)
    shop.open_home()
    expect(browser_page.get_by_role("link", name="Browse products")).to_be_visible()

def test_invalid_login_shows_error(browser_page, base_url):
    shop = ShopPage(browser_page, base_url)
    shop.login_invalid()

def test_search_and_add_product_to_cart(browser_page, base_url):
    shop = ShopPage(browser_page, base_url)
    shop.open_products()
    shop.search_product("Wireless Mouse")
    shop.add_first_result_to_cart()
    expect(browser_page.locator("body")).to_contain_text("Wireless Mouse")

def test_checkout_is_simulated(browser_page, base_url):
    shop = ShopPage(browser_page, base_url)
    shop.open_login()
    shop.login_valid()
    shop.open_products()
    shop.search_product("USB-C Hub")
    shop.add_first_result_to_cart()
    shop.open_cart()
    shop.proceed_to_checkout()
    expect(browser_page.locator("body")).to_contain_text("No payment details are requested")
