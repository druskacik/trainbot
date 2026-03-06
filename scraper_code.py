import json
from datetime import date, timedelta

import pandas as pd
import requests
from bs4 import BeautifulSoup

from tqdm.auto import tqdm

url = 'https://www.europeansleeper.eu/'

r = requests.get(url)

r.status_code

soup = BeautifulSoup(r.content, 'html.parser')

soup

constants_script = soup.find('script', id='booking-search-props')
data = json.loads(constants_script.string.strip())

data

stations = data['constants']['stations']
stations = {}
for country in data['constants']['stations']:
    for station in country['stations']:
        stations[station['id']] = station['name']
stations

routes = data['constants']['routes']

for route in routes:
    print(route['id'], route['from'])
    for station_id in route['stations']:
        print(stations[station_id])

train_numbers_prg_to_ams = '452'
train_numbers_ams_to_prg = '453'

def search_availability(date_str: str, train_number: str) -> dict:
    body = {
        "trainRouteId": "77ab1c5a-ea0b-4634-7cdd-08db0daabe3f",
        "fromLocationId":"5457076",
        "toLocationId":"8400058",
        "passengerTypes":[72],
        "trainNumber":train_number,
        "travelDate":date_str,
        "bicycleCount":0
    }
    url = 'https://europeansleeperprod-api.azurewebsites.net/api/search/availability'
    response = requests.post(url, json=body)
    return response.json()

results = []
start_date = date.today()
for i in tqdm(range(90)):
    current_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
    results.append(search_availability(current_date))

rows = []

for result in results:
    availability = result['availabilityResult']['availability']
    if availability['departureStationName'] == 'Not available':
        continue

    row = {**availability}
    for price_class in row['priceClasses']:
        row[price_class['placeTypeKey']] = None if price_class['prices'] is None else price_class['prices']['eur']

    del row['priceClasses']
    del row['sections']

    rows.append(row)

df = pd.DataFrame(rows)

df.sort_values(by='couchette-5').head()



