#!/usr/bin/python

import urllib2
import pdb
from bs4 import BeautifulSoup as Soup

host = 'http://www.tvsubs.net/'

def get_soup(url):
	print "Reading %s" % url
	page = urllib2.urlopen(url)
	return Soup(page)

#Root page, with list of all episodes
x = get_soup(host + 'tvshow-3-1.html').body.find('ul', attrs={'class' : 'list1'})

for li in x.children:
	href = li.find_all('a')[0]
	addr = href.attrs['href']
	soup = get_soup(host + addr)
	#pdb.set_trace()
	# first link is for English, this goes to another page where options are given
	dl_url = soup.find('a', text='House M. D. S01E01 720p.Web-DL.TjHD').attrs['href']

	dl_url = host + dl_url
	dl_url2 = get_soup(dl_url).find('a', text='Download subtitles').attrs['href']
	print "Actual download URL: %s" % ( host + dl_url2)

	#This page has to be processed to get the real zip file URL

