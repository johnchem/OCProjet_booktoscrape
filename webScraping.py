#! \env\scripts\python
# -*-coding: utf-8 -*-
import requests
import bs4
import os
import re
from pathlib import *
import urllib
import csv
import webbrowser

WEBSITE = "http://books.toscrape.com/"
TRAVEL_PAGE = "http://books.toscrape.com/catalogue/category/books/travel_2/index.html"
SEQUENTIAL_ART_PAGE = "http://books.toscrape.com/catalogue/category/books/sequential-art_5/index.html"
BOOK_PAGE = "http://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html"

def get_main_page():
	r = requests.get(WEBSITE)
	print(r.text)

def get_category_data(category_url):
	# generate output variable
	output_list = []

	# collect the raw html
	r = requests.get(category_url)
	r.encoding = 'utf-8'
	soup = bs4.BeautifulSoup(r.text, 'html.parser')

	# get category name
	category_name = soup.find("div", class_="page-header action").h1.text
	print(category_name)

	# get the number of book in the category
	hits_result = soup.form.find("strong")
	print(hits_result.contents[0])

	# collect book data while next button exists
	next_button = soup.find('li', class_="next")
	while next_button:
		next_url = urllib.parse.urljoin(category_url, next_button.a.attrs["href"])
		print(next_url)
		
		# list of all book 
		list_article = soup.find_all("article")
		for article in list_article:
			raw_url_article = article.div.a.attrs["href"]
			url_article = urllib.parse.urljoin(category_url, raw_url_article)
			output_list.append(get_article_data(url_article, category = category_name))
			
		# move to the next page
		print("move to next page ...")
		r = requests.get(next_url)
		r.encoding = 'utf-8'
		soup = bs4.BeautifulSoup(r.text, 'html.parser')

		# check for next page
		next_button = soup.find('li', class_="next")

	output_file(output_list, f"{category_name}.csv")
	quit()


	
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
	r.encoding = 'utf-8'
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

	# get product description
	result_desc = soup.article.find("p", class_=None)
	item_data["product_description"] = result_desc.contents[0]

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
		writer = csv.DictWriter(fichier_csv, fieldnames=columns, delimiter=',')
		
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

	return None

def convert_availability(stock):
	re_stock = re.compile(r"(\d+)")
	value_stock = re_stock.search(stock)
	return value_stock.group(0)

def get_picture():
	pass


if __name__ == '__main__':
	#get_main_page()
	get_category_data(SEQUENTIAL_ART_PAGE)
	#output = get_article_data(BOOK_PAGE, category="travel")
	#output_file(output, "test.csv")
	
	pass