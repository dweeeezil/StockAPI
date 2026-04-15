from sqlite3.dbapi2 import Date

import finnhub
import pandas as pd
from math import sqrt
from datetime import date, timedelta
from time import sleep

from progressBar import ProgressBar

API_CALL_LIMIT = 1 #API call limit per second (default = 1 for free keys)
client = None


def main():
    with open('apiKey.txt', 'r') as f:
        api_key = f.read()
        global client
        client = finnhub.Client(api_key = api_key)
        f.close()


    generatePicks(client)
    return






def getWeeklyEarningsCalendar(_apiClient:finnhub.Client = client,
                              _start:date = date.today(),
                              _end:date = date.today() + timedelta(days = 7),
                              _symbol:str = '',
                              printToCSV:bool = False,
                              CSVoutputPath:str = '') -> pd.DataFrame:

    if not _apiClient:
        global client
        _apiClient = client
    calendarRaw = _apiClient.earnings_calendar(_from=_start, to=_end, symbol=_symbol, international=False)
    calendar = pd.DataFrame(calendarRaw['earningsCalendar'])

    if printToCSV:
        if CSVoutputPath == '':
            CSVoutputPath = f'EarningsCalendar{_start:%Y%m%d}-{_end:%Y%m%d}.csv'
        calendar.to_csv(CSVoutputPath, index=False)
    sleep(API_CALL_LIMIT)
    return calendar


def computeConfidenceRating(_apiClient:finnhub.Client = client,
                            symbol:str = '') -> list:

    try:
        _ratings = (client.recommendation_trends(symbol))
        ratings = pd.DataFrame(_ratings)
        ratings.sort_values(by=['period'], ascending=False)
        print(symbol, ratings)
    except:
        print(f'Ratings Period Key Error for {symbol}')
        return [0, 0, '1970-01-01']
    mostRecentRatings = ratings.iloc[0]

    ratingsDate = mostRecentRatings['period']
    weighted = (
            [0] * mostRecentRatings.get('strongSell', 0) +
            [25] * mostRecentRatings.get('sell', 0) +
            [50] * mostRecentRatings.get('hold', 0) +
            [75] * mostRecentRatings.get('buy', 0) +
            [100] * mostRecentRatings.get('strongBuy', 0)
    )

    if weighted:
        mean = round((sum(weighted) / len(weighted)), 2)
        meanSquared = sum(x * x for x in weighted) / len(weighted)
        variance = meanSquared - mean ** 2
        std_dev = round(sqrt(variance), 3)
        max_std = 50
        congruency = round(max(0, (1 - (std_dev / max_std))), 4) * 100
    else:
        mean, congruency = 0, 0

    return [mean, congruency, ratingsDate]


def generatePicks(_apiClient: finnhub.Client = client,
                  calendar = None,
                  CSVoutputPath: str = '') -> pd.DataFrame:

    if calendar is None:
        calendar = getWeeklyEarningsCalendar(_apiClient = _apiClient)
        sleep(API_CALL_LIMIT + 1)

    if CSVoutputPath == '':
        CSVoutputPath = f'picks{date.today().strftime("%Y%m%d%H%M%S")}.csv'

    rows = []
    for CalendarRow in calendar.itertuples():
        EarningsDate = CalendarRow[1]
        symbol = CalendarRow[8]
        ratings = computeConfidenceRating(_apiClient = _apiClient, symbol = symbol)
        meanRating = ratings[0]
        congruency = ratings[1]
        ratingsDate = ratings[2]


        currentRow = [
            EarningsDate,
            symbol,
            meanRating,
            congruency,
            ratingsDate
        ]
        rows.append(currentRow)
        sleep(API_CALL_LIMIT)

    if CSVoutputPath != '':
        pd.DataFrame(rows).to_csv(CSVoutputPath, index=False)

    return pd.DataFrame(rows)

if __name__ == "__main__":
    main()