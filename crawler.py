#!/usr/bin/env python

import urllib,urllib2
import re
import time
import random
from urllib2 import HTTPError, URLError
from utils import *	#self defined utility lib
from courseParser import *

root = "http://registrar.sc.edu"
sub_root = "/html/course_listings/Columbia/%(term)s/%(dept)s%(term)s.htm"
test_term = "201241"

testUrls = ["http://registrar.sc.edu/html/Course_Listings/Columbia/201241shortDept.htm","http://registrar.sc.edu/html/Course_Listings/Columbia/201141shortDept.htm"]
user_agent = "Mozilla/4.0 (compatible; MSIE 9.0; Windows NT)"
headers = {'User-Agent': user_agent}

"""Attempts to open a url and returns the contents if url is correct
   returns False or none if error (404, etc)"""
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

"""Returns the the list of all departments from the main page"""
def getDepartments(page):
	print "Generating a List of Departments..."
	links = ""
	if page:
		links = page[page.index("<TABLE>")+8:page.index("</TABLE>")]
		if links:
			to_remove = r"<TD>|</TD>|<HR>|<TR>|</TR>"
			links = re.sub(to_remove,"",links)	#removes other tags
			links = re.sub("(\n)+","\n",links)	#removes excess \n

			linksList = []
			for item in links.split("\n"):
				dept = re.search("(?<=htm\">)\w+",item)
				if not dept:
					continue
				linksList.append(dept.group(0))
	print "Departments list generated! Got %d depts" %(len(linksList))
	return linksList

"""Returns the list of courses """
def getCourses(deptUrl):
	print "crawling for ...%s"%(deptUrl[-15:])
	page = getPage(deptUrl)
	rawHTML = page[page.index("<TABLE BORDER=1>"):page.index("</TABLE")]
	to_remove = r"<TABLE BORDER=1>"
	rawHTML = re.sub(to_remove,"",rawHTML)
	parser = CourseParser()

	parser.feed(rawHTML)
	#print rawHTML

#test main function
def main():
	for url in testUrls[:1]:
		#retrieve the page
		page = getPage(url)
		#get the depts as a list
		deptList = getDepartments(page)

		deptURLs = []
		#create a list of department urls
		for dept in deptList:
			url = root+sub_root%{'term':test_term,'dept':dept}
			deptURLs.append(url)

		for dept in deptURLs:
			pause = random.randint(0,1)
			print "pausing for %d sec" %(pause)
			time.sleep(pause)	#pause for 0 or 1 second on every request to not overload the server
			getCourses(dept)
			break

		#print courseURL

if __name__ == "__main__":
	main()
