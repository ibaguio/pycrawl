#!/usr/bin/env python
from HTMLParser import HTMLParser
from dataModels import *
import sys

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

class CourseParser(HTMLParser):
	"""Class used to parse subpage from list of courses from the departments page"""

	#CUSTOM FUNCTIONS
	#set verbose to True in debugging mode
	def customInit(self,dept,verbose_=False):
		global f,verbose
		self.dept = dept
		self.courses = []
		self.waitingFor = -1
		self.next = 0
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
		global f
		if verbose:
			f.write('\n'+"OPEN TAG: "+tag)
		
		for attr in attrs:
			#colspan is the marker that it is a new Course
			if attr[0] == "colspan" and attr[1] == "3":
				#set marker to 1 and wait for the course name to be parsed
				self.waitingFor = 1
				if verbose:
					f.write('\n'+"Waiting for New Course")

			#size is the marker for course info
			elif attr[0] == "size" and attr[1] == "-1":
				#set marker to the next details to be parsed
				self.waitingFor = self.next
				if verbose:
					f.write('\n'+ "WAITING FOR: "+code[self.waitingFor])

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
		#expects a new Course
		if verbose:
			f.write('\n'+"DATA:"+data)
		if self.waitingFor == 1:
			data = data.split()						#splits the data to list of words
			cname = str(" ".join(data[2:]))			#course name: 3rd word till last word
			cnum = str(data[1])						#course num: 2nd word
			self.courses.append(Course(self.dept,cname,cnum))	#append a new Course to list
			self.waitingFor= -1 							#set marker to -1, waiting for nothing
			self.next = 2 								#set next to 2, telling the parser that the next
													#data to read is the class number
		elif self.waitingFor == 2:
			classNumber = data 						#sets the classnumber
			self.courses[-1].addClass(Class(classNumber)) 	#adds a new class to the last course
			self.waitingFor= -1
			self.next = 3 								#next data to read is the class link
		elif self.waitingFor == 3:
			self.waitingFor = 5							#do not store link, do nothing
		elif self.waitingFor == 4:						#ignore coursecode, we already have this info
			pass
		elif self.waitingFor == 5:
			try: 
				section = data.split()[2]			#get the section
			except IndexError:
				print "Index error! Will QUIT!\nData:",data
				if verbose:
					f.write('\n'+"Index error! Will QUIT!\nData: "+data)
				sys.exit()
			self.courses[-1].getLastClass().setSection(section)	#set the section of the last class of the last course
			self.waitingFor = -1
			self.next = 6 								#next data to read is schedule
		elif self.waitingFor == 6:
			sched = " ".join(data.split()[2:]) 		#reformat the string of schedule
			self.courses[-1].getLastClass().setSchedule(sched)
			self.waitingFor = -1
			self.next = 2
