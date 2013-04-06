#!/usr/bin/python

import urllib2
import pdb
import re

from bs4 import BeautifulSoup as Soup
from pprint import pprint

host = 'http://www.tvsubs.net/'

def get_soup(url):
	print "Reading %s" % url
	page = urllib2.urlopen(url)
	return Soup(page)

def get_var(line):
	"Get var value, return None if no match"
	pat = "var\s+(.*)\s*=\s*'(.*)'\s*;"
	mat = re.compile(pat)
	mo = re.search(mat, line)
	if mo:
		return (mo.group(1), mo.group(2))
	else:
		return (None, None)

def down_zip(url):
	"url: page address that's nofollow"
	jsvars = {}
	jsvars['s1'] = 'fil' # this is missing from the actual remote file

	page = urllib2.urlopen(url)
	for l in page:
		name, value = get_var(l)
		if name:
			jsvars[name] = value
	zip_addr = jsvars['s1'] + jsvars['s2'] + jsvars['s3'] + jsvars['s4']
	zip_addr = host + zip_addr
	print zip_addr

def main():
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

		down_zip(host + dl_url2)

def test_get_var():
	lines = [ "var s2= 'es/H';",
		"var s3= 'ou';",
		"var s4= 'se.M..D..S01E18.720p.Web-DL.TjHD.en.zip';" ]

	for l in lines:
		pprint(get_var(l))

if __name__ == '__main__':
	main()
