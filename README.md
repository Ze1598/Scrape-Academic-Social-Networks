# Scrape-Academic-Social-Networks

For a college project, me and a classmate had to find out how many documents the authors of each school from Instituto Politécnico do Porto (IPP) had published in academic social networks, specifically Google Scholar, ResearchGate and Academia.edu. Unfortunately, there's still no API support for none of them, and so I had to scrape this information with Python and Selenium.

These scripts are by no means API to the platforms, since they were tailored to our need, but I think these scripts offer a solid base for someone looking to start a project like that.

Due note that, because these scripts (Selenium) rely on a Google Chrome driver, you need to specify the path where it's located. For my case, executing the driver once and having it in the same folder as the scripts was enough to run the script successfully afterwards.

The code will probably be a bit messy as I was more worried about getting the results than making the code readable and/or maintainable in the long run, but I feel it's still clear enough as I wrote docstrings for every function and wrote comments for everything.

External sources:

* Selenium: https://www.seleniumhq.org/

* Google Chrome's driver download: https://chromedriver.storage.googleapis.com/index.html?path=73.0.3683.68/

* Google Scholar: https://scholar.google.com/

* ResearchGate: https://www.researchgate.net/

* Academia.edu: https://www.academia.edu/