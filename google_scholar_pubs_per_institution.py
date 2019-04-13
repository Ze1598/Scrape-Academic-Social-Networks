'''
File to scrape the total number of documents published by the authors
affiliated to each of Instituto Politécnico do Porto's (IPP) schools, through
Google Scholar.

This script is by no means an API to Google Scholar, since it was specifically
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


# Credit for this class goes to https://stackoverflow.com/a/35536565
class wait_for_more_than_n_elements (object):
	'''
	This class is responsible for making the profile page wait to load
	a user's publications after clicking the "SHOW MORE" button,
	before running any more code.
	'''
	def __init__(self, locator, count):
		self.locator = locator
		self.count = count

	# Overload the `call()` method so that it makes the script wait for the\
	# page to load all remaining publications or, in other words, until\
	# there are more publications loaded than there were before clicking\
	# the "SHOW MORE" button
	def __call__(self, driver):
		try:
			count = len(EC._find_elements(driver, self.locator))
			return count > self.count
		except StaleElementReferenceException:
			return False


def get_author_pubs (target_url):
	'''
	Extracts the number of publications found in a single user profile.

	Parameters
	----------
	target_url : str
		The URL of the profile from which we'll extract the number of
		published documents.

	Returns
	-------
	pubs : int
		The number of published documents by the present author.
	'''

	# We'll use Google Chrome
	driver = webdriver.Chrome()
	# Make the driver wait 10 seconds
	driver.implicitly_wait(10)
	# Open the target URL
	driver.get(target_url)
	# Find the "SHOW MORE" button by its id
	elem = driver.find_element_by_id("gsc_bpf_more")
	# If the author has less than 21 publications, try to extract the exact\
	# number; if it raises any exception, assume the author has 0 publications
	try:
		pubs = int(driver.find_element_by_id("gsc_a_nn").text.split("–")[-1])
	except:
		pubs = 0

	# Click the button while it is not disabled, that is, load more publications\
	# while it is possible
	while driver.find_element_by_id("gsc_bpf_more").get_attribute("disabled") == None:
		# Create an object to make the driver wait 10 seconds
		wait = WebDriverWait(driver, 10)
		# Wait 3 seconds until the button is clickable
		elem = wait.until( EC.element_to_be_clickable((By.ID, "gsc_bpf_more")) )
		# Click the button (load more publications)
		elem.click()
		# Get the number of currently shown publications
		pubs = int(driver.find_element_by_id("gsc_a_nn").text.split("–")[-1])
		# Click the "SHOW MORE" button only after all the publications have\
		# loaded since the previous click
		wait = WebDriverWait(driver, 10)
		wait.until(wait_for_more_than_n_elements((By.CLASS_NAME, "gsc_a_tr"), pubs) )

	if pubs > 20:
		# Wait for the page to finish loading the last batch of publications
		wait = WebDriverWait(driver, 10)
		wait.until(wait_for_more_than_n_elements((By.CLASS_NAME, "gsc_a_tr"), pubs) )
		# To get the total number of publications, just extract the number from the\
		# <span> element at the end of the page, next to the now disabled "SHOW MORE"\
		# button
		pubs = int(driver.find_element_by_id("gsc_a_nn").text.split("–")[-1])
	# Close the currently open browser window (the driver)
	driver.quit()

	return pubs



def get_page_profiles (target_url):
	'''
	Return a list with the URLs for each user profile in the current
	page of results.

	Parameters
	----------
	target_url : str
		The URL of the page from which will be extracted profile URLs.

	Returns
	-------
	profiles_list : list
		A list of URLs, that is, of strings, for the profiles of authors.
	'''

	# List to contain the scraped profile URLs
	profiles_list = []
	# Each profile URL starts with this
	base_url = "https://scholar.google.pt/citations?hl=en&user="
	# We'll use Google Chrome
	driver = webdriver.Chrome()
	# Make the driver wait 10 seconds
	driver.implicitly_wait(10)
	# Open the target URL
	driver.get(target_url)
	# Find the "SHOW MORE" button by its id
	elem = driver.find_element_by_id("gsc_sa_ccl")
	# Loop through the results in the page and extract the desired URLs
	for profile in elem.find_elements_by_class_name("gsc_1usr"):
		# Extract the profile's ID and suffix it to the base URL to\
		# create the full profile URL
		profile_url = base_url + profile.find_element_by_class_name("gs_ai_pho").get_attribute("href").split("=")[-1]
		# Add the profile URL to the list
		profiles_list.append(profile_url)

	# Close the currently open browser window (the driver)
	driver.quit()

	return profiles_list



def get_next_page_url (target_url):
	'''
	Get the URL for the next page of profile results.

	Parameters
	----------
	target_url : str
		The URL of the page from which will be extracted the URL for the
		next page; the URL of the current page

	Returns
	-------
	return_url : str
		The URL for the next page. If the current page was the last one,
		just return `None` instead.
	'''

	# This the base of the URL for the next page of results. What is\
	# scraped is suffixed to this
	base_url = "https://scholar.google.pt"
	# We'll use Google Chrome
	driver = webdriver.Chrome()
	# Make the driver wait 10 seconds
	driver.implicitly_wait(10)
	# Open the target URL
	driver.get(target_url)
	# Find the "SHOW MORE" button by its id
	# elem = driver.find_element(By.CLASS_NAME("gs_btnPR gs_in_ib gs_btn_half gs_btn_lsb gs_btn_srt gsc_pgn_pnx"))
	elem = driver.find_elements_by_tag_name("button")[-1]
	# try/except clause in case the page doesn't have buttons at all
	try:
		# Find the last <button> and extract the desired URL
		if elem.get_attribute("disabled") == None:
			next_url = elem.get_attribute("onclick")[17:-1].replace("\\x3d", "=").replace("\\x26", "&")
			return_url = base_url + next_url
		# If the button is disabled, there's no next URL
		else:
			return_url = None
	except:
		return_url = None

	# Close the currently open browser window (the driver)
	driver.quit()

	return return_url

def get_citations (profile):
	'''
	Get the number of citations for a single user profile.

	Parameters
	----------
	profile : str
		The URL for the user profile.

	Returns
	-------
	citations : int
		The citations for the target user.
	'''

	# We'll use Google Chrome
	driver = webdriver.Chrome()
	# Make the driver wait 10 seconds
	driver.implicitly_wait(10)
	# Open the target URL
	driver.get(profile)

	try:
		citations = int(driver.find_elements_by_class_name("gsc_rsb_std")[0].text.strip())
	except:
		# If we couldn't scrape the citations, assume it's zero
		citations = 0

	driver.quit()

	return citations


# The following code is run only if this file itself is being executed\
# instead of imported by another file
if __name__ == "__main__":
	# The schools (institutions) to search for
	schools = ["isep.ipp", "iscap.ipp", "ese.ipp", "esmae.ipp", "estg.ipp", "ess.ipp", "esht.ipp", "esmad.ipp"]
	# Holds key-value pairs of the type school-number_of_published_documents
	results = {}
	school_citations = {}
	# String to be written into a text file with the published documents\
	# per school
	write_string = ""
	# String to be written into a text file with the citations per school
	write_string_citations = ""
	
	# Find the number of published documents by each school
	for school in schools:
		# Create the school name/dictionary key
		school_name = school.split(".")[0].upper()
		# Add the key-value pair to the dictionary
		results[school_name] = 0
		school_citations[school_name] = 0

		# The current page is, at first, the first page of results for the\
		# current school
		curr_page = f"https://scholar.google.pt/citations?view_op=search_authors&hl=en&mauthors={school}"

		# While we haven't reached the end, extract the number of publications\
		# of each author in the current page and add it to the running sum in\
		# the respective school's dictionary key
		while curr_page != None:
			# Get a list with the URLs for each profile in the page
			page_profiles = get_page_profiles(curr_page)

			# Loop through the author pages to extract the number of published\
			# documents (update the running sum)
			for author_profile in page_profiles:
				pubs = get_author_pubs(author_profile)
				results[school_name] += pubs
				cites = get_citations(author_profile)
				school_citations[school_name] += cites
				print(school_citations[school_name])

			# The current page is now the next page (call this function to get\
			# the URL for said page)
			curr_page = get_next_page_url(curr_page)

		# print(f"{school_name}'s authors have {results[school_name]} publications.")
		print(f"{school_name}'s authors have {school_citations[school_name]} citations.")

		# Update the string to be written to a text file
		# write_string += f"{school_name}: {results[school_name]} publications\n"
		write_string_citations += f"{school_name}: {school_citations[school_name]} citations\n"


	# Write the string to a new text file
	with open("GS_docs_escola.txt", "w") as f:
		f.write(write_string)
	print(results)

	with open("GS_citations.txt", "w") as f:
		f.write(write_string_citations)