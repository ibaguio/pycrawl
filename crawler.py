#!/usr/bin/env python

import urllib,urllib2
import re
from urllib2 import HTTPError, URLError
from utils import *	#self defined utility lib

root = "http://registrar.sc.edu/"
sub_root = "/html/course_listings/Columbia/%(term)/ACCT(%term).htm"%(term = )

testUrls = ["http://registrar.sc.edu/html/Course_Listings/Columbia/201241shortDept.htm","http://registrar.sc.edu/html/Course_Listings/Columbia/201141shortDept.htm"]
user_agent = "Mozilla/4.0 (compatible; MSIE 9.0; Windows NT)"
headers = {'User-Agent': user_agent}

"""Attempts to open a url and returns the contents if url is correct
   returns False or none if error (404 or etc)"""
def getPage(url):
	global responses
	try:
		print 'Trying to fetch',url
		req = urllib2.Request(url)
		response = urllib2.urlopen(req)
		page = response.read()
		print 'Fetch completed; Size:',len(page)
		return page
	except HTTPError, e:
		print 'The server couldn\'t fulfill the request.'
		print 'Error code:', e.code, responses[int(e.code)]
	except URLError, e:
		print 'Failed to reach',url
		print 'Reason:', e.reason


"""Returns the main table of the main page that contains all the list of subjects/course
   5th inner <table> """
def getMainList(page):
	mainList = ""
	if page:
		mainList = page[page.index("<TABLE>"):page.index("</TABLE>")]
		if mainList:
			to_replace = r"<TD>|</TD>|<HR>|<TR>|</TR>"
			mainList = re.sub(to_replace,"",mainList)
			mainList = re.sub("(\n)+","\n",mainList)
	return mainList

#test main function
def main():
	for url in testUrls[:1]:
		page = getPage(url)
		mainList = getMainList(page)
		print mainList, type(mainList)


if __name__ == "__main__":
	main()
