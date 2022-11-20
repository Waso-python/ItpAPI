import asyncio
import asyncpg
import psycopg2
import json
from parse import get_products_from_json, get_active_products
from main import get_db_connection


def get_catalog_value(id):
	with open('catalog.json', 'r', encoding='utf-8') as f:
		items = json.load(f)
	for item in items:
		if item['id'] == id:
			return item['name']
	return None

def get_price(sku):
    result = {}
    for item in get_active_products():
        if item['sku'] == sku:
            result['price'] = item['price']
            result['qty'] = item['qty']
            return result
    return None

def get_product_by_text(text):
    result = {}
    for item in get_products_from_json():
        if 'barcodes' in item.keys():
            if item['barcodes'].find(text) != -1:
                result['sku'] = item['sku']
                result['name'] = item['name']
                result['vendor'] = item['vendor']
                result['category'] = get_catalog_value(item['category'])
                price = get_price(result['sku'])
                result['price'] = price['price']
                result['qty'] = price['qty']
                return result
            elif item['name'].find(text) != -1:
                result['sku'] = item['sku']
                result['name'] = item['name']
                result['vendor'] = item['vendor']
                result['category'] = get_catalog_value(item['category'])
                price = get_price(result['sku'])
                result['price'] = price['price']
                result['qty'] = price['qty']
                return result
    return None

# async def get_product_from_db(text):
#     con = await asyncpg.connect('postgresql://ecommerce:SuperShop2022@localhost:5433/ks_ecommerce')
#     SQL = """select p.barcodes, p."name", p.vendor, ap.price, ap.qty 
# from products p 
# right outer join active_products ap on p.sku = ap.sku
# where LOWER(p.barcodes) like LOWER('%{text}%') or LOWER(p."name") like LOWER('%{text}%') """
#     row = await con.fetch(SQL.format(text = text))
#     # print(row)
#     await con.close()
    
# asyncio.get_event_loop().run_until_complete(get_product_from_db('Фасадная'))
    
def get_product_from_db(text):
    con = psycopg2.connect(database='ks_ecommerce', user='ecommerce', password='SuperShop2022', host='localhost', port=5433)
    cursor = con.cursor()
    text = text.replace(' ', '%')
    SQL = """select p.barcodes, p."name", p.vendor, ap.price, ap.qty ,
array_to_string(array(select i.url from images i where i.sku = p.sku), ', ') as images,
p.sku::text || p."name"::text as article,
p.sku
from products p 
right outer join active_products ap on p.sku = ap.sku
where LOWER(p.barcodes) like LOWER('%{text}%') or LOWER(p."name") like LOWER('%{text}%') or p.sku::text like '%{text}%'"""
    cursor.execute(SQL.format(text = text))
    row = cursor.fetchall()
    print(row)
    con.close()
    return row

