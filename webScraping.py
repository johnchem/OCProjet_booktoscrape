#! \env\scripts\python
# -*-coding: utf-8 -*-
import requests
import bs4
import os
import re
from pathlib import *
import urllib
#import webbrowser

WEBSITE = "http://books.toscrape.com/"
TRAVEL_PAGE = "http://books.toscrape.com/catalogue/category/books/travel_2/index.html"
BOOK_PAGE = "http://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html"


def get_main_page():
	r = requests.get(WEBSITE)
	print(r.text)

def get_category_data(category_url):
	r = requests.get(category_url)
	print(r.json)

def get_article_data(article_url, category = None):
	all_rating = ["one", "Two", "Three", "Four", "Five"]
	# initialize the item's data dictionnary
	item_data = {"product_page_url" : None,
				"universal_product_code(upc)" : None,
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

	pass

def get_picture():
	pass


if __name__ == '__main__':
	#get_main_page()
	#get_category_data(TRAVEL_PAGE)
	get_article_data(BOOK_PAGE)
	pass