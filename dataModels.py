#!/usr/bin/env python
file_ = None			#file pointer
verbose = False		#debugging log
if verbose:
	file_ = open("logs/courselogs.log","a")

class Book():
	"""Book class, contains info about the classes' books"""
	def __init__(self,title):
		self.title = title
		self.author = ""
		self.edition = ""
		self.publisher = ""
		self.isbn = ""

	def setAuthor(self,author):
		self.author = author
		
	def setEdition(self,edition):
		self.edition = edition

	def setPublisher(self,publisher):
		self.publisher = publisher

	def setISBN(self,isbn):
		self.isbn = isbn

	def getBookInfo(self,i='all'):
		info = {}
		info["title"] = self.title
		info["author"] = self.author
		info["edition"] = self.edition
		info["publisher"] = self.publisher
		info["isbn"] = self.isbn
		if info == 'all':
			return info
		else:
			return info[i]

	def printBookInfo(self):
		return "   TITLE:\t"+self.title+"\n   AUTHOR:\t"+self.author+\
		"\n   EDITION:\t"+self.edition+"\n   Publisher:\t"+self.publisher+"\n   ISBN:\t"+self.isbn+"\n"

class Class():
	"""Class class, contains info about the class(course class not OOP class :P)"""
	def __init__(self,classNumber):
		self.classNumber = classNumber
		self.courseNumber = ""
		self.section = ""
		self.schedule = ""
		self.link = ""
		self.books = []
		self.courseNumber = ""
		self.deptLimit = 0

	def setCourseNumber(self,cNum):
		self.courseNumber = cNum

	def setSchedule(self,sched):
		self.schedule = sched
		if verbose:
			file_.write("\n   "+self.classNumber+" Sched: "+sched)

	def setSection(self,section):
		self.section = section
		if verbose:
			file_.write("\n   "+self.classNumber+" is Section "+section)

	def setDeptLimit(self,limit):
		self.deptLimit = limit

	def addBook(self,info):
		newBook = Book(info)
		self.books.append(newBook)

	def printClassInfo(self):
		return "   NUMBER:  "+self.classNumber + "\n   SECTION: "+self.section+"\n   SCHED:   "+self.schedule+"\n   LIMIT:"+str(self.deptLimit)+"\n   * * * * * *\n"

class Course():
	"""Course class, contains info about the course, and lists of all classes of that course"""
	def __init__(self,dept,courseName,courseNumber):
		self.department = dept
		self.courseName = courseName
		self.courseNumber = courseNumber
		self.classes = []	#list of classes for this course
		if verbose:	
			#print "NEW COURSE:",courseNumber,courseName
			file_.write("\nNEW COURSE:"+courseNumber+" "+courseName)

	def addClass(self,newClass):
		self.classes.append(newClass)
		if verbose:
			#print self.courseNumber,"NEW CLASS ADDED:"
			file_.write("\n   NEW CLASS ADDED: "+self.courseNumber+" "+newClass.classNumber)

	#returns the last added class
	def getLastClass(self):
		return self.classes[-1]

	#returns a list of all added classes
	def getClasses(self):
		return self.classes

	def printCourseInfo(self):
		p = "\nCOURSE:\t"+self.department+" "+self.courseNumber+": "+self.courseName+"\nCLASSES(%d):\n"%len(self.classes)
		for c in self.classes:
			p += c.printClassInfo()
		return p