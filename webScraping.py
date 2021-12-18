#! \env\scripts\python
# -*-coding: utf-8 -*-
import requests
import bs4
import os
import re
from pathlib import *


WEBSITE = "http://books.toscrape.com/"
TRAVEL_PAGE = "http://books.toscrape.com/catalogue/category/books/travel_2/index.html"
BOOK_PAGE = "http://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html"


def get_main_page():
	r = requests.get(WEBSITE)
	print(r.text)

def get_category_data(category_url):
	r = requests.get(category_url)
	print(r.json)

def get_article_data(article_url):
	# collect the raw html
	r = requests.get(article_url)
	soup = bs4.BeautifulSoup(r.text, 'html.parser')
	
	# get the title
	result_title = soup.find("div", class_="content").find("h1")
	print(result_title.get_text())

	# get the rating
	re_rating = re.compile("star_rating {*}")
	result = soup.find_all("a", class_=re_rating)
	print(result.attrs)



def get_picture():
	pass


if __name__ == '__main__':
	#get_main_page()
	#get_category_data(TRAVEL_PAGE)
	get_article_data(BOOK_PAGE)
	pass