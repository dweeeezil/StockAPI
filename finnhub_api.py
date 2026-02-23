import finnhub
from datetime import date, timedelta
import pandas as pd
from math import sqrt

def main():
    with open('apiKey.txt', 'r', encoding='UTF-8') as f:
        api_key = f.read()
    finnhub_client = finnhub.Client(api_key = api_key)

    print(getCalendar(client = finnhub_client, outputCSV = True))





    return





def getCalendar(client: finnhub.Client,
                _from:date = date.today(),
                _to:date = (date.today()) + timedelta(days=7),
                symbol:str = '',
                outputCSV: bool = False) -> pd.DataFrame:


    calendar = client.earnings_calendar(_from=_from, to=_to, symbol=symbol, international=False)
    calendar = pd.DataFrame(calendar)

    if outputCSV:
        calendar.to_csv(f'calendar{date.today()}.csv')
    return calendar



def confidenceRating(client: finnhub.Client, symbol: str = 'AAPL') -> dict:
    ratings = client.recommendation_trends(symbol)
    ratings = pd.DataFrame(ratings)
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

    N = sum(weighted.values())
    if N == 0:
        raise Exception('No data')

    mean = sum(score * count for score, count in weighted.items()) / N
    variance = sum(count * (score - mean)**2
                   for score, count in weighted.items()) / N

    std_dev = sqrt(variance)


    confidence = float(round(mean, 2))
    congruency = round((1 - (std_dev / 2)), 2)

    data = {'Confidence': confidence,
            'Period' : period[0],
            'Congruency': congruency,
            'Symbol': symbol}

    return (data)





if __name__ == '__main__':
    main()