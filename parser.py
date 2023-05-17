from collections import defaultdict
import csv
from datetime import datetime
from itertools import zip_longest
import random
import time
import urllib.parse

import steam.webauth as wa

import utils


if __name__ == '__main__':
    # initial data request and authentication
    # analysis period is set in start_date_str and end_date_str
    # year of the deal is not displayed in the history of deals in steam, it is calculated based on deal_date_str
    # break in trading shouldn't be more than a year, otherwise the definition of the year will be incorrect
    while True:
        deal_date_str = input('Enter last deal date in format dd.mm.yyyy: ')
        start_date_str = input('Enter start date in format dd.mm.yyyy: ')
        end_date_str = input('Enter end date in format dd.mm.yyyy: ')
        login = input('Login: ')
        password = input('Password: ')
        twofactor_code = input('Two-factor code from SDA: ')
        try:
            user = wa.WebAuth(login)
            user.login(password=password, twofactor_code=twofactor_code)
            start_date = datetime.strptime(start_date_str, '%d.%m.%Y')
            end_date = datetime.strptime(end_date_str, '%d.%m.%Y')
            deal_date = datetime.strptime(deal_date_str, '%d.%m.%Y')
            if start_date > end_date:
                raise ValueError('Start day must be before end day!')
            break
        except wa.TwoFactorCodeRequired:
            print('Incorrect two-factor code from SDA!')
        except wa.LoginIncorrect:
            print('Incorrect login or password!')
        except ValueError as e:
            print(e)

    print('Authorization passed successfully!')

    response = user.session.get('https://steamcommunity.com/market/myhistory')
    if response.status_code != 200:
        print(f'There was a problem getting steam response. Http code: {response.status_code}')
    else:
        print('Table creation in progress...')

        response_json = response.json()
        total_count = response_json['total_count']
        item_refs = {}
        sell_listings = defaultdict(list)  # defaultdict is used for the convenience of further filling
        buy_listings = defaultdict(list)
        need_stop = False
        for i in range(0, total_count, 100):
            time.sleep(random.uniform(0.5, 2.5))
            url = f'https://steamcommunity.com/market/myhistory/render/?l=english&query=&start={i}&count={100}'
            response_json = user.session.get(url).json()
            assets = response_json['assets']
            hovers = utils.get_hovers(response_json['hovers'])
            results_html = response_json['results_html']
            for item in hovers:
                info = utils.get_item_info(results_html, item)

                # definition of the year
                try:
                    listing_date = info[next(iter(info))]['date'].replace(year=deal_date.year)
                except ValueError:
                    assert info[next(iter(info))]['date'].month == 2 and info[next(iter(info))]['date'].day == 29
                    listing_date = info[next(iter(info))]['date'].replace(month=2, day=28, year=deal_date.year)
                if (deal_date - listing_date).days < 0:
                    listing_date = listing_date.replace(year=listing_date.year - 1)
                info[next(iter(info))]['date'] = listing_date.date()
                deal_date = listing_date

                # analysis period check
                if listing_date > end_date:
                    continue
                if listing_date < start_date:
                    need_stop = True
                    break
                item_address = hovers[item]
                market_name = assets[item_address[0]][item_address[1]][item_address[2]]['market_hash_name']

                # filling item_refs with links to item
                if market_name not in item_refs:
                    item_refs[
                        market_name] = f'https://steamcommunity.com/market/listings/{item_address[0]}/{urllib.parse.quote(market_name)}'

                # filling sell_listings and buy_listings with selling and buying item info (date, price)
                if '-' in info:
                    sell_listings[market_name].append(info['-'])
                if '+' in info:
                    buy_listings[market_name].append(info['+'])
            if need_stop:
                break

        # filling and saving the final file
        with open('results.csv', 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(['Name', 'Link', 'Buy date', 'Sell date', 'Buy amount', 'Sell amount', 'Spread'])
            for item in item_refs:
                for buy, sell in zip_longest(buy_listings.get(item, {}), sell_listings.get(item, {}), fillvalue={}):
                    buy_amount = buy.get('price', '')
                    sell_amount = sell.get('price', '')
                    spread = sell_amount - buy_amount if buy_amount and sell_amount else ''
                    writer.writerow([item, item_refs[item], buy.get('date', ''), sell.get('date', ''),
                                     buy_amount, sell_amount, spread])

        print('Completed!')
