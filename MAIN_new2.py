from logging import exception

import finnhub
import pandas as pd
from math import sqrt
from datetime import date, timedelta
from time import sleep


API_CALL_LIMIT = 1 #API call limit per second (default = 1 for free keys)
API_CLIENT = None


def main():
    with open('apiKey.txt', 'r') as f:
        api_key = f.read()
        global API_CLIENT
        API_CLIENT = finnhub.Client(api_key = api_key)
        f.close()

    generatePicks(API_CLIENT)

    return



def computeConfidenceRating(_symbol:str = '',
                            _apiClient:finnhub.Client = None,
                            logging: bool = True) -> list:
    if not _symbol:
        exception("Invalid or blank Symbol")
        return 0

    try:
        global API_CLIENT
        _apiClient = API_CLIENT
    except:
        exception("Invalid API Client")
        return [0, 0, '0000-00-00']
    if not _apiClient:
        exception("Invalid API Client")
        return [0, 0, '0000-00-00']



    try:
        _ratings = (_apiClient.recommendation_trends(_symbol))
        _ratings = pd.DataFrame(_ratings)
        _ratings.sort_values(by=['period'], ascending=False)
        _ratings = _ratings.iloc[0]
    except:
        print(f'Ratings Period Key Error for {_symbol}')
        return [0, 0, '0000-00-00']

    ratingsDate = _ratings['period']
    weighted = (
            [0] * _ratings.get('strongSell', 0) +
            [25] * _ratings.get('sell', 0) +
            [50] * _ratings.get('hold', 0) +
            [75] * _ratings.get('buy', 0) +
            [100] * _ratings.get('strongBuy', 0)
    )

    if weighted:
        mean = round((sum(weighted) / len(weighted)), 2)
        meanSquared = sum(x * x for x in weighted) / len(weighted)
        variance = meanSquared - mean ** 2
        std_dev = round(sqrt(variance), 3)
        max_std = 50
        congruency = round(max(0, (1 - (std_dev / max_std))), 4) * 100
        congruency = round(congruency, 2)
    else:
        mean, congruency = 0, 0

    if logging:
        print(f'{_ratings} \n Mean:{mean} \n Congruency:{congruency} \n RatingsDate:{ratingsDate}')

    return [mean, congruency, ratingsDate]



# Gets earnings calendar, ratings, etc... Computes confidence and congruency, returns picks
def generatePicks(_apiClient:finnhub.Client = API_CLIENT,
                  _start: date = date.today(),
                  _end: date = date.today() + timedelta(days=7)):
    if not _apiClient:
        exception("Invalid API Client Object")
        return 0

    calendar = _apiClient.earnings_calendar(_from=_start, to=_end, symbol='', international=False)
    calendar = pd.DataFrame(calendar['earningsCalendar'])
    sleep(API_CALL_LIMIT)

    rows = []
    for CalendarRow in calendar.itertuples():
        EarningsDate = CalendarRow[1]
        symbol = CalendarRow[8]
        ratings = computeConfidenceRating(_apiClient=_apiClient, _symbol=symbol, logging=True)
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


    CSVoutputPath = f'picks{date.today().strftime("%Y%m%d%")}.csv'
    pd.DataFrame(rows).to_csv(CSVoutputPath, index=False)
    return pd.DataFrame(rows)





if __name__ == '__main__':
    main()