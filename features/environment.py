from selenium import webdriver
from behave import fixture, use_fixture


@fixture
def selenium_browser_chrome(context):
    context.browser = webdriver.Chrome()
    context.browser.maximize_window()
    yield context.browser
    context.browser.quit()


def before_all(context):
    use_fixture(selenium_browser_chrome, context)
