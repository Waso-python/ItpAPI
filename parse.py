import json
from time import sleep
from main import get_session, get_image, get_db_connection


def main():
	cursor = get_db_connection()
	cursor.execute("SELECT * from portal.portal_users;")
	record = cursor.fetchall()

def get_products():
	products = []
	with open('products.json', 'r', encoding='utf-8') as f:
		products = json.load( f)
	return products

def images_to_db():
	sql = '''insert into images (id, deleted, priority, sku, url) values ({id}, {deleted}, {priority}, {sku}, '{url}')
			 ON CONFLICT (id) DO UPDATE SET (deleted, priority, sku, url) = (EXCLUDED.deleted, EXCLUDED.priority, EXCLUDED.sku, EXCLUDED.url)'''
	con = get_db_connection()
	cursor = con.cursor()
	for image in get_images_from_json():
		cursor.execute(sql.format(id = image['id'], deleted = image['deleted'], priority = image['priority'] if 'priority' in image.keys() else 0, sku = image['sku'], url = image['url']))
	cursor.close()
	con.commit()
	con.close()

def products_to_db():
	sql = '''insert into products (barcodes, category, has_image, multiplicity, name, part, sku, vendor, volume, warranty, weight) 
			 values ('{barcodes}', {category}, {has_image}, {multiplicity}, '{name}', '{part}', {sku}, '{vendor}', {volume}, '{warranty}', {weight})
			 ON CONFLICT (sku) DO UPDATE SET (barcodes, category, has_image, multiplicity, name, part, sku, vendor, volume, warranty, weight)
			  = (EXCLUDED.barcodes, EXCLUDED.category, EXCLUDED.has_image, EXCLUDED.multiplicity, EXCLUDED.name, EXCLUDED.part, EXCLUDED.sku, EXCLUDED.vendor, EXCLUDED.volume, EXCLUDED.warranty, EXCLUDED.weight)'''
	con = get_db_connection()
	cursor = con.cursor()
	for i, product in enumerate(get_products()):
		print(i)
		if i < 2000: # delete this
			try:
				cursor.execute(sql.format(
				barcodes = product['barcodes'] if 'barcodes' in product.keys() else None, category = product['category'], has_image = product['has_image'],
				multiplicity = product['multiplicity'], name = product['name'].replace("'",""), part = product['part'], 
				sku = product['sku'], vendor = product['vendor'], volume = product['volume'],
				warranty = product['warranty'] if 'warranty' in product.keys() else None , weight = product['weight']))
			except Exception as e:
				print(e)
	cursor.close()
	con.commit()
	con.close()


def get_images_from_json():
	images = []
	with open('images.json', 'r', encoding='utf-8') as f:
			images = json.load( f)
	return images	

def get_active_products():
	active_products = {}
	with open('active_products.json', 'r', encoding='utf-8') as f:
			active_products = json.load( f)
	return active_products

def has_image(sku:int):
	products = get_products()
	for product in products:
		if product['sku'] == sku:
			if product['has_image'] == True:
				# print(product)
				return True



def get_images():
	session = get_session()
	active_products = get_active_products()
	hundered_sku = []
	images = []
	for i, el in enumerate(active_products['data']['products']):
		if i < 3000:   # delete this
			print(i)
			if len(hundered_sku) < 98:
				if el['sku']:
					hundered_sku.append(el['sku'])
			else:
				temp_list = []
				temp_list = get_image(session, hundered_sku)
				if temp_list:
					images.extend(temp_list)
				print(images)
				hundered_sku = []
		else:
			break

	# images+=get_image(session, hundered_sku)
	with open('images.json', 'w', encoding='utf-8') as f:
		json.dump(images, f, ensure_ascii=False, indent=4)

products_to_db()	
# get_images()
# images_to_db()

# print(has_image(531013))