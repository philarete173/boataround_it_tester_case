from datetime import timedelta, date

import requests
import pandas as pd
from bs4 import BeautifulSoup


class NoBoatsOnPageException(Exception):
    """Exception then parser can't find any boat card on page."""


def daterange(start_date, end_date):
    for day in range((end_date - start_date).days + 1):
        yield start_date + timedelta(day)


def get_boat_info_from_one_page(search_page, date_checkin, date_checkout):
    """Scrape data about boats from one search results page."""

    boats_info_from_page = []
    search_page_soup = BeautifulSoup(search_page.content, 'html.parser')
    boats_cards = search_page_soup.select('.search-results-list .search-result')
    if not boats_cards:
        raise NoBoatsOnPageException

    for boat_card in boats_cards:
        charter_name, boat_name = boat_card.select_one('.search-result-middle__heading .mr-2').text.split(' | ')

        price_string = boat_card.select_one('.price-box .price-box__price').get_text().strip()
        price = ''.join(symbol for symbol in price_string if symbol.isnumeric())

        board_data_labels = [
            element.get_text().strip()
            for block in boat_card.select('.search-result-middle__params-name')
            for element in block.find_all('li')
        ]
        board_data_values = [
            element.get_text().strip()
            for block in boat_card.select('.search-result-middle__params-value')
            for element in block.find_all('li')
        ]
        board_data_dict = dict(zip(board_data_labels, board_data_values))

        boats_info_from_page.append({
            'Charter Name': charter_name,
            'Boat Name': boat_name,
            'Boat length': board_data_dict.get('Length', ''),
            'Price in EUR': price,
            'Check - in': date_checkin.strftime('%d.%m.%Y'),
            'Check - out': date_checkout.strftime('%d.%m.%Y'),
        })

    return boats_info_from_page


def transfer_data_to_excel(boats_data):
    """Transfer scraped data to excel file."""

    df = pd.DataFrame.from_dict(boats_data)

    df['Price in EUR'] = pd.to_numeric(df['Price in EUR'])
    df['Check - in'] = pd.to_datetime(df['Check - in'], dayfirst=True)
    df['Check - out'] = pd.to_datetime(df['Check - out'], dayfirst=True)

    df.to_excel('boats_bookings.xlsx', index=False)


def get_data_about_boats():
    """Main function to receive all necessary data."""

    # start date of the data collection period
    start_date = date(2024, 5, 1)
    # end date of the data collection period
    end_date = date(2024, 9, 30)
    # main url of requests
    request_url = 'https://bt2stag.boataround.com/search'
    # limit the number of attempts for each request
    request_repeats_max = 5

    # make pairs of weekends dates for each iteration
    weekends_dates = [
        date_ for date_ in daterange(start_date, end_date)
        if date_.isoweekday() in [6, 7]
    ]
    dates_pairs = [
        weekends_dates[idx:idx+2] for idx in range(0, len(weekends_dates), 2)
    ]

    boats_info = []

    for date_checkin, date_checkout in dates_pairs:
        print(
            'Collecting data about available boats in city Split for '
            f'{date_checkin.strftime("%d.%m.%Y")} - {date_checkout.strftime("%d.%m.%Y")}...'
        )
        # List for records about available boats at weekend
        weekends_boats = []
        # This list will be updated with page numbers if results more than on one page
        available_pages = []
        base_params = {
            'destinations': 'split-1',
            'checkIn': date_checkin.strftime('%Y-%m-%d'),
            'checkOut': date_checkout.strftime('%Y-%m-%d'),
            'currency': 'EUR',
        }
        repeat = 1
        while repeat <= request_repeats_max:
            print(f'Page 1, attempt {repeat}')

            try:
                search_page = requests.get(
                    url=request_url,
                    params=base_params,
                    timeout=5*repeat,
                )
            except requests.ReadTimeout:
                repeat += 1
                continue
            else:
                if search_page.status_code == 200:
                    search_page_soup = BeautifulSoup(search_page.content, 'html.parser')
                    available_pages = [
                        element.get_text().strip()
                        for element in search_page_soup.select('.paginator__item .paginator__item__button')
                    ]
                    try:
                        weekends_boats.extend(get_boat_info_from_one_page(search_page, date_checkin, date_checkout))
                        break
                    except NoBoatsOnPageException:
                        repeat += 1
                        continue
                else:
                    repeat += 1
                    continue

        # If results more than on one page, we need to scrape other pages
        if available_pages:
            available_pages.remove('1')

            for page_number in available_pages:
                base_params.update({
                    'page': page_number,
                })
                page_repeat = 1
                while page_repeat <= request_repeats_max:
                    print(f'Page {page_number}, attempt {page_repeat}')
                    try:
                        weekends_boats.extend(
                            get_boat_info_from_one_page(
                                requests.get(
                                    url=request_url,
                                    params=base_params,
                                    timeout=5*page_repeat,
                                ),
                                date_checkin,
                                date_checkout,
                            )
                        )
                        break
                    except (NoBoatsOnPageException, requests.ReadTimeout):
                        page_repeat += 1
                        continue

        boats_info.extend(weekends_boats)
        print(
            f'Collected data about {len(weekends_boats)} available boats in city Split for '
            f'{date_checkin.strftime("%d.%m.%Y")} - {date_checkout.strftime("%d.%m.%Y")}.'
        )

    transfer_data_to_excel(boats_info)
    
    print(
        f'Total of {len(boats_info)} records about Saturday-Saturday booking from '
        f'{start_date.strftime("%d.%m.%Y")} till {end_date.strftime("%d.%m.%Y")} received.'
    )


if __name__ == '__main__':
    get_data_about_boats()
