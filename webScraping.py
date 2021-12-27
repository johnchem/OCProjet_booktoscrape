#! \env\scripts\python
# -*-coding: utf-8 -*-

import requests
import bs4
import os
import re
from pathlib import *
from PIL import Image
import urllib
import csv
import webbrowser

WEBSITE = "http://books.toscrape.com/"
TRAVEL_PAGE = "http://books.toscrape.com/catalogue/category/books/travel_2/index.html"
SEQUENTIAL_ART_PAGE = "http://books.toscrape.com/catalogue/category/books/sequential-art_5/index.html"
ROMANCE_PAGE = "http://books.toscrape.com/catalogue/category/books/romance_8/index.html"
BOOK_PAGE = "http://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html"
WEBPAGE_ENCODING = "utf-8"


def get_category_list(website):
	r = requests.get(website)
	r.encoding = WEBPAGE_ENCODING
	soup = bs4.BeautifulSoup(r.text, 'html.parser')

	hits_category = soup.find("div", class_="side_categories").ul.find_all("a")
	category_list = []
	for cat in hits_category:
		category_name = cat.get_text().strip()
		category_url = urllib.parse.urljoin(website, cat.attrs["href"])
		category_list.append((category_name, category_url))
	return category_list

def get_category_data(category_url):
	# generate output variable
	output_list = []

	# collect the raw html
	r = requests.get(category_url)
	r.encoding = WEBPAGE_ENCODING
	soup = bs4.BeautifulSoup(r.text, 'html.parser')

	# get category name
	category_name = soup.find("div", class_="page-header action").h1.text
	#print(category_name)

	# get the number of book in the category
	hits_result = soup.form.find("strong")
	print(f"{hits_result.contents[0]} books in the category")

	
	# incremental number 
	i = 0
	# loop control 
	pursue_scraping = True

	while pursue_scraping:	
		# list of all book 
		list_article = soup.find_all("article")
		for article in list_article:
			i+=1
			title = article.h3.a.attrs["title"]
			print(f"{i} - {title}")
			raw_url_article = article.div.a.attrs["href"]
			url_article = urllib.parse.urljoin(category_url, raw_url_article)
			output_list.append(get_article_data(url_article, category = category_name))
	
		# collect book data while next button exists
		next_button = soup.find('li', class_="next")
		
		if next_button:
			pursue_scraping = True

			# move to the next page
			next_url = urllib.parse.urljoin(category_url, next_button.a.attrs["href"])
			print("move to next page ...")
			print(next_url)
			r = requests.get(next_url)
			r.encoding = WEBPAGE_ENCODING
			soup = bs4.BeautifulSoup(r.text, 'html.parser')
		
		else:
			pursue_scraping = False
		
	del_output_file(f"{category_name}.csv")
	output_file(output_list, f"{category_name}.csv")
	return None

def get_article_data(article_url, category = None):
	all_rating = ["One", "Two", "Three", "Four", "Five"]
	# initialize the item's data dictionnary
	item_data = {"product_page_url" : None,
				"universal_product_code (upc)" : None,
				"title" : None,
				"price_including_tax" : None,
				"price_excluding_tax" : None,
				"number_available": None,
				"product_description" : None,
				"category" : None,
				"review_rating" : None,
				"image_url" : None}
	# collect the raw html
	r = requests.get(article_url)
	r.encoding = WEBPAGE_ENCODING
	soup = bs4.BeautifulSoup(r.text, 'html.parser')

	# record the category
	if category : item_data["category"] = category
	
	# get the produt page url
	item_data["product_page_url"] = article_url

	# get the title
	result_title = soup.find("div", class_="content").find("h1")
	item_data["title"] = result_title.get_text()

	# get the rating then turn word into numeric value
	re_rating = re.compile(r"(?:star-rating) (\w*)")
	result_rating = soup.find("p", class_=re_rating)
	raw_rating = result_rating["class"][1]
	item_data["review_rating"] = all_rating.index(raw_rating)+1

	# get the picture url
	result_picture = soup.find("img")
	relative_url = result_picture.attrs["src"]
	item_data["image_url"] = urllib.parse.urljoin(article_url, relative_url)

	#save the picture
	dir_name = Path(category)
	picture_file_name = f'{item_data["title"]}.jpg'
	get_picture(item_data["image_url"], picture_file_name, dir_name)

	# get product description
	result_desc = soup.article.find("p", class_=None)
	print(type(result_desc.contents[0]))
	item_data["product_description"] = result_desc.contents[0]
	# if '\u203d' in item_data["product_description"]:


	# get data from the table
	conversion_dict = {"UPC":"universal_product_code (upc)",
						"Price (excl. tax)":"price_excluding_tax",
						"Price (incl. tax)":"price_including_tax",
						"Availability":"number_available"}
	result_table = soup.article.table
	result_table_row = result_table.find_all("tr")
	table_split = [(item.th.contents[0], item.td.contents[0]) for item in result_table_row]
	
	for tag, value in table_split:
		
		# distribute the data in the main dictionnary
		if tag in conversion_dict:
			
			# take care of the special case of availability
			if tag == "Availability":
				new_tag = conversion_dict[tag]
				item_data[new_tag] = convert_availability(value)
			else:
				# associate the other value
				new_tag = conversion_dict[tag]
				item_data[new_tag] = value	
	return item_data

def del_output_file(file_name):
	if Path(file_name).is_file():
		os.remove(file_name)
		print(f"{file_name} remove from directory")
	else :
		print("the file doesn't exists yet.")

def output_file(data, file_name):
	columns = ["product_page_url",
				"universal_product_code (upc)",
				"title",
				"price_including_tax",
				"price_excluding_tax",
				"number_available",
				"product_description",
				"category",
				"review_rating",
				"image_url"]

	# switch to create column header if new file
	create_header = not Path(file_name).exists()

	# write the data
	with open(file_name, "a", newline="") as fichier_csv:
		writer = csv.DictWriter(fichier_csv, fieldnames=columns, 
											dialect='excel')
		
		if create_header:
			writer.writeheader()
		
		# change pattern depending of 1 dict or list of dict
		if isinstance(data, dict):
			writer.writerow(data)
		elif isinstance(data, list):
			for item in data:
				writer.writerow(item)
		else:
			raise Exeption("wrong output data format")
	
		fichier_csv.close()
	print(f"{file_name} created")

	return None

def wrong_char_handler(string):
	return re.sub(r'[\\/*?:"<>|]',"_",string)

def convert_availability(stock):
	re_stock = re.compile(r"(\d+)")
	value_stock = re_stock.search(stock)
	return value_stock.group(0)

def get_picture(image_url, name, directory):
	img = Image.open(requests.get(image_url, stream = True).raw)
	dir_path = "picture" / directory

	# check if directory is already created
	create_picture_file(dir_path)

	# store the file path
	name = wrong_char_handler(name)
	picture_path = dir_path / name
	[]
	if not picture_path.exists():
		try:
			img.save(picture_path)
		except Exception as e:
			print("erreur avec fichier %s : %s" % (name, e))
	pass

def create_picture_file(dir_name):
	if not dir_name.is_dir():
		os.makedirs(dir_name)
		print("fichier '%s' crée" % dir_name)
	pass


if __name__ == '__main__':
	category_list = get_category_list(WEBSITE)
	for name, url in category_list:
		if name == "Books": continue
		print(f"next category : {name}")
		get_category_data(url)
	print("scrapping finished ... have a nice day !")
	quit()
	#get_category_data(ROMANCE_PAGE)
	#output = get_article_data(BOOK_PAGE, category="travel")
	#output_file(output, "test.csv")	
	pass