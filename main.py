import webScraping as WS
import logging
import os
from time import time
from queue import Queue
from threading import Thread

WEBSITE = "http://books.toscrape.com/"
TRAVEL_PAGE = "http://books.toscrape.com/catalogue/category/books/travel_2/index.html"
SEQUENTIAL_ART_PAGE = "http://books.toscrape.com/catalogue/category/books/sequential-art_5/index.html"
ROMANCE_PAGE = "http://books.toscrape.com/catalogue/category/books/romance_8/index.html"
BOOK_PAGE_1 = "http://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html"
BOOK_PAGE_CHAR_ISSUE = "http://books.toscrape.com/catalogue/ajin-demi-human-volume-1-ajin-demi-human-1_4/index.html"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DownloadWorker(Thread):

	def __init__(self, queue):
		Thread.__init__(self)
		self.queue = queue

	def run(self):
		while True:
			# Get the work from the queue and expand the tuple
			name, url = self.queue.get()
			try:
				print(f"next category : {name}")
				WS.get_category_data(url)
			finally:
				self.queue.task_done()

def main():
	ts = time()
	category_list = WS.get_category_list(WEBSITE)

	# Create a queue to communicate with the worker threads
	queue = Queue()
	# Create 8 worker threads
	for x in range(8):
		worker = DownloadWorker(queue)
		# Setting daemon to True will let the main thread exit even though the workers are blocking
		worker.daemon = True
		worker.start()
	# Put the tasks into the queue as a tuple
	for name, url in category_list:
		if name == "Books": continue
		logger.info(f'Queueing {name}')
		queue.put((name, url))
	# Causes the main thread to wait for the queue to finish processing all the tasks
	queue.join()
	logging.info('Took %s', time() - ts)

'''
# old main function w/o multithreading
def main():
	category_list = WS.get_category_list(WEBSITE)
	for name, url in category_list:
		if name == "Books": continue
		print(f"next category : {name}")
		WS.get_category_data(url)
	print("scrapping finished ... have a nice day !")
	quit()
'''

if __name__ == '__main__':
	main()