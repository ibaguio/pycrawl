def write_course_headers(sheet):
	sheet.write(0, 0, 'class_ #')
	sheet.write(0, 1, 'Course')
	sheet.write(0, 2, 'Section')
	sheet.write(0, 3, 'Schedule')
	sheet.write(0, 4, 'Books')
	sheet.write(0, 5, 'Dept.')

	sheet.col(0).width = 3500
	sheet.col(1).width = 5000
	sheet.col(2).width = 5000
	sheet.col(3).width = 5500
	sheet.col(4).width = 20000
	sheet.col(5).width = 3500

def write_book_headers(sheet):
	sheet.write(0, 0, 'Title')
	sheet.write(0, 1, 'Author')
	sheet.write(0, 2, 'Edition')
	sheet.write(0, 3, 'Publisher')
	sheet.write(0, 4, 'ISBN')

	sheet.col(0).width = 10000
	sheet.col(1).width = 7000
	sheet.col(2).width = 5000
	sheet.col(3).width = 7000
	sheet.col(4).width = 5500

def write_class_data(row, col, course,  class_, book_list, sheet):
	col = 0
	sheet.write(row, col, class_.classNumber) #write class_ number
	course_name = "%s %s" % (course.department, course.courseNumber)
	sheet.write(row, col+1, course_name) #write course name and course number
	sheet.write(row, col+2, class_.section)
	sheet.write(row, col+3, class_.schedule)
	sheet.write(row, col+4, get_book_titles(book_list))
	sheet.write(row, col+5, course.department)

def write_book_data(row, col, book, sheet):
	col = 0
	sheet.write(row, col, book.title) #write class_ number
	sheet.write(row, col+1, book.author) #write course name and course number
	sheet.write(row, col+2, book.edition)
	sheet.write(row, col+3, book.publisher)
	sheet.write(row, col+4, book.isbn)

def get_book_titles(book_list):
	titles = ""
	arr_len = len(book_list)
	for x in range(0, arr_len):
		titles += "\"%s\"" %(book_list[x].title)
		if x + 1 != arr_len:
			titles += "; "

	return titles