import json
import os
from datetime import datetime

import requests

NTFY_TOPIC = os.environ['NTFY_TOPIC']
LAT = float(os.environ.get('LAT') or '32.7157')
LON = float(os.environ.get('LON') or '-117.1611')
PLACE = os.environ.get('PLACE') or 'San Diego'
TIMEZONE = os.environ.get('TIMEZONE') or 'America/Los_Angeles'
THRESHOLD = int(os.environ.get('RAIN_THRESHOLD') or '50')

SEEN_FILE = 'seen.json'


def load_state():
    try:
        with open(SEEN_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {'alerted_dates': []}


def save_state(state):
    with open(SEEN_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def fetch_tomorrow():
    url = 'https://api.open-meteo.com/v1/forecast'
    params = {
        'latitude': LAT,
        'longitude': LON,
        'daily': 'precipitation_probability_max,precipitation_sum',
        'precipitation_unit': 'inch',
        'timezone': TIMEZONE,
        'forecast_days': 2,
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    daily = resp.json()['daily']
    return {
        'date': daily['time'][1],
        'probability': daily['precipitation_probability_max'][1],
        'amount': daily['precipitation_sum'][1],
    }


def notify(forecast):
    day = datetime.strptime(forecast['date'], '%Y-%m-%d').strftime('%A')
    amount = forecast['amount'] or 0
    message = f"{day}: {forecast['probability']}% chance, {amount:.2f} in expected."
    requests.post(
        f'https://ntfy.sh/{NTFY_TOPIC}',
        data=message.encode(),
        headers={
            'Title': f'Rain tomorrow in {PLACE}',
            'Priority': 'default',
            'Click': f'https://forecast.weather.gov/MapClick.php?lat={LAT}&lon={LON}',
        },
    )


def main():
    state = load_state()
    forecast = fetch_tomorrow()
    prob = forecast['probability']

    if prob is None:
        print(f"No probability data for {forecast['date']}")
        return

    print(f"{forecast['date']}: {prob}% chance, {forecast['amount']} in expected")

    already_alerted = forecast['date'] in state.get('alerted_dates', [])
    if prob >= THRESHOLD and not already_alerted:
        notify(forecast)
        state['alerted_dates'] = state.get('alerted_dates', [])[-29:] + [forecast['date']]
        save_state(state)
        print(f"Alerted: {prob}% >= {THRESHOLD}%")
    else:
        print(f"No alert (threshold {THRESHOLD}%, already alerted: {already_alerted})")


if __name__ == '__main__':
    main()
