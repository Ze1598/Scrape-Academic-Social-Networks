'''
File to scrape the total number of document reads and member citations of
each school of Instituto Politécnico do Porto's (IPP) schools, through
ResearchGate.

This script is by no means an API to ResearchGate, since it was specifically
created to scrape information about authors affiliated to schools of IPP.
But, if that's also your intention, then I hope this file helps you as there's
no API for the platform.

Due note that, because this file relies on a Google Chrome driver, you need to
specify the path where it's located.
For my case, executing the driver once and having it in the same folder as this
file was enough to run the script successfully afterwards.

Note: you need to have a Python file called `researchGate_id.py` in the same
directory as this script with two string variables `user` and `password` so
that they can be imported and you can be logged into ResearchGate.
'''


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
import pickle
import io
# Python file with the credentials for our ResearchGate account
import researchGate_id


def get_profiles (source):
	'''
	Scrape the URLs of the user profiles for a given ResearchGate
	institution.

	Parameters
	----------
	source : str
		A string with the URL for the institution.

	Returns
	-------
	user_urls : list
		A list with the scraped profile URLs. The list will be empty
		if the the given institution URL (`source`) did not contain
		a valid URL.
	'''

	# List to hold the profile URLs
	user_urls = []

	# If we passed a string with a valid URL, scrape data
	if source != "":
		# We'll use Google Chrome
		driver = webdriver.Chrome()
		# Make the driver wait 10 seconds when needed
		driver.implicitly_wait(10)
		# Log into an account
		# Log in page
		driver.get("https://www.researchgate.net/login")
		# Type the user and password
		driver.find_element_by_id("input-login").send_keys(username)
		driver.find_element_by_id("input-password").send_keys(password)
		# Actually log in
		driver.find_element_by_class_name("nova-c-button__label").find_element(By.XPATH, "./..").click()

		# We'll start at the URL given as input to the function call
		curr_page = source
		# Make the driver wait 10 seconds
		driver.implicitly_wait(10)
		# Get the actual first page of results (the string with the URL\
		# passed to the function call initially)
		driver.get(curr_page)

		# Base URL for a profile page (we'll scrape the id of the profile\
		# to be appended to this)
		user_base_url = "https://www.researchgate.net/profile/"

		# Find the number of result pages available
		try:
			last_page = int(driver.find_elements_by_class_name("navi-page-link")[-1].text.strip())
		except:
			last_page = 1

		# Number of the current page of results (start at page 1)
		page_num = 1

		# Run the loop until we scrape the last page of results
		while page_num <= last_page:

			# Get the HTML with the list of user profiles in the current page
			users = driver.find_elements_by_tag_name("li")
			# We are only interested in the HTML elements that are actually\
			# about user profiles, so filter them by the element's class\
			# values
			users = [user for user in users if "people-item" in user.get_attribute("class")]

			# Extract the user profile URLs from the scraped HTML elements
			for user in users:
				# The profile id is the value of the following property
				user_id = user.get_attribute("data-account-key")
				# A user profile URL is the concatenation of the base url\
				# with the scraped id
				user_urls.append(user_base_url + user_id)

			# Move to the next page (increment the `page` argument of the URL)
			page_num += 1
			curr_page = curr_page.split("=")[0] + "=" + str(page_num)
			# Make the driver wait 10 seconds
			driver.implicitly_wait(10)
			# Open the new page
			driver.get(curr_page)

		# When the loop finishes, close the driver
		driver.quit()

		# Print the number of scraped profiles
		# print("Number of profiles scraped:", len(user_urls))

		# Return the list with the scraped user profiles URLs
		return user_urls

	# If the passed string is not a valid URL, return an empty list
	else:
		return user_urls



def get_school_reads_citations (profiles_list):
	'''
	Scrape the totals for two variables about the members of a given school:
	how many times their publications were read and how many the members have
	been cited.

	Parameters
	----------
	profiles_list : list
		A list of URLs for the profiles of all the members of a single school.

	Returns
	-------
	(total_reads, total_citations) : tuple
		A tuple for the totals of a single school: total reads of documents
		and total citations of its members.
	'''

	# We'll use Google Chrome
	driver = webdriver.Chrome()
	# Make the driver wait 10 seconds when needed
	driver.implicitly_wait(10)
	# Log into an account
	# Log in page
	driver.get("https://www.researchgate.net/login")
	# Type the user and password
	driver.find_element_by_id("input-login").send_keys(username)
	driver.find_element_by_id("input-password").send_keys(password)
	# Actually log in
	driver.find_element_by_class_name("nova-c-button__label").find_element(By.XPATH, "./..").click()

	# Make the driver wait 10 seconds
	driver.implicitly_wait(10)

	# Running sums of the reads and citations
	total_reads = 0
	total_citations = 0

	# Scrape information from each profile of the input list
	for profile in profiles_list:
		# Go to that profile
		driver.get(profile)

		# The try/except work mainly as follows: if the reads and\
		# citations information is available in the profile, then scrape\
		# it; otherwise ignore the profile and move on. However, sometimes\
		# the source code of ResearchGate changes and thus the information\
		# can be found in different elements: hence the nested `try` clause\
		# to try to scrape both cases before ignoring the current profile
		try:
			profile_reads = int(driver.find_element(By.XPATH, '//*[@id="about"]/div/div/div[2]/div/div/div[2]/div[1]').text.strip())
			profile_citations = int(driver.find_element(By.XPATH, '//*[@id="about"]/div/div/div[2]/div/div/div[3]/div[1]').text.strip())
			total_reads += profile_reads
			total_citations += profile_citations

		except:
			# If the first possible HTML elements were not found, try the\
			# second ones; if they are also not found, ignore this profile\
			# and move on
			try:
				profile_reads = int(driver.find_elements_by_class_name("application-box-layout__item")[3].\
					find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("div").\
					find_element_by_tag_name("div").find_element_by_tag_name("div").text.strip())
				profile_citations = int(driver.find_elements_by_class_name("application-box-layout__item")[1].\
					find_element_by_tag_name("div").find_element_by_tag_name("div").find_element_by_tag_name("div").\
					find_element_by_tag_name("div").find_element_by_tag_name("div").text.strip())
				total_reads += profile_reads
				total_citations += profile_citations
			
			except:
				pass

		print(total_reads, total_citations)

	# Close the browser window
	driver.quit()

	return (total_reads, total_citations)



if __name__ == "__main__":
	# Import our account's credentials from a Python file in the same\
	# directory
	username = researchGate_id.user
	password = researchGate_id.password

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
		"https://www.researchgate.net/institution/Instituto_Superior_de_Engenharia_do_Porto/members?page=1",
		"https://www.researchgate.net/institution/Instituto_Superior_de_Contabilidade_e_Administracao_do_Porto/members?page=1",
		"",
		"https://www.researchgate.net/institution/Polytechnic_Institute_of_Porto/department/Escola_Superior_de_Musica_e_das_Artes_do_Espetaculo/members?page=1",
		"https://www.researchgate.net/institution/Polytechnic_Institute_of_Porto/department/Escola_Superior_de_Tecnologia_e_Gestao_de_Felgueiras/members?page=1",
		"https://www.researchgate.net/institution/Polytechnic_Institute_of_Porto/department/Escola_Superior_de_Tecnologia_da_Saude_do_Porto/members?page=1",
		"",
		""
	]

	# List to hold lists of profiles for each school
	school_urls = []

	# Counter to keep track of which school we are looking at (by using the\
	# index of the `schools` list)
	counter = 0
	# Create a dictionary of the type `school: list_of_profiles` (this\
	# dictionary will be written to the first .pickle file)
	scraped_data = {school: [] for school in schools}
	
	# Loop through the schools' pages and scrape the URLs for the profiles\
	# of their members
	for school_page in school_pages:
		# Scrape profiles for the current school
		user_profiles = get_profiles(school_page)
		# Add the newly-scraped profiles to the list of scraped data
		school_urls.append(user_profiles)
		print(schools[counter], "has", len(user_profiles), "members.")
		# Update the dictionary with the list of profiles for the current\
		# school
		scraped_data[schools[counter]] = user_profiles
		# Increment the counter since we are moving to the next school
		counter += 1

	# Write the dictionary of schools and profiles to a new .pickle file
	with open("scraped_profiles.pickle", "wb") as f:
		pickle.dump(scraped_data, f, pickle.HIGHEST_PROTOCOL)

	# Load the dictionary of profiles from the created .pickle file (this\
	# block is unnecessary if the whole script is run at once, but in our\
	# use case that's not how it hapenned)
	with open('scraped_profiles.pickle', 'rb') as f:
		scraped_profiles = pickle.load(f)

	# Create dictionaries of the type `school: total_reads` and\
	# `school: total_citations`
	total_reads = {school: 0 for school in schools}
	total_citations = {school: 0 for school in schools}

	# Create another counter to keep track of which school we are\
	# currently scraping
	counter = 0
	# Single string to contain the schools and their reads and citations\
	# This string will be built as the information is scraped and will be\
	# written to a new .txt file
	write_string = ""

	# Loop through the schools (their members' profiles) and scrape the\
	# required information
	for school in schools:
		# Get the total reads and citations for a single school
		scraped_reads_citations = get_school_reads_citations(scraped_profiles[school])
		# Save the total reads in the proper dictionary
		total_reads[schools[counter]] += scraped_reads_citations[0]
		# Save the total citations in the proper dictionary
		total_citations[schools[counter]] += scraped_reads_citations[1]
		# Phrases with the scraped information which will be included in the\
		# created .txt file
		reads_write = schools[counter] + "'s documents have " + str(total_reads[schools[counter]]) + " reads.\n"
		citations_write = schools[counter] + "'s researchers have " + str(total_citations[schools[counter]]) + " citations.\n\n"
		write_string += reads_write
		write_string += citations_write
		print(reads_write)
		print(citations_write)
		counter += 1

	# Update the .pickle file with the newly-scraped information\
	# (dictionaries)
	with open("scraped_reads_citations.pickle", "wb") as f:
		pickle.dump(total_reads, f, pickle.HIGHEST_PROTOCOL)
		pickle.dump(total_citations, f, pickle.HIGHEST_PROTOCOL)

	# Finally, write the scraped information to the new .txt file
	with open("RG_reads_citations.txt", "w") as f:
		f.write(write_string)