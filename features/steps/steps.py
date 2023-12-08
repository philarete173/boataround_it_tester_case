from datetime import date
from urllib.parse import urlparse, parse_qs

from behave import *
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@when('Visit boataround website')
def step(context):
    context.browser.get('https://bt2stag.boataround.com/')


@then('It should have an element with class "header__logo__img" and title "Boataround"')
def step(context):
    logo_image = context.browser.find_element(By.CLASS_NAME, 'header__logo__img')
    assert logo_image.get_attribute('title') == "Boataround"


@then('A pop-up ad message was displayed')
def step(context):
    context.browser.find_element(By.ID, 'closeCookieConsent').click()

    ad_close_button = WebDriverWait(
        context.browser,
        10,
    ).until(
        EC.presence_of_element_located((
            By.XPATH,
            '//div[@class="overlay-modal modal-auto"]/i',
        )),
        'Сan\'t find the pop-up ad message.',
    )

    assert ad_close_button
    ad_close_button.click()



@given('Enter a destination (Croatia), dates (check in: 01.06.2024, check out: 08.06.2024)')
def step(context):
    context.destination = 'croatia'
    context.date_check_in = date(2024, 6, 1)
    context.date_check_out = date(2024, 6, 8)


@when('Visit search result page')
def step(context):
    context.browser.get(
        'https://bt2stag.boataround.com/search?'
        f'destinations={context.destination}'
        f'&checkIn={context.date_check_in.strftime("%Y-%m-%d")}'
        f'&checkOut={context.date_check_out.strftime("%Y-%m-%d")}'
    )


@then('The search results page should display available boats for the specified dates')
def step(context):
    search_results = WebDriverWait(
        context.browser,
        10,
    ).until(
        EC.presence_of_all_elements_located((
            By.CLASS_NAME,
            'search-result-wrapper',
        )),
        'Can\'t find any search results. The search results page may have taken a long time to load',
    )

    assert len(search_results) > 0


@when('Open second boat from list')
def step(context):
    search_results = context.browser.find_elements(By.CLASS_NAME, 'search-result-wrapper')
    url = search_results[1].find_element(By.TAG_NAME, 'a').get_attribute('href')

    context.browser.get(url)


@then('The product page should display available booking option for the specified dates')
def step(context):
    availability_carousel = WebDriverWait(
        context.browser,
        10,
    ).until(
        EC.presence_of_element_located((
            By.CLASS_NAME,
            'ava-list-wrapper',
        )),
        'Сan\'t find the element with the list of available periods for reserve.',
    )

    ActionChains(context.browser).move_to_element(availability_carousel).perform()

    selected_period = WebDriverWait(
        availability_carousel,
        10,
    ).until(
        EC.presence_of_element_located((
            By.XPATH,
            '//li[@class="ava-item active"]//p[@class="ava-date"]',
        )),
        'Can\'t find element with selected period for reserve.',
    )

    assert all(
        period_date.strftime('%d/%m/%Y') in selected_period.text
        for period_date in (context.date_check_in, context.date_check_out)
    )


@when('Choose first available option after selected dates')
def step(context):
    context.url_params_before_switch_period = parse_qs(urlparse(context.browser.current_url).query)

    print(context.url_params_before_switch_period)

    next_available_period = context.browser.find_element(
        By.XPATH,
        '//li[@class="ava-item active"]'
        '//following-sibling::li[@class="ava-item"]'
        '//div[@class="availability-label__title"]'
        '//span[not(contains(@class, "ava-reserved"))]',
    )

    ActionChains(context.browser).move_to_element(next_available_period).click(next_available_period).perform()
    WebDriverWait(context.browser, 5)


@then('The product page should have updated checkIn and checkOut params in url')
def step(context):
    context.url_params_after_switch_period = parse_qs(urlparse(context.browser.current_url).query)

    print(context.url_params_after_switch_period)

    assert all(
        context.url_params_after_switch_period[param] != context.url_params_before_switch_period[param]
        for param in ('checkIn', 'checkOut')
    )


@when('Find lowest price around selected period')
def step(context):
    choices = [
        context.browser.find_element(
            By.XPATH,
            '//li[@class="ava-item active"]//preceding-sibling::*[1]',
        ),
        context.browser.find_element(
            By.XPATH,
            '//li[@class="ava-item active"]',
        ),
        context.browser.find_element(
            By.XPATH,
            '//li[@class="ava-item active"]//following-sibling::li[@class="ava-item"]',
        ),
    ]

    choices_price_map = {}
    for choice in choices:
        choice_data = choice.text.split('\n')
        choice_data[2] = int(''.join(s for s in choice_data[2] if s.isnumeric()))
        if 'Available' in choice_data:
            choices_price_map.update({
                choice_data[2]: choice
            })

    lowest_price_choice = choices_price_map[min(choices_price_map.keys())]

    ActionChains(context.browser).move_to_element(lowest_price_choice).click(lowest_price_choice).perform()


@when('Click button "Reserve"')
def step(context):
    reserve_button = context.browser.find_element(
        By.XPATH,
        '//div[@class="reservation-box"]//div[contains(text(), "Reserve")]',
    )

    ActionChains(context.browser).scroll_to_element(reserve_button).click(reserve_button).perform()


@then('"Enter your details" page should load without errors')
def step(context):
    enter_details_element = WebDriverWait(
        context.browser,
        10,
    ).until(
        EC.presence_of_element_located((
            By.XPATH,
            '//h2[contains(text(), "Enter your details")]',
        )),
        'Can\'t find the block with the title "Enter your details".',
    )

    assert enter_details_element and "Enter your details" in enter_details_element.text
