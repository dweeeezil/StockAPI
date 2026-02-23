import finnhub
from datetime import date, timedelta
import pandas as pd
from math import sqrt
from time import sleep

def main():
    with open('apiKey.txt', 'r', encoding='UTF-8') as f:
        api_key = f.read()
    finnhub_client = finnhub.Client(api_key = api_key)

    #print(getCalendar(client = finnhub_client, outputCSV = True))
    parseCalendar(finnhub_client, readFromCSV=True, path= 'calendar2026-02-22.csv')

    #print(confidenceRating(finnhub_client, symbol = 'CANN'))





    return


def parseCalendar(client: finnhub.Client, calendar = None, readFromCSV:bool = False, path:str = '') -> pd.DataFrame:
    if readFromCSV:
            calendar = pd.read_csv(path)

    for row in calendar.itertuples(index = False):
        date = row[0]
        epsActual = row[1]
        epsEstimate = row[2]
        hour = row[3]
        quarter = row[4]
        revenueActual = row[5]
        revenueEstimate = row[6]
        symbol = row[7]
        year = row[8]


        print(confidenceRating(client, symbol = symbol))
        sleep(1)  # sleep 1s to avoid api call limit



    return calendar




def getCalendar(client: finnhub.Client,
                _from:date = date.today(),
                _to:date = (date.today()) + timedelta(days=7),
                symbol:str = '',
                outputCSV: bool = False) -> pd.DataFrame:


    calendarRaw = client.earnings_calendar(_from=_from, to=_to, symbol=symbol, international=False)
    calendar = pd.DataFrame(calendarRaw['earningsCalendar'])

    if outputCSV:
        calendar.to_csv(f'calendar{date.today()}.csv', index=False)
    return calendar



def confidenceRating(client: finnhub.Client, symbol: str = 'AAPL') -> dict:
    ratings = client.recommendation_trends(symbol)
    ratings = pd.DataFrame(ratings)

    if ratings.empty:
        data = {'Confidence': 0,
                'Period': 0,
                'Congruency': 0,
                'Symbol': symbol}
        return (data)


    ratings = ratings.sort_values(by='period', ascending=False) #sort by most recent
    latest = ratings.iloc[0] #isolate most recent ratings
    #print(ratings)


    period = latest['period']
    weighted = {
        -2: latest['strongSell'],
        -1: latest['sell'],
        0: latest['hold'],
        1: latest['buy'],
        2: latest['strongBuy']
    }

    N = sum(weighted.values()) # this is wrong, N should be sum of values * their weights
    if N == 0:
        raise Exception('No data')

    mean = sum(score * count for score, count in weighted.items()) / N
    variance = sum(count * (score - mean)**2
                   for score, count in weighted.items()) / N

    std_dev = sqrt(variance)


    confidence = float(round(mean, 2)) # wrong, need to figure how tf this returns values of >100%
    congruency = round((1 - (std_dev / 2)), 2)

    data = {'Confidence': confidence,
            'Period' : period,
            'Congruency': congruency,
            'Symbol': symbol}


    return (data)





if __name__ == '__main__':
    main()