'''
File to scrape the total number of document reads and profile views of the
members of a given institution of each of Instituto Politécnico do Porto's
(IPP) schools, through Academia.edu.

This script is by no means an API to Academia.edu, since it was specifically
created to scrape information about authors affiliated to schools of IPP.
But, if that's also your intention, then I hope this file helps you as there's
no API for the platform.

Due note that, because this file relies on a Google Chrome driver, you need to
specify the path where it's located.
For my case, executing the driver once and having it in the same folder as this
file was enough to run the script successfully afterwards.
'''

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
import time # time.sleep() will be useful when waiting for a page to load
import pickle
import io


def get_docs_profiles_pages (school):
	'''
	Get all the (first) pages of documents and of members' profiles for
	a single school (that has its own institutional page).

	Parameters
	----------
	school : str
		The URL for the page of the school.

	Returns
	-------
	(docs_pages, profiles_pages) : tuple
		Tuple of lists: one for the pages of documents and another for the
		members of the departments.
	'''
	
	# Go to the page of the school
	driver.get(school)

	# List to hold the scraped URLs for the documents and profiles
	docs_pages = []
	profiles_pages = []

	# Find all the spans with information
	target_spans = driver.find_elements_by_class_name("u-fs12")[:-1]
	# Loop through the found <span>s to extract the desired URLs
	for elem in target_spans:
		# We want information from inner <a>nchors
		inner_anchors = elem.find_elements_by_tag_name("a")
		# If the department has a has link to members and documents
		if len(inner_anchors) == 2:
			profiles_pages.append(inner_anchors[0].get_attribute("href"))
			docs_pages.append(inner_anchors[1].get_attribute("href"))
		# If the department has only a link to its members
		elif len(inner_anchors) == 1:
			profiles_pages.append(inner_anchors[0].get_attribute("href"))

	# Return a tuple of lists: one for the pages of documents and another\
	# for the members of the departments
	return (docs_pages, profiles_pages)



def count_views (dept_page):
	'''
	Scrape the views from the list of members of a single department.
	In cases where a school's page is actually a department, this function
	is used as well.

	Parameters
	----------
	dept_page : str
		The URL for the first page of members of the target department.

	Returns
	-------
	tuple
		`(total_views, next_link)` if the last page of results was scraped,
		otherwise, return a tuple with only the total profile views for the
		members of the target department.
	'''

	driver.get(dept_page)

	# Running sum of the profile views scraped
	total_views = 0
	# Number of the current page of results
	if "?page=" not in dept_page:
		page_number = 1
	else:
		page_number = int(dept_page.split("=")[1]) + 1

	member_containers = driver.find_elements_by_class_name("container-fluid")

	# Run the loop while there's pages of members to scrape
	while True:

		# Loop through the relevant elements found to scrape the required\
		# information
		for container in member_containers:
			# Target element
			info_span = int(container.find_elements_by_class_name("u-ml0x")[1].\
				text.split()[3].strip().replace(",", ""))
			# Update the running sum with the scraped views
			total_views += info_span

		# Try to move to the next page of results
		try:
			# We are moving to the next page of results
			page_number += 1
			# If no element with this class can be found, then we are at the\
			# last page of results
			next_page = driver.find_element_by_class_name("next_page")
			next_link = dept_page.split("?")[0]+"?page="+str(page_number) 
			# If the element was found, navigate to the next page
			driver.get(next_link)
			# If there's at least one more page of members to scrape, return\
			# the scraped views for the current page, as well as the URL for\
			# the next page of members
			return (total_views, next_link)

		# If this was the last page, then break the loop because there's\
		# nothing more to scrape
		except:
			break

	# Otherwise, if this was the last page of results, return just the\
	# scraped profile views
	return (total_views,)



def count_reads (docs_page):
	'''
	Scrape the total number of document reads for a single department,
	given the first page of documents available.

	Parameters
	----------
	docs_page : str
		The URL of the first page of publications for a target department.

	Returns
	-------
	total_reads : int
		The total number of times the publications associated to the target
		department have been read.
	'''

	driver.get(docs_page)

	# Time to wait for the page to load every time new content is\
	# dynamically loaded (in seconds)
	scroll_pause_time = 0.5

	# Get scroll height
	last_height = driver.execute_script("return document.body.scrollHeight")

	# Running sum of scraped document views
	total_reads = 0
	# Number of the current page of results
	page_number = 1

	# Run this outer loop while we there are pages of documents to be scraped
	while True:

		# https://stackoverflow.com/a/28928684/1316860
		# ---------------------------------------------------------------------------
		# Loop until the current page is completely loaded
		while True:
			# Scroll down to bottom
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

			# Wait to load page
			time.sleep(scroll_pause_time)

			# Calculate new scroll height and compare with last scroll height
			new_height = driver.execute_script("return document.body.scrollHeight")
			# If the page's height didn't change since last iteration, then\
			# there's nothing more to load in this page
			if new_height == last_height:
				break
			# Current height of the page
			last_height = new_height
		# ---------------------------------------------------------------------------

		# Scrape the available document views
		views_elems = driver.find_elements_by_class_name("js-view-count")
		# Loop through the scraped elements to get the actual document\
		# views/reads
		for elem in views_elems:
			# Update the running sum with the scraped values
			total_reads += int(elem.text.strip().split()[0].replace(",", ""))
		
		# Try to move to the next page of results
		try:
			# We are moving to the next page of results
			page_number += 1
			# If no element with this class can be found, then we are at the\
			# last page of results
			next_page = driver.find_element_by_class_name("next_page")
			# If the element was found, navigate to the next page
			driver.get(docs_page+"?page="+str(page_number))
		
		# If this was the last page, then break the loop because there's\
		# nothing more to scrape
		except:
			break


	return total_reads



if __name__ == "__main__":
	# List with the names of the schools
	schools = [
		"ISEP",
		"ISCAP",
		"ESE",
		"ESMAE",
		"ESTG",
		"ESS",
		"ESHT",
		"ESMAD"
	]

	# URLs from where we'll extract the profiles for each school. If a school\
	# has an empty string, it means that school is not present in ResearchGate
	school_pages = [
		"http://cityoffuture.academia.edu/",
		"http://iscap.academia.edu/",
		"https://ipp.academia.edu/Departments/Escola_Superior_de_Educa%C3%A7%C3%A3o_do_Porto",
		"http://esmae-ipp.academia.edu/",
		[
			"https://ipp.academia.edu/Departments/Escola_superior_de_Tecnologia_e_Gest%C3%A3o_de_Felgueiras",
			"http://ipp.academia.edu/Departments/School_of_Management_and_Technology_of_Felgueiras",
			"https://ipp.academia.edu/Departments/School_of_Technology_and_Management_of_Felgueiras"
		],
		[
			"https://ipp.academia.edu/Departments/Escola_Superior_de_Sa%C3%BAde_do_Porto",
			"https://ipp.academia.edu/Departments/Escola_Superior_de_Tecnologia_da_Sa%C3%BAde_do_Porto",
			"https://ipp.academia.edu/Departments/School_of_Health_Technologies"
		],
		"http://ipp.academia.edu/Departments/Escola_Superior_de_Hotelaria_e_Turismo",
		"https://ipp.academia.edu/Departments/Escola_Superior_de_Media_Artes_e_Design"
	]

	# We'll use Google Chrome
	driver = webdriver.Chrome()
	# Make the driver wait 10 seconds when needed
	driver.implicitly_wait(10)


	# Counter to keep track of which school we are looking at (by using the\
	# index of the `schools` list)
	counter = 0
	# Final dictionaries with the total sum of document reads and profile\
	# views for each school, respectively
	reads_count = {school:0 for school in schools}
	views_count = {school:0 for school in schools}
	# String to be written to a .txt file with the scraped results
	write_string = ""
	# All the first pages of publications for the departments of each\
	# school (list of lists where the inner lists represent a single\
	# school)
	all_docs = []
	# All the first pages of members for the departments of each\
	# school (list of lists where the inner lists represent a single\
	# school)
	all_members = []

	# Loop through the schools to scrape their pages of publications for\
	# their departments as well as for their members
	for school_page in school_pages:

		# If the school doesn't have a single institutional page, then it\
		# probably has multiple pages as departments. In those cases\
		# we'll need less work

		# When schools have their own institutional pages
		if type(school_page) != list:
			if "ipp.academia.edu" in school_page:
				docs_page, members_page = page+"/Documents", page
			else:
				docs_page, members_page = get_docs_profiles_pages(school_page)

		# When they don't
		else:
			docs_page = []
			members_page = []
			for page in school_page:
				# docs_page, members_page = page+"/Documents", page
				docs_page.append(page+"/Documents")
				members_page.append(page)

	# This block would be used if the script was executed in parts and\
	# we had beforehand a .pickle file with the document and member\
	# pages
	# with open("scraped_profiles.pickle", "rb") as f:
		# docs = pickle.load(f)
		# members = pickle.load(f)

	# Loop through each school once again, but this time to scrape the\
	# total counts for publication reads and profile views for the\
	# scraped URLs
	for school_page in school_pages:

		# Scrape the publication reads
		for page in docs_page:
		# for page in docs[counter]:
			reads_count[schools[counter]] += count_reads(page)

		# Scrape the profile views
		for page in members_page:
		# for page in members[counter]:
			final_views = 0
			# Stupid little trick because it wasn't possible to scrape all\
			# pages of members with a single function call. Instead, as\
			# long as the function call is used to scrape any other page\
			# that is not the last page of members, return the total views\
			# scraped for that page as well as the URL for the next page;\
			# when the last page is scraped, return just the scraped views
			while True:
				temp_result = count_views(page)
				# If two-item tuple was returned, update the total views\
				# and the target page for the next function call
				if len(temp_result) == 2:
					final_views += temp_result[0]
					page = temp_result[1]
				# Otherwise, just update the total views and break the loop\
				# because we have finally finished scraping the current\
				# department
				else:
					final_views += temp_result[0]
					break
			# Update the total views for the current school with the views\
			# scraped for the current department
			views_count[schools[counter]] += final_views

		# Create phrases for the scraped information and add it to the string\
		# which will be written to the .txt file
		write_string += schools[counter] + "'s documents have been read " +\
			str(reads_count[schools[counter]]) + " times.\n"
		write_string += schools[counter] + "'s members' profiles have been visited " +\
			str(views_count[schools[counter]]) + " times.\n\n"

		# Increment the counter since we are moving to the next school
		counter += 1
		# Create a nested list with all the first pages of publications and\
		# members for each department of a single school
		all_docs.append(docs_page)
		all_members.append(members_page)

	# Quit/exit the driver
	driver.quit()

	# We can execute the following block to create a single .pickle\
	# file with all the document and member scraped pages
	# Write the dictionary of schools and profiles to a new .pickle file
	with open("scraped_profiles.pickle", "wb") as f:
		pickle.dump(all_docs, f, pickle.HIGHEST_PROTOCOL)
		pickle.dump(all_members, f, pickle.HIGHEST_PROTOCOL)

	# Finally, write the scraped information to a .txt file
	with open("acadEdu_reads_views.txt", "w") as f:
		f.write(write_string)