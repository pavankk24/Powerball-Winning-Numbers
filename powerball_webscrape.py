#%%
from bs4 import BeautifulSoup
import requests
from collections import Counter
import pandas as pd
import datetime
import os
from datetime import timedelta
import colorama

# %%
def add_months(original_date, months_to_add):
    '''
    Added n months to the original date
    Args:
    original_date (date): Date
    months_to_add (Int): Number of months to be added

    Returns:
    new_date (date): Returns new date
    '''
    new_month = original_date.month + months_to_add
    new_year = original_date.year + (new_month - 1) // 12 # If new_month exceeds 12 then rollover and -1 for month offset as month starts with 0
    new_month = (new_month - 1) % 12 + 1 # Adjust month to stay within 1-12 range

    try:
        new_date = original_date.replace(year=new_year, month=new_month)
    except ValueError:
        last_day = calendar.monthrange(new_year, new_month)[1]
        new_date = original_date.replace(year=new_year, month=new_month, day=last_day)
    return new_date


def add_days(original_date, days_to_add):
    '''
    Adds a specified number of days to the original date.

    Args:
    original_date (date): The original date.
    days_to_add (int): The number of days to be added.

    Returns:
    new_date (date): The new date after adding the specified days.
    '''
    new_date = original_date + timedelta(days=days_to_add)
    return new_date



def extract_data(start_date, end_date):
    '''
    Scrapes the winning numbers between the start and end dates
    Args:
    start_date (date) : Start date of results to be fetched
    end_date (date)   : End date of results to be fetched

    Returns:
    data (Dataframe)  : Containing dates and powerball winning numbers 
    '''
    data = pd.DataFrame(columns=['date']+ ['white_balls']+['powerball'])
    results = []
    # while start_date.date() < end_date:
    while start_date <= end_date:
        temp_date = add_days(start_date, 90) # Temp date of 3 months since results > 3 months are consolidated
        url = f'https://www.powerball.com/previous-results?gc=powerball&sd={start_date}&ed={temp_date}'
        response = requests.get(url)

        # Parse the html
        soup = BeautifulSoup(response.content, 'lxml')

        # Find all date and number sections
        entries = soup.find_all('div', class_='col-12 col-lg-4')

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
        start_date = add_days(temp_date,1)
    data = pd.concat([data, pd.DataFrame((results), columns=data.columns)], ignore_index=True)
    #data = data.drop_duplicates(subset=['date', 'white_balls', 'powerball'], keep='last')
    data['date'] = data['date'].str.replace(r'^[A-Za-z]+, ', '', regex=True) # Convert the date column to correct type
    data['date'] = pd.to_datetime(data['date'], format='%b %d, %Y')
    data = data.sort_values(by='date') # Sort by date
    return data
    
# %%
if __name__ == "__main__":
    if os.path.exists('table.csv'):
        print('CSV already exists')
        table = pd.read_csv('table.csv', parse_dates=['date'])
        cont_date = table['date'].iloc[-1].date() # Most recent date scrape in CSV
        end_date = datetime.date.today() # Execution date of the script
        data = pd.concat([table.iloc[:-1], extract_data(cont_date, end_date)], ignore_index=True) # Remove the last row since being duplicated during concatenation
        data.to_csv('table.csv', index=False)
        print(colorama.Fore.GREEN, 'Finished appending latest results', colorama.Style.RESET_ALL)
    else:
        print('Creating new CSV and inserting the results')
        start_date = datetime.datetime.strptime("1997-11-01", "%Y-%m-%d").date() # Start date of lottery results in the website 
        end_date = datetime.date.today() # Execution date of the script
        table = extract_data(start_date, end_date)
        print(colorama.Fore.GREEN, 'Finished inserting all the results', colorama.Style.RESET_ALL)
        table.to_csv('table.csv', index=False)
    