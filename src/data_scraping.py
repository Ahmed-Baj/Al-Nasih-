import requests
import pandas as pd
from time import sleep

def scrape_apartments(direction_id, output_file):
    # Initialize variables
    FIRST_PAGE = 0
    i = FIRST_PAGE
    all_listings = pd.DataFrame([])

    # Define cookies and headers for the request
    cookies = {
        '_ga': 'GA1.2.1278248909.1659285193',
        '_gid': 'GA1.2.1862803336.1660289756',
        '_gac_UA-52229618-6': '1.1660301559.CjwKCAjw9NeXBhAMEiwAbaY4lj1eKkVdYvl2n7n-CsxVyhOK4UV5OkiNQY1L-CmZ2ROHmtbk-eKAhhoCpAwQAvD_BwE',
        'AWSALBTG': 'YKGzHhGDjN/uo8GvjfJhScsisxqqxDPMIZo/6L+jEiJBriaSBlUMnDwlg+et5O2sPiXcOHdH9gTq6jE3k+CHZ4arwPg4645uCJ3skPc4x+yil+wmsJeB6FZ7b2DIrOjwa8+E4KAmDJ7hfDyRk7fG+f8M9amzXTD3BX/RwxpcftYuPMwxouo=',
        'AWSALBTGCORS': 'YKGzHhGDjN/uo8GvjfJhScsisxqqxDPMIZo/6L+jEiJBriaSBlUMnDwlg+et5O2sPiXcOHdH9gTq6jE3k+CHZ4arwPg4645uCJ3skPc4x+yil+wmsJeB6FZ7b2DIrOjwa8+E4KAmDJ7hfDyRk7fG+f8M9amzXTD3BX/RwxpcftYuPMwxouo=',
    }

    headers = {
        'authority': 'sa.aqar.fm',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,hmn;q=0.8,ar;q=0.7,nl;q=0.6',
        'app-version': '0.16.18',
        'dpr': '1.33333',
        'origin': 'https://sa.aqar.fm',
        'referer': 'https://sa.aqar.fm/',
        'req-app': 'web',
        'req-device-token': '33e28a14-0941-41b1-b2a1-68e1304e76d8',
        'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        'viewport-width': '1050',
    }

    while True:
        try:
            # Define the JSON payload for the request
            json_data = {
                'operationName': 'findListings',
                'variables': {
                    'size': 20,
                    'from': i,
                    'sort': {
                        'create_time': 'desc',
                        'has_img': 'desc',
                    },
                    'where': {
                        'category': {'eq': 6},  # 6: 'for sale', Aqar encoding
                        'city_id': {'eq': 21},  # 21: 'Riyadh', Aqar encoding
                        'direction_id': {'eq': direction_id},  # Direction ID for specific area
                    },
                },
                'query': 'query findListings($size: Int, $from: Int, $sort: SortInput, $where: WhereInput, $polygon: [LocationInput!]) {\n  Web {\n    find(size: $size, from: $from, sort: $sort, where: $where, polygon: $polygon) {\n      ...WebResults\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment WebResults on WebResults {\n  listings {\n    user_id\n    id\n    uri\n    title\n    price\n    content\n    imgs\n    refresh\n    category\n    beds\n    livings\n    wc\n    area\n    type\n    street_width\n    age\n    last_update\n    street_direction\n    ketchen\n    ac\n    furnished\n    location {\n      lat\n      lng\n      __typename\n    }\n    path\n    user {\n      review\n      img\n      name\n      phone\n      iam_verified\n      rega_id\n      __typename\n    }\n    native {\n      logo\n      title\n      image\n      description\n      external_url\n      __typename\n    }\n    rent_period\n    city\n    district\n    width\n    length\n    advertiser_type\n    create_time\n    __typename\n  }\n  total\n  __typename\n}\n',
            }

            # Send POST request to the server
            response = requests.post('https://sa.aqar.fm/graphql', cookies=cookies, headers=headers, json=json_data)
            response_json = response.json()

            # Extract listings from the response
            listings_list = response_json.get('data').get('Web').get('find').get('listings')
            listings_list = pd.DataFrame(listings_list)

            # Check for duplicate listings to stop the loop
            if i != 0 and list(all_listings.iloc[0])[1] == list(listings_list.iloc[0])[1]:
                break

            # Append new listings to the dataframe
            all_listings = all_listings.append(listings_list, ignore_index=True)
            sleep(0.5)  # Sleep to avoid overwhelming the server
            i += 20  # Increment to fetch the next set of listings
        except:
            break

    # Save the collected listings to a CSV file
    all_listings.to_csv(output_file, index=False)

# Scrape different directions and save to respective CSV files
scrape_apartments(3, "apartments_sale_east_riyadh.csv")
scrape_apartments(6, "apartments_sale_west_riyadh.csv")
scrape_apartments(1, "apartments_sale_south_riyadh.csv")
scrape_apartments(4, "apartments_sale_north_riyadh.csv")
scrape_apartments(7, "apartments_sale_middle_riyadh.csv")