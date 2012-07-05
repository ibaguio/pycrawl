#!/usr/bin/env python
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint
import sys

#NOTE: BEFORE PARSING, MAKE SURE ALL THE & ampersands are replaced with another character/string
#HTMLParser would read it as special character

courses = []		#test/temp variable for courses
f = None			#file pointer
verbose = False		#debugging log
next = 0
waitingFor = -1 	
	# CODE      DESCRIPTION
	#  -1 		waiting for nothing
	#	1 		waits for a course name 			#course
	#	2		waits for a class number 			#class
	#	3		waits for a link (of the class) 	#class 	#ignore
	#	4		waits for a course code 			#course #ignore
	#	5		waits for a section number 			#class
	#	6		waits for a meeting time 			#class

code = {-1:'Nothing',
	 1:'Course Name',
	 2:'Class Number',
	 3:'Class Link (ignore)',
	 4:'Course Code(ignore)',
	 5:'Class Section',
	 6:'Class Sched'}

class Book():
	"""Book class, contains info about the classes' books"""
	def __init__(self,info):
		self.title = info['title']
		self.edition = info['edition']
		self.publisher = info['publisher']
		self.isbn = info['isbn']

class Class():
	"""Class class, contains info about the class(course class not OOP class :P)"""
	def __init__(self,classNumber):
		self.classNumber = classNumber
		self.section = ""
		self.schedule = ""
		self.link = ""
		self.books = []

	def setSchedule(self,sched):
		self.schedule = sched
		if verbose:
			f.write("\n"+self.classNumber+" Sched: "+sched)

	def setSection(self,section):
		self.section = section
		if verbose:
			f.write("\n"+self.classNumber+" is Section "+section)

	def addBook(self,info):
		newBook = Book(info)
		self.books.append(newBook)

	def printClassInfo(self):
		return "   NUMBER: "+self.classNumber + "\n   SECTION:"+self.section+"\n  SCHED:   "+self.schedule+"\n  * * * * * * "

class Course():
	"""Course class, contains info about the course, and lists of all classes of that course"""
	def __init__(self,courseName,courseNumber):
		global f
		self.courseName = courseName
		self.courseNumber = courseNumber
		self.classes = []	#list of classes for this course
		if verbose:	
			#print "NEW COURSE:",courseNumber,courseName
			f.write('\n'+"NEW COURSE:"+courseNumber+courseName)

	def addClass(self,newClass):
		global f	
		self.classes.append(newClass)
		if verbose:
			#print self.courseNumber,"NEW CLASS ADDED:"
			f.write("\nNEW CLASS ADDED: "+self.courseNumber)

	#returns the last added class
	def getLastClass(self):
		return self.classes[-1]

	#returns a list of all added classes
	def getClasses(self):
		return self.classes

	def printCourseInfo(self):
		p = "COURSE:"+self.courseNumber+" "+self.courseName+"\nCLASSES(%d):\n"%len(self.classes)
		for c in self.classes:
			p += c.printClassInfo()
		return p

class CourseParser(HTMLParser):
	"""Class used to parse subpage from list of courses from the departments page"""

	#CUSTOM FUNCTIONS
	#set verbose to True in debugging mode
	def customInit(self,verbose_=False):
		global f,verbose
		self.courses = []
		verbose = verbose_
		if verbose:
			f = open("logs/parseLog.txt","a")

	def getCourses(self):
		return self.courses

	#returns the total number of classes of all the courses
	def getClassCount(self):
		count = 0
		for course in self.courses:
			count += len(course.getClasses())
		return count

	#INHERITED FUNCTIONS

	#this function is called whenever a start tag has been parsed
	#attrs is the attributes of the tag
	def handle_starttag(self,tag,attrs):
		global waitingFor,f
		if verbose:
			f.write('\n'+"OPEN TAG: "+tag)
		
		for attr in attrs:
			#colspan is the marker that it is a new Course
			if attr[0] == "colspan" and attr[1] == "3":
				#set marker to 1 and wait for the course name to be parsed
				waitingFor = 1
				if verbose:
					f.write('\n'+"Waiting for New Course")

			#size is the marker for course info
			elif attr[0] == "size" and attr[1] == "-1":
				#set marker to the next details to be parsed
				waitingFor = next
				if verbose:
					f.write('\n'+ "WAITING FOR: "+code[waitingFor])

	#this function is called whenever a end tag has been parsed
	#useless for now
	def handle_endtag(self,tag):
		if verbose:
			f.write('\n'+"ENDTAG: "+tag)

	#this function is called whenever a data is parsed
	#a data is the string between the start and end tag
	#<start_tag> DATA <end tag>
	#watingFor marks the expected data to be read
	def handle_data(self,data):
		global waitingFor, next
		#expects a new Course
		if verbose:
			f.write('\n'+"DATA:"+data)
		if waitingFor == 1:
			data = data.split()						#splits the data to list of words
			cname = str(" ".join(data[2:]))			#course name: 3rd word till last word
			cnum = str(" ".join(data[:2]))			#course num: first and 2nd words
			self.courses.append(Course(cname,cnum))	#append a new Course to list
			waitingFor= -1 							#set marker to -1, waiting for nothing
			next = 2 								#set next to 2, telling the parser that the next
													#data to read is the class number
		elif waitingFor == 2:
			classNumber = data 						#sets the classnumber
			self.courses[-1].addClass(Class(classNumber)) 	#adds a new class to the last course
			waitingFor= -1
			next = 3 								#next data to read is the class link
		elif waitingFor == 3:
			waitingFor= 5							#do not store link, do nothing
		elif waitingFor == 4:						#ignore coursecode, we already have this info
			pass
		elif waitingFor	== 5:
			try: 
				section = data.split()[2]			#get the section
			except IndexError:
				print "Index error! Will QUIT!\nData:",data
				if verbose:
					f.write('\n'+"Index error! Will QUIT!\nData: "+data)
				sys.exit()
			self.courses[-1].getLastClass().setSection(section)	#set the section of the last class of the last course
			waitingFor = -1
			next = 6 								#next data to read is schedule
		elif waitingFor == 6:
			sched = " ".join(data.split()[2:]) 		#reformat the string of schedule
			self.courses[-1].getLastClass().setSchedule(sched)
			waitingFor = -1
			next = 2
