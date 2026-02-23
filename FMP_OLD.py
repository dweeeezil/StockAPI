import requests


def formatrequest(urlbase: str,
                  endpoint: str,
                  query: str,
                  apikey: str) -> str:
    if query == "":
        return (f'{urlbase}{endpoint}?apikey={apikey}')
    else:
        return (f'{urlbase}{endpoint}?{query}&apikey={apikey}')

def getresponse(request):
    response = requests.get(request)
    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print(response.status_code)



def main():

    with open('apikey.txt', 'r', encoding='UTF-8') as f:
        api_key = f.read()
        if api_key == '':
            raise Exception('API key is empty')


    request = formatrequest('https://financialmodelingprep.com/stable',
                            '/stock-list',
                            '',
                            api_key)
    getresponse(request)


    return



if __name__ == '__main__':
    main()


