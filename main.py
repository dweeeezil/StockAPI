import finnhub
from datetime import date, timedelta
import pandas as pd
from math import sqrt
from time import sleep



def main():
    with open('apiKey.txt', 'r', encoding='UTF-8') as f:
        api_key = f.read()
    finnhub_client = finnhub.Client(api_key = api_key)






    parseCalendar(finnhub_client,
                  readFromCSV = True,
                  readPath = 'calendar2026-02-22.csv',
                  exportCSV = True,
                  logging = True)

    #print(confidenceRating(finnhub_client, symbol = 'CANN'))




    return


def parseCalendar(client: finnhub.Client,
                  calendar = None,
                  readFromCSV:bool = False,
                  readPath:str = '',
                  exportCSV:bool = False,
                  exportPath:str = f'RatingsCalendar{date.today()}.csv',
                  logging:bool = True) -> pd.DataFrame:
    if readFromCSV:
            calendar = pd.read_csv(readPath)

    calenderLength = len(calendar)
    exportRows = []

    for CalendarEntry in calendar.itertuples():
        #date = CalendarEntry[0]
        #epsActual = CalendarEntry[1]
        #epsEstimate = CalendarEntry[2]
        #hour = CalendarEntry[3]
        #quarter = CalendarEntry[4]
        #revenueActual = CalendarEntry[5]
        #revenueEstimate = CalendarEntry[6]
        #symbol = CalendarEntry[7]
        #year = CalendarEntry[8]

        ratings = confidenceRating(client, symbol = CalendarEntry[8])

        currentrow = {
            'Release Date': CalendarEntry[0],
            'RevenueActual': CalendarEntry[5],
            'RevenueEstimate': CalendarEntry[6],
            'symbol': CalendarEntry[8],
            'Confidence': ratings['Confidence'],
            'LastUpdated': ratings['Period'],
            'Congruency': ratings['Congruency'],
        }


        exportRows.append(currentrow)

        if logging:
            output = f'Generating Ratings, progress: {round(((CalendarEntry.Index / calenderLength) * 100), 1)}%'
            print(output, end='\r', flush=True)

        sleep(1)  # sleep 1s to avoid api call limit

        #------------------------------------ END OF LOOP ---------------

    exportRows = pd.DataFrame(exportRows)
    exportRows.sort_values(by='Confidence', ascending=False, inplace=True)

    if exportCSV:
        exportRows.to_csv(exportPath, index=False)
    print('Done!')
    return exportRows


def getCalendar(client: finnhub.Client,
                _from:date = date.today(),
                _to:date = (date.today()) + timedelta(days=7),
                symbol:str = '',
                exportCSV: bool = False) -> pd.DataFrame:


    calendarRaw = client.earnings_calendar(_from=_from, to=_to, symbol=symbol, international=False)
    calendar = pd.DataFrame(calendarRaw['earningsCalendar'])

    if exportCSV:
        calendar.to_csv(f'calendar{date.today()}.csv', index=False)

    sleep(2) #api call limit timing
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
        -2: -2 * latest['strongSell'],
        -1: -1 * latest['sell'],
        0: 0 * latest['hold'],
        1: latest['buy'],
        2: 2 * latest['strongBuy'] #still not great, need to improve
    }

    max = sum([latest['strongSell'], latest['sell'], latest['hold'], latest['buy'], latest['strongBuy']])

    N = sum(weighted.values()) # this is wrong, N should be sum of values * their weights
    if N == 0:
        raise Exception('No data')


    mean = sum(score * count for score, count in weighted.items()) / N
    variance = sum(count * (score - mean)**2
                   for score, count in weighted.items()) / N

    #std_dev = sqrt(variance)


    #confidence = float(round(mean, 2))
    confidence = float(round((N / max), 2))
    congruency = 0#round((1 - (std_dev / 2)), 2)

    data = {'Confidence': confidence,
            'Period' : period,    #how up to date ratings are
            'Congruency': congruency,
            'Symbol': symbol}


    return (data)





if __name__ == '__main__':
    main()
