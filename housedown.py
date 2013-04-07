#!/usr/bin/env python
#Script that autoamte download subtitle from tvsubs.net
#Requires: beautiful soup on lxml or html5lib

import urllib2
import pdb
import re
import os
import sys
import os.path
import getopt

from bs4 import BeautifulSoup as Soup
from pprint import pprint

__mydebug__ = 1
host = 'http://www.tvsubs.net'
rls_group = 'TjHD'
_season = 1
_group = 'TjHD'

def trace(msg):
	if __mydebug__:
		print msg

def get_season_root(season):
	root_url = 'tvshow-3-%d.html'
	return root_url % season

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


class SubDownlaoder():
	def __init__(self, host, root, group):
		self.host = host # host 
		self.root = root # root URL for a season
		self.group = group # release group 

	def __url(self, rel_url):
		return os.path.join(self.host, rel_url)

	def down_zip(self, url):
		"""tvsubs.net use a technic where:
		1. <a href> with nofollow attribute
		2. JS that sets the current URL to hide actual subtitle URL"""
		jsvars = {}
		jsvars['s1'] = 'fil' # this is missing from the actual remote file

		#Following logic is the derived from the actual web page.
		page = urllib2.urlopen(self.__url(url))
		for l in page:
			name, value = get_var(l)
			if name:
				jsvars[name] = value
		zip_addr = jsvars['s1'] + jsvars['s2'] + jsvars['s3'] + jsvars['s4']

		f = urllib2.urlopen(self.__url(zip_addr))

		trace("Downloading %s " % zip_addr)
		with open(os.path.basename(zip_addr), "wb") as local_file:
			local_file.write(f.read())

		f.close()
		local_file.close()

	def find_sub_by_group(self, url, grp):
		"""url: page address with sub for a certain episodes
		grp: the release grp to search for"""
		soup = get_soup(self.__url(url))

		for a in soup("a"):
			if a.text.find(grp) != -1:
				return a

		return None
		
	def go(self):
		#Root page, with list of all episodes in the whole Season
		#Controlled by the format of the page
		x = get_soup(self.__url(self.root))\
			.body.find('ul', attrs={'class' : 'list1'})

		for li in x.children:
			# first link is for English, this goes to another page where options are given
			if li.text == "": # after the last episode there is a empty li
				break
			addr = li.find_all('a')[0]['href']

			ancr = self.find_sub_by_group(addr, self.group)

			if not ancr:
				print 'Unable to find group %s in %s' % (self.group, self.__url(addr))
				return

			url = get_soup(self.__url(ancr['href']))\
				.find('a', text='Download subtitles')\
				.attrs['href']

			self.down_zip(url)

def main():
	dldr = SubDownlaoder(host, get_season_root(_season), _group)
	dldr.go()

def test_get_var():
	lines = [ "var s2= 'es/H';",
		"var s3= 'ou';",
		"var s4= 'se.M..D..S01E18.720p.Web-DL.TjHD.en.zip';" ]

	for l in lines:
		pprint(get_var(l))

if __name__ == '__main__':
	options, reminder = getopt.getopt(sys.argv[1:], "s:g:", ['season=', 'group='])
	for opt, arg in options:
		if opt in ('-s', '--season'):
			_season = int(arg)
		elif opt in ('-g', '--group'):
			_group = arg
	main()
