from datetime import datetime
import decimal
import re

from bs4 import BeautifulSoup


# function for forming a dictionary with information, thanks to which the requested data can be gotten
def get_hovers(html: str) -> dict:
    hovers_dict = {}
    regex = r"CreateItemHoverFromContainer\( [\w]+, 'history_row_([\d]+)_([\d]+)_name', ([\d]+), " \
            r"'([\d]+)', '([\d]+)', [\d]+ \);"
    for match in re.findall(regex, html):
        hovers_dict[f'history_row_{match[0]}_{match[1]}'] = [str(match[2]), match[3], match[4]]
    return hovers_dict


# function to form a numeric value from a string
# possible inputs $5.35($5,35)
def get_price(price: str) -> decimal.Decimal:
    pattern = r'\D?(\d*)(\.|,)?(\d*)'
    tokens = re.search(pattern, price)
    decimal_str = tokens.group(1) + '.' + tokens.group(3)
    return decimal.Decimal(decimal_str)


# function for forming a dictionary with selling or buying info
def get_item_info(html: str, history_row: str) -> dict:
    item_info = {}
    html_response = BeautifulSoup(html, 'html.parser')
    market_listings_raw = html_response.findAll('div', {'id': history_row})
    gain_or_loss = market_listings_raw[0].findAll('div', {'class': 'market_listing_gainorloss'})[0].text.strip()
    price_str = market_listings_raw[0].select('span[class=market_listing_price]')[0].text.strip()
    date_str = market_listings_raw[0].findAll('div', {'class': 'market_listing_listed_date'})[0].text.strip() + ' 1600'
    correct_date = datetime.strptime(date_str, '%d %b %Y')
    item_info[gain_or_loss] = {'price': get_price(price_str), 'date': correct_date}
    return item_info
