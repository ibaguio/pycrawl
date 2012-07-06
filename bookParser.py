#!/usr/bin/env python
from HTMLParser import HTMLParser
from dataModels import *

#last_tag
#  code		desc
#	1		author
#	2		edition
#	3		publisher
#	4		isbn

class BookParser(HTMLParser):
	"""Parses an html code snippet which contains info about the book
	   Assumes that title has already been parsed beforehand"""

	#CUSTOM FUNCTIONS

	#custom init function
	def customInit(self,title,verbose_=False):
		self.book = Book(title)
		self.verbose = verbose_
		self.last_tag = -1
		self.wait = False		#waiting for a book info
		self.prompt("New Book",title)

	#returns the found book
	def getBook(self):
		return self.book

	#checks if verbose is true and prints the output if it is
	def prompt(self,*msg):
		if self.verbose:
			for m in msg:
				print m,
			print "\n"

	#handles html start tags
	def handle_starttag(self,tag,attrs):
		self.prompt("TAG:",tag)
		if tag == "ul":
			pass
		elif tag=="span":
			self.wait = False

	#handles html end tags
	def handle_endtag(self,tag):
		self.prompt("ENDTAG:",tag)

	#handles html data tag
	def handle_data(self,data):
		#not waiting for a book info, expect a book info category
		if not self.wait:
			if "author" in data.lower():
				self.last_tag = 1
			elif "edition" in data.lower():
				self.last_tag = 2
			elif "publisher" in data.lower():
				self.last_tag = 3
			elif "isbn" in data.lower():
				self.last_tag = 4
			else:
				self.last_tag = -1
			self.wait = True
		else:
			if self.last_tag == 1:
				self.book.setAuthor(data.split()[0])
			elif self.last_tag == 2:
				self.book.setEdition(data)
			elif self.last_tag == 3:
				self.book.setPublisher(data)
			elif self.last_tag == 4:
				self.book.setISBN(data.split()[0])

		self.prompt("DATA:",data)
		self.prompt("Last tag:",self.last_tag)