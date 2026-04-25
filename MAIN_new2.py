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

    computeConfidenceRating(_symbol='AAPL', logging=True)
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
    except:
        print(f'Ratings Period Key Error for {_symbol}')
        return [0, 0, '0000-00-00']



    if logging:
        print(_ratings)
    return []


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





if __name__ == '__main__':
    main()