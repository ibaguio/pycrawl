#!/usr/bin/env python

import urllib,urllib2
import re
import sys
from urllib2 import HTTPError, URLError
from utils import *	#self defined utility library
from bookParser import *
from courseParser import *

root = "http://registrar.sc.edu"
sub_root = "/html/course_listings/Columbia/%(term)s/%(dept)s%(term)s.htm"
bookstore_URI = "https://secure.bncollege.com/webapp/wcs/stores/servlet/TBListView"
test_term = "201241"

bookData = { "catalogId": "10001",
			 "langId"   : "-1",
			 "level"	: "1",
			 "storeId"  : "10052",
			 "courseXml": ""}
courseXml = ' <textbookorder> <courses> <course dept="%(dept)s" num="%(courseNum)s"'+\
			 			  ' sect="%(section)s" term="%(term)s" /></courses> </textbookorder> '

allBooks = []
bookTitles = []
cacheR = 0.0
cacheHIT = 0.0

testUrls = ["http://registrar.sc.edu/html/Course_Listings/Columbia/201241shortDept.htm","http://registrar.sc.edu/html/Course_Listings/Columbia/201141shortDept.htm"]
user_agent = "Mozilla/4.0 (compatible; MSIE 9.0; Windows NT)"
headers = {'User-Agent': user_agent}

"""Attempts to open a url and returns the contents if url is correct
   returns False or none if error (404, etc)"""
def getPage(url,x=False,data=None):
	global responses
	if data:
		data = urllib.urlencode(data)
	try:
		if x:
			print 'Trying to fetch',url
		req = urllib2.Request(url,data,headers)
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
#param page = html text
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
#param  deptUrl = list of urls
#		dept = string dept name
#		term = string term
def getCourses(deptUrl,dept,term):
	print "crawling for ...%s"%(deptUrl[-15:])
	page = getPage(deptUrl)
	rawHTML = page[page.index("<TABLE BORDER=1>"):page.index("</TABLE")]
	to_remove = r'<TABLE BORDER=1>|<FONT SIZE=-2><A[<a-zA-Z0-9\./ \=\:\>\"]*</A></FONT></FONT>|<B><FONT COLOR="FF0000">*</FONT></B>'
	rawHTML = re.sub(to_remove,"",rawHTML)

	#replace empty <td></td> tag with empty <td><font></font></td> so parser wouldnt get confused
	#that there is no class number
	rawHTML = re.sub("<TD></TD>","<TD><FONT SIZE=-1>N/A</FONT></TD>",rawHTML)
	parser = CourseParser()
	parser.customInit(dept,True)	#initialize the courses list
	parser.feed(rawHTML)			#tell the parser to parse rawHTML

	courses = parser.getCourses()
	classCount = parser.getClassCount()
	courseLog(term,courses,dept,classCount)

	print "  DEPT:\t\t",dept
	print "  COURSES:\t",len(courses)
	print "  Total Class:\t",classCount
	print "  * * * * * * * * * * * *"
	return list(courses)

"""Given the home/root page, gets the term"""
def getTerm(page):
	search = "by Department for "
	term = page[page.index(search)+len(search):]
	term = term[:term.index(',')]
	return term, term[-2:]

"""Given a class, sends a request to the bookstore for the class's book info"""
def crawlBooks(dept,course,class_,term,yr):
	if "Fall" in term:
		t = "F"+yr
	elif "Summer II" in term:
		t = "B"+yr
	elif "Summer I" in term:
		t = "A"+yr
	elif "May" in term:
		t = "A"+yr

	#Finish filling up data to be sent to server thru post
	bookData["courseXml"] = courseXml%({ 'dept'	   : dept,
				'section'  : class_.section,
				'courseNum': course.courseNumber,
				'term'	   : t})
	
	#get page
	print "Crawling Book info for ",dept,course.courseNumber,"Section", class_.section
	page = getPage(bookstore_URI,x=True,data=bookData)
	return page

#checks if the title of the book is already in cache, if it is then
#return the book
def checkBookCache(title):
	global cacheR,cacheHIT,allBooks
	cacheR += 1
	if title in bookTitles:
		cacheHIT +=1
		print "Cache HIT","\tHit Rate:",(cacheHIT/cacheR)*100,"%"
		return allBooks[bookTitles.index(title)]
	else:
		print "Cache Miss","\tHit Rate:",(cacheHIT/cacheR)*100,"%"

#adds the book to cache, so that repeating courses may just load book
#info from cache and skip parsing html
def addtoBookCache(book):
	global allBooks,bookTitles
	title = book.getBookInfo("title")
	if title in bookTitles:
		return
	bookTitles.append(title)
	allBooks.append(book)
	print "Added to Cache:"

def parseBookStore(bookstore):
	#markers that there are no books for that course
	noBook = ["This Course does not require any textbooks.","Course Pre-Order"]
	for i in noBook:
		v = re.compile(i)
		if v.match(bookstore):	#no book in page
			print "No book for this course"
			return

	books = []
	#parse books
	try:
		while True:
			bookstore = bookstore[bookstore.index('<td class="sectionImage" rowspan="2">')+1:]

			#parse book title
			title = bookstore[bookstore.index('title="')+len('title="'):]
			title = title[:title.index('"')]

			#check if the book has already been parsed before
			#if yes, continue to next book
			book = checkBookCache(title)
			if book:
				books.append(book)
				continue

			bookstore = bookstore[bookstore.index('<ul class="TBinfo">'):]
			bookHTML = bookstore[:bookstore.index('<div id = "view')]

			#remove white spaces
			bookHTML = re.sub("\s+"," ",bookHTML)

			#remove <li>, <br>
			bookHTML = re.sub("<li>|</li>|<br />","",bookHTML)

			#start parsing books
			parser = BookParser()
			parser.customInit(title)
			parser.feed(bookHTML)

			#get Books from parser
			newBook = parser.getBook()
			books.append(newBook)
			addtoBookCache(newBook)
			print books[-1].printBookInfo()

	except ValueError,e:		#when there are no books, a value error is raised
		pass
	return books

#test main function
def main():
	#check if a log folder is created, if not create it (utils.py)
	checkLogs()
	depts = {}

	for url in testUrls[:1]:
		#retrieve the page
		page = getPage(url,x=True)
		term,yr = getTerm(page)
		print "Term is:",term

		#get the depts as a list
		deptList = getDepartments(page)

		#create a list of department urls
		deptURLs = []
		for dept in deptList:
			url = root+sub_root%{'term':test_term,'dept':dept}
			deptURLs.append(url)
		
		for dUrl,dept in zip(deptURLs,deptList):
			randomPause()
			courses = getCourses(dUrl,dept,term)
			depts[dept] = courses
			break		#remove this in deployment

		for dName in depts:
			for course in depts[dName]:
				for class_ in course.getClasses():
					randomPause()
					bookstore = crawlBooks(dept,course,class_,term,yr)
					parseBookStore(bookstore)

if __name__ == "__main__":
	main()
