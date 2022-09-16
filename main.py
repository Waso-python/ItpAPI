import requests
import json

def main():
    """
    Main function
    """
    session = get_session()
    # get_catalog(session)
    # get_products(session)
    # get_stock(session)
    get_one_product(session, 10278489)

def get_one_product(session, sku:int):
    """
    Get one product
    """
    url = "https://b2b.i-t-p.pro/api/2"
    req = {
    "request": {
        "method": "get_active_products",
        "model": "client_api",
        "module": "platform"
    },
    "filter" : [
        {
            "property" : "sku",
            "operator" : '=',
            "value" : sku
        }
    ],
    "session": session
    }
    data = json.dumps(req)
    response = requests.get(url, data=data)
    response = json.loads(json.dumps(response.json()))
    with open(f'{sku}_products.json', 'w', encoding='utf-8') as f:
        json.dump(response, f, ensure_ascii=False, indent=4)




def get_catalog(session):
    """
    Get catalog once per day
    """
    url = "https://b2b.i-t-p.pro/download/catalog/json/catalog_tree.json"
    cookies = {'session': session}
    response = requests.get(url, cookies=cookies)
    response = json.loads(json.dumps(response.json()))
    with open('catalog.json', 'w', encoding='utf-8') as f:
        json.dump(response, f, ensure_ascii=False, indent=4)

def get_stock(session):
    """
    Get stock
    """
    url = "https://b2b.i-t-p.pro/api/2"
    req = {
    "request": {
        "method": "get_active_products",
        "model": "client_api",
        "module": "platform"
    },
    "session": session
    }
    data = json.dumps(req)
    response = requests.get(url, data=data)
    response = json.loads(json.dumps(response.json()))
    with open('active_products.json', 'w', encoding='utf-8') as f:
        json.dump(response, f, ensure_ascii=False, indent=4)



def get_products(session):
    """
    Get all products
    """
    url = "https://b2b.i-t-p.pro/download/catalog/json/products.json"
    cookies = {'session': session}
    response = requests.get(url, cookies=cookies)
    response = json.loads(json.dumps(response.json()))
    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump(response, f, ensure_ascii=False, indent=4)

def get_session():
    """
    Get session
    """
    url = "https://b2b.i-t-p.pro/api/2"
    req = {
    "data": {
        "login": "********",
        "password": "********",
    },
    "request": {
        "method": "login",
        "model" : "auth",
        "module": "quickfox"
    }
    }
    data = json.dumps(req)
    response = requests.get(url, data=data)
    # response = {"event":0,"expires":"","session":"399354321715A16A387909B1E3352C2C876ECD755DB2273710AA1E1AB584A4DD","success":'true',"total":0}
    response = json.loads(json.dumps(response.json()))
    api_key = response['session']
    return api_key





if __name__ == '__main__':
    main()
