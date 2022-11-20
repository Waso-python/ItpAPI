import re
from time import sleep
import requests
import json
import psycopg2
from my_set import DB_NAME, HOST_DB, PORT_DB, USER_DB, PASSWORD_DB

def get_db_connection():
    
    connection = psycopg2.connect(database=DB_NAME, user=USER_DB, password=PASSWORD_DB, host=HOST_DB, port=PORT_DB)
    cursor = connection.cursor()
    return connection

def main():
    """

    Main function
    """
    session = get_session()
    get_catalog(session)
    get_products(session)
    get_stock(session)
    # get_one_product(session, 10278489)
    # get_image(session, 187005)

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
    Get catalog 1 per minute
    """
    url = "https://b2b.i-t-p.pro/download/catalog/json/catalog_tree.json"
    cookies = {'session': session}
    response = requests.get(url, cookies=cookies)
    response = json.loads(json.dumps(response.json()))
    with open('catalog.json', 'w', encoding='utf-8') as f:
        json.dump(response, f, ensure_ascii=False, indent=4)

def get_image(session, sku:list):
    """
    Get image max 100 sku's  2 per second
    """
    sleep(0.6)
    url = "https://b2b.i-t-p.pro/api/2"
    req = {
    "filter": [
        {
            "operator": "IN",
            "property": "sku",
            "value": sku
        }
    ],
    "request": {
        "method": "read_new",
        "model": "products_clients_images",
        "module": "platform"
    },
    "session": session,
}
    data = json.dumps(req)
    response = requests.get(url, data=data)
    response = json.loads(json.dumps(response.json()))
    if response['success']:
        return(response['data']['product_images'])

def get_stock(session):
    """
    Get stock 10 per hour
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
    Get all products 2 per hour
    """
    url = "https://b2b.i-t-p.pro/download/catalog/json/products.json"
    cookies = {'session': session}
    response = requests.get(url, cookies=cookies)
    response = json.loads(json.dumps(response.json()))
    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump(response, f, ensure_ascii=False, indent=4)

def get_session():
    """
    Get session offen 10 per minut
    """
    url = "https://b2b.i-t-p.pro/api/2"
    req = {
    "data": {
        "login": "ks.gulk.client2",
        "password": "123456",
    },
    "request": {
        "method": "login",
        "model" : "auth",
        "module": "quickfox"
    }
    }
    data = json.dumps(req)
    response = requests.get(url, data=data)
    print(response.text)
    response = json.loads(json.dumps(response.json()))
    api_key = response['session']
    return api_key


if __name__ == '__main__':
    main()