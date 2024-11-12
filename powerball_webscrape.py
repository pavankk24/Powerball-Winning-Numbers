#%%
from bs4 import BeautifulSoup
import requests
from collections import Counter
import pandas as pd
import datetime

# %%
def add_months(original_date, months_to_add):
    new_month = original_date.month + months_to_add
    new_year = original_date.year + (new_month - 1) // 12 # If new_month exceeds 12 then rollover
    new_month = (new_month - 1) % 12 + 1 # Adjust month to stay within 1-12 range

    try:
        new_date = original_date.replace(year=new_year, month=new_month)
    except ValueError:
        last_day = calendar.monthrange(new_year, new_month)[1]
        new_date = original_date.replace(year=new_year, month=new_month, day=last_day)
    return new_date

# %%
# table = pd.DataFrame(columns=['Date']+ [f'Number{i}' for i in range(1,6)]+['Powerball Number'])
table = pd.DataFrame(columns=['date']+ ['white_balls']+['powerball'])
from_date = datetime.datetime.strptime("1997-11-01", "%Y-%m-%d")
while from_date < datetime.datetime.now():
    to_date = add_months(from_date, 3)
    url = f'https://www.powerball.com/previous-results?gc=powerball&sd={from_date}&ed={to_date}'
    from_date = to_date
    response = requests.get(url)

    # Parse the html
    soup = BeautifulSoup(response.content, 'lxml')

    # Find all date and number sections
    entries = soup.find_all('div', class_='col-12 col-lg-4')

    results = []

    for entry in entries:
        # Extract the date
        date_element = entry.find('h5', class_='card-title')

        if date_element:
            date = date_element.text.strip()

        white_ball = entry.find('div', class_='form-control col white-balls item-powerball')
        if white_ball:
            white_balls = [ball.text for ball in entry.find_all('div', class_='form-control col white-balls item-powerball')]
            powerball = entry.find('div', class_='form-control col powerball item-powerball').text.strip() if entry.find('div', \
                class_='form-control col powerball item-powerball') else None

            results.append({
                    'date': date,
                    'white_balls': white_balls,
                    'powerball': powerball
            })
    table = pd.concat([table, pd.DataFrame((results), columns=table.columns)], ignore_index=True)

# %%
table.to_csv('table.csv', index=False)