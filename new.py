
import finnhub
import pandas as pd
from math import sqrt
from datetime import date, timedelta
from time import sleep

API_CALL_LIMIT = 1 #API call limit per second (default = 1 for free keys)
client = None


def main():
    with open('apiKey.txt', 'r') as f:
        api_key = f.read()
        global client
        client = finnhub.Client(api_key = api_key)
        f.close()


    computeConfidenceRating(client, symbol = 'AAPL')


    return



def getWeeklyEarningsCalendar(_apiClient:finnhub.Client = client,
                              _start:date = date.today(),
                              _end:date = date.today() + timedelta(days = 7),
                              _symbol:str = '',
                              printToCSV:bool = False,
                              CSVoutputPath:str = '') -> pd.DataFrame:


    calendarRaw = _apiClient.earnings_calendar(_from=_start, to=_end, symbol=_symbol, international=False)
    calendar = pd.DataFrame(calendarRaw['earningsCalendar'])

    if printToCSV:
        if CSVoutputPath == '':
            CSVoutputPath = f'EarningsCalendar{_start:%Y%m%d}-{_end:%Y%m%d}.csv'
        calendar.to_csv(CSVoutputPath, index=False)

    return calendar


def computeConfidenceRating(_apiClient:finnhub.Client = client,
                            symbol:str = ''):

    ratings = pd.DataFrame(client.recommendation_trends(symbol)).sort_values(by=['period'], ascending=False)
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

    return mean, congruency




if __name__ == "__main__":
    main()