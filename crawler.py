#!/usr/bin/env python

import urllib,urllib2
import re
import sys
from xlwt import *
from urllib2 import HTTPError, URLError
from utils import *	#self defined utility library
from bookParser import *
from courseParser import *
from xls_utils import *

#URIs
homePage = "http://registrar.sc.edu"
dept_url = "/html/Course_Listings/Columbia/%(term)sshortDept.htm"
courses_url = "/html/course_listings/Columbia/%(term)s/%(dept)s%(term)s.htm"
class_link = "/html/course_listings/Columbia/%(term)s/%(dept)s/%(class_level)s/%(dept)s%(courseNum)s%(isMay)s%(section)s.htm"
bookstore_URI = "https://secure.bncollege.com/webapp/wcs/stores/servlet/TBListView"
main_term = ""

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

user_agent = "Mozilla/4.0 (compatible; MSIE 9.0; Windows NT)"
headers = {'User-Agent': user_agent}

"""Attempts to open a url and returns the contents if url is correct
   returns False or none if error (404, etc)"""
 #set x to true if you want this function to print details
def getPage(url,verbose=False,data=None):
	global responses
	if data:
		data = urllib.urlencode(data)
	try:
		if verbose:
			print 'Trying to fetch',url
		req = urllib2.Request(url,data,headers)
		response = urllib2.urlopen(req)
		page = response.read()
		if verbose:
			print 'Fetch completed; Size:',len(page)
		return page
	except HTTPError, e:
		print 'The server couldn\'t fulfill the request. On URL',url
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
	to_remove = r'<TABLE BORDER=1>|<FONT SIZE=-2><A[<a-zA-Z0-9\./ \=\:\>\"]*</A></FONT></FONT>|<B><FONT COLOR=\"FF0000\">\*</FONT></B>'
	rawHTML = re.sub(to_remove,"",rawHTML)

	#replace empty <td></td> tag with empty <td><font></font></td> so parser wouldnt get confused
	#that there is no class number
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

#sets the department class limit of each class
def setDeptClassLimit(courses):
	for course in courses:
		for class_ in course.getClasses():
			clevel = course.courseNumber[0]+"00"
			isMay = ""		#url of may terms are different! err!
			if main_term[-2:] == "mm":
				isMay = "M"
			url = homePage+class_link%{'term':main_term,'dept':course.department,'class_level':clevel,'section':class_.section,'courseNum':class_.courseNumber,'isMay':isMay}
			#print "Crawling for",course.department,course.courseNumber,"Section",class_.section,"..."
			page = getPage(url)
			limit = parseClassLimit(page)
			class_.setDeptLimit(limit)
			randomPause()

def parseClassLimit(page):
	find1 = "<TR><TD><B>Department Limit:  </B></TD><TD>"
	find2 = "</TD></TR>"
	page = page[page.index(find1)+len(find1):]
	limit = page[:page.index(find2)]
	return int(limit)

"""Given the home/homePage page, gets the term"""
def getTerm(page):
	try:
		search = "by Department for "
		term = page[page.index(search)+len(search):]
		term = term[:term.index(',')]
	except:
		print "Term and year does not exist!"
		sys.exit()
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
	elif "Spring":
		t = "W"+yr
	else:
		print "WARNING NO TERM IN CRAWLING BOOKS"
	
	#Finish filling up data to be sent to server thru post
	bookData["courseXml"] = courseXml%({ 'dept'	   : dept,
				'section'  : class_.section,
				'courseNum': course.courseNumber,
				'term'	   : t})
	
	print "Crawling Book info for",dept,class_.courseNumber,"Section", class_.section
	page = getPage(bookstore_URI,data=bookData)
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

#asks for user input on what term
def getUserTerm():
	clearScreen()
	print "Choose Term:"
	print "  1. Fall"
	print "  2. May"
	print "  3. Summer I"
	print "  4. Summer II"
	print "  5. Spring"	
	while True:
		t = raw_input("Term: ")
		if int(t[0]) in range(1,6):
			break
	yr = "0000"
	if len(t) == 6:
		yr = t[2:]
		t = t[0]
	while int(yr) < 2011:
		yr = raw_input("Enter year (format: 20xx): ")

	if t == '1':	#fall
		term = yr+"41"
	elif t == '2':#may
		term = yr+"mm"
	elif t == '3':#summer i
		term = yr+"21"
	elif t == '4':#summer ii
		term = yr+"31"
	elif t == '5':#spring
		term = yr+"11"

	return term

#asks user for a list of departments to crawl
def getUserDeptToCrawl(deptURL,deptNames):
	print "\n\nChoose which departments to crawl..."
	print "Formats or Valid Inputs (NOT case sensitive):\n"
	print "  all\t\t\t  fetches info for ALL departments"
	print "  <dept>\t\t  fetches info for <dept> ONLY"
	print "  <dept_1> to <dept_2>\t  fetches info from <dept_1> to <dept_2>"
	print "  <dept> onward\t\t  fetches info from <dept> to the last dept"
	print
	print "    ****************************************************"
	for i in range(len(deptNames)/9 + 1):
		print "  ",
		for v in range(9):
			if 9*i + v < len(deptNames):
				print "",deptNames[9*i + v],
		print
	print "    ****************************************************"
	print
	while True:
		inp = raw_input("Input Department: ")
		if inp.lower() == 'all':
			print "Crawling ALL departments; Count",len(deptNames)
			return deptNames
		elif " to " in inp.lower():
			first = inp[:inp.index(" to")].upper()
			last = inp[inp.index("to ")+3:].upper()
			try:
				f = deptNames.index(first)
			except:
				print "Invalid department '"+first+"'"
				continue
			try:
				l = deptNames.index(last)
			except:
				print "Invalid department '"+last+"'"
				continue
			if f >= l:
				print "Invalid department range"
			else:
				dURL = deptURL[f:l+1]
				dNames = deptNames[f:l+1]
				print "Crawling from",first,"to",last+"; Count",len(dNames)
				return dURL,dNames
		elif "onward" in inp.lower():
			dept = inp.split()[0].upper()
			try:	
				dURL = deptURL[deptNames.index(dept):]
				dNames = deptNames[deptNames.index(dept):]
				print "Crawling",dept,"onwards; Count",len(dNames)
				return dURL,dNames
			except:
				print "Invalid department '"+dept+"'"
		else:
			dept = inp.upper()
			print "Crawling",dept+"; Count 1"
			try:
				return [deptURL[deptNames.index(dept)]],[deptNames[deptNames.index(dept)]]
			except:
				print "Invalid department '"+dept+"'"

#test main function
def main():
	#check if a log folder is created, if not create it (utils.py)
	global main_term
	main_term = getUserTerm()

	checkDirs()
	depts = {}

	course_xls = Workbook()
	book_xls = Workbook()

	dept_sheet = {}
	book_sheet = {}

	dept_sheet_col = 0
	dept_sheet_row = 0

	book_sheet_col = 0
	book_sheet_row = 0
	
	url = homePage + dept_url%{'term':main_term}
	#retrieve the page
	page = getPage(url,verbose=True)
	term,yr = getTerm(page)
	print "\n******************\nTerm is:",term,"\n******************\n"

	#get the depts as a list
	deptList = getDepartments(page)
	print

	#create a list of department urls
	deptURLs = []
		
	#gets all the departments in the home page
	for dept in deptList:
		url = homePage+courses_url%{'term':main_term,'dept':dept}
		deptURLs.append(url)

	#asks the user what departments to crawl
	deptURLs,depts_to_crawl = getUserDeptToCrawl(deptURLs,deptList)

	#gets the courses per department
	for dUrl,dept in zip(deptURLs,depts_to_crawl):
		randomPause()
		courses = getCourses(dUrl,dept,term)
		depts[dept] = courses

	for dName in depts_to_crawl:
		#gets the course limit of each class per dept
		print "Getting Class limit for classes in",dName
		print "Please Wait this might take a while..."
		setDeptClassLimit(depts[dName])
		print "Class Limit for all classes in",dName,"crawled"
		dept_sheet = course_xls.add_sheet(dName)
		book_sheet = book_xls.add_sheet(dName)
		write_course_headers(dept_sheet)
		dept_sheet_row += 1
		write_book_headers(book_sheet) #prepare sheets for course list and book list
		book_sheet_row += 1
		for course in depts[dName]:
			for class_ in course.getClasses():
				randomPause()
				book_list = parseBookStore(crawlBooks(dName,course,class_,term,yr))
				write_class_data(dept_sheet_row, dept_sheet_col, course, class_, book_list, dept_sheet)
				dept_sheet_row += 1

				for book_itr in book_list:
					write_book_data(book_sheet_row, book_sheet_col, book_itr, book_sheet)
					book_sheet_row += 1
				#break
				book_xls.save(xls_dir+'Book List.xls')
			course_xls.save(xls_dir+'Course List.xls')
			book_sheet_row = 0
		dept_sheet_row = 0
	
	print "FINISHED CRAWLING\nHave a nice day!"

if __name__ == "__main__":
	main()
