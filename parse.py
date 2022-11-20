import json, sys
from time import sleep
from main import get_session, get_image, get_db_connection, get_catalog, get_products, get_stock
from datetime import datetime
from log_bot import add_to_table

def error_bot(rec, priority):
    rec = [rec, 2, priority]
    add_to_table(rec)

def save_error(err_text):
	err_text =str(datetime.now()) + ' ' + err_text + '\n'
	error_bot(err_text, 2)
	with open('error.txt', 'a', encoding='utf-8') as f:
		f.write(err_text)

def get_catalog_from_json():
	items = []
	result = []
	with open('catalog.json', 'r', encoding='utf-8') as f:
		items = json.load(f)

	def add_item(item):
		result.append(item)

	def rec(items):
		for item in items:
			dict_ = {}
			dict_['id'] = item['id']
			dict_['name'] = item['name']
			dict_['leaf'] = item['leaf']
			if 'parentId' in item.keys():
				dict_['parentId'] = item['parentId']
			else:
				dict_['parentId'] = 'NULL'
			if 'childrens' in item.keys():
				dict_['childrens'] = True
				add_item(dict_)
				rec(item['childrens'])
			else:
				dict_['childrens'] = False
				add_item(dict_)
	rec(items)
	with open('catalog_new.json', 'w', encoding='utf-8') as f:
		json.dump(result, f, ensure_ascii=False, indent=4)
	return result

def get_products_from_json():
	products = []
	with open('products.json', 'r', encoding='utf-8') as f:
		products = json.load(f)
	return products


def catalog_to_db():
	sql = '''insert into catalog (id,leaf,name,parentid,childrens) values ({id}, {leaf}, '{name}', {parentid}, {childrens})
			 ON CONFLICT (id) DO UPDATE SET (leaf, name, parentid, childrens) = (EXCLUDED.leaf, EXCLUDED.name, EXCLUDED.parentid, EXCLUDED.childrens)'''
	con = get_db_connection()
	cursor = con.cursor()
	try:
		for item in get_catalog_from_json():
			cursor.execute(sql.format(
				id = item['id'], leaf = item['leaf'],
				 name = item['name'].replace("'",""),
				  parentid = item['parentId'], childrens = item['childrens']))
		con.commit()
	except Exception as e:
		save_error(str(e))
		con.rollback()
	cursor.close()
	con.commit()
	con.close()

def images_to_db():
	sql = '''insert into images (id, deleted, priority, sku, url) values ({id}, {deleted}, {priority}, {sku}, '{url}')
			 ON CONFLICT (id) DO UPDATE SET (deleted, priority, sku, url) = (EXCLUDED.deleted, EXCLUDED.priority, EXCLUDED.sku, EXCLUDED.url)'''
	con = get_db_connection()
	cursor = con.cursor()
	try:
		for image in get_images_from_json():
			cursor.execute(sql.format(id = image['id'], deleted = image['deleted'], priority = image['priority'] if 'priority' in image.keys() else 0, sku = image['sku'], url = image['url']))
		con.commit()
	except Exception as e:
		save_error(str(e))
		con.rollback()
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
	for i, product in enumerate(get_products_from_json()):
		print(i)
		try:
			cursor.execute(sql.format(
			barcodes = product['barcodes'] if 'barcodes' in product.keys() else None, category = product['category'], has_image = product['has_image'],
			multiplicity = product['multiplicity'], name = product['name'].replace("'",""), part = product['part'].replace("'",""), 
			sku = product['sku'], vendor = product['vendor'].replace("'",""), volume = product['volume'],
			warranty = product['warranty'].replace("'","") if 'warranty' in product.keys() else None , weight = product['weight']))
			con.commit()
		except Exception as e:
			con.rollback()
			save_error(str(e))
			print(e)
	cursor.close()
	con.commit()
	con.close()

def active_products_to_db():
	sql = '''insert into active_products (sku, qty, price, delivery_days) 
			 values ({sku}, '{qty}', {price}, {delivery_days})
			 ON CONFLICT (sku) DO UPDATE SET (qty, price, delivery_days)
			  = (EXCLUDED.qty, EXCLUDED.price, EXCLUDED.delivery_days);
			  INSERT INTO public.price_monitoring (sku, price) VALUES({sku},{price});'''
	con = get_db_connection()
	cursor = con.cursor()
	for i, product in enumerate(get_active_products()):
		print(i)
		try:
			cursor.execute(sql.format(
			sku = product['sku'], qty = product['qty'], price = product['price'],
			delivery_days = product['delivery_days'] if 'delivery_days' in product.keys() else 0))
			con.commit()
		except Exception as e:
			con.rollback()
			save_error(str(e))
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
	return active_products['data']['products']

def has_image(sku:int):
	products = get_products_from_json()
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
	try:
		for i, el in enumerate(active_products):
			print(i)
			if len(hundered_sku) < 98:
				if el['sku']:
					hundered_sku.append(el['sku'])
			else:
				temp_list = []
				temp_list = get_image(session, hundered_sku)
				if temp_list:
					images.extend(temp_list)
				# print(images)
				hundered_sku = []
	except Exception as e:
		save_error(str(e))
		

	# images+=get_image(session, hundered_sku)
	with open('images.json', 'w', encoding='utf-8') as f:
		json.dump(images, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
	try:
		if len(sys.argv) == 2:
			if sys.argv[1] == 'all':
				session = get_session()
				get_catalog(session)
				get_products(session)
				get_stock(session)
				catalog_to_db()
				products_to_db()
				active_products_to_db()
			elif sys.argv[1] == 'all_images':
				get_images()
				images_to_db()
			elif sys.argv[1] == 'active_products':
				session = get_session()
				get_stock(session)
				active_products_to_db()
			elif sys.argv[1] == 'x':
				pass
		else:
			raise ValueError('Count of arg')
		error_bot(f"SUCCESS PARSING WITH ARGUMENTS - {sys.argv[1]}", 1)
	except Exception as e:
		save_error(str(e))
