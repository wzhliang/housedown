#!/usr/bin/python

import urllib2
import pdb
import re
import os
import os.path

from bs4 import BeautifulSoup as Soup
from pprint import pprint

__mydebug__ = 1
host = 'http://www.tvsubs.net/'

def trace(msg):
	if __mydebug__:
		print msg

def get_soup(url):
	trace("Reading %s" % url)
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
	"""tvsubs.net use a technic where:
	1. <a href> with nofollow attribute
	2. JS that sets the current URL to hide actual subtitle URL"""
	jsvars = {}
	jsvars['s1'] = 'fil' # this is missing from the actual remote file

	#Following logic is the derived from the actual web page.
	page = urllib2.urlopen(url)
	for l in page:
		name, value = get_var(l)
		if name:
			jsvars[name] = value
	zip_addr = jsvars['s1'] + jsvars['s2'] + jsvars['s3'] + jsvars['s4']
	zip_addr = host + zip_addr

	f = urllib2.urlopen(zip_addr)

	trace("Downloading %s " % zip_addr)
	with open(os.path.basename(zip_addr), "wb") as local_file:
		local_file.write(f.read())

	f.close()
	local_file.close()

def find_sub_by_group(url, grp):
	"""url: page address with sub for a certain episodes
	grp: the release grp to search for"""
	soup = get_soup(url)

	for a in soup("a"):
		if a.text.find(grp) != -1:
			return a

	return None
	
def main():
	#Root page, with list of all episodes in Season 1
	x = get_soup(host + 'tvshow-3-1.html').body.find('ul', attrs={'class' : 'list1'})

	for li in x.children:
		# first link is for English, this goes to another page where options are given
		addr = li.find_all('a')[0]['href']

		ancr = find_sub_by_group(host + addr, 'TjHD')

		dl_url = host + ancr['href']
		dl_url2 = get_soup(dl_url).find('a', text='Download subtitles').attrs['href']
		trace("Actual download URL: %s" % ( host + dl_url2))

		down_zip(host + dl_url2)

def test_get_var():
	lines = [ "var s2= 'es/H';",
		"var s3= 'ou';",
		"var s4= 'se.M..D..S01E18.720p.Web-DL.TjHD.en.zip';" ]

	for l in lines:
		pprint(get_var(l))

if __name__ == '__main__':
	main()
