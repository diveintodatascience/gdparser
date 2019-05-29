import os
import csv
import time
import random
import re
import datetime

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

class GParser:
    def __init__(self, config):
        self._parseconfig(config)

        self.driver = webdriver.Chrome()
        self.joblinks = None
        #Maybe because of AB testing GD change apperiance of the page on differnet loads
        self.designtype = -1
        self.nomorejobs = False
        self.jobs_processed_num = 0
        self.jobs_list = []

    def run(self):
        #Prepare to run in loop.
        self.driver.get(self.searchurl)
        self.joblinks =  self.driver.find_elements_by_xpath("//article[@id='MainCol']/div/ul[@class='jlGrid hover']/li[@class='jl' or @class = 'jl selected']")
        self._closepopup()
        self._figuredesign()

        # while not self.nomorejobs:
        #
        #     self._parsepage()
        #     self._nextpage()
        #     self._check_the_end()

        for i in range(0, 32):
            self._parsepage()
            headers = ['num', 'position', 'company', 'location', 'date', 'time', 'relpath', 'href']
            self._writecsv(self.jobs_list, headers)
            #Clear temporary dict after saving data to file
            self.jobs_list.clear()
            self._nextpage()
            #We are soory but high load...so lets put 10 sec
            time.sleep(10)

        time.sleep(1000)
        self.driver.quit()

    def _writecsv(self, list_to_write, headerslist):

        path_to_file = os.path.join(self.csvpath, self.csvfilename)
        file_exist = False

        if os.path.isfile(path_to_file):
            file_exist = True
        if not os.path.isdir(self.csvpath):
            os.makedirs(self.csvpath)

        with open(path_to_file, mode='a', newline='') as csv_file:

            writer = csv.DictWriter(csv_file, fieldnames=headerslist, delimiter=self.csvsep)

            if not file_exist:
                writer.writeheader()

            for item in list_to_write:
                writer.writerow(item)

            csv_file.close()

        print("{} jobs saved to file".format(len(list_to_write)))

    def _writejobtofile(self, path, data):
        #check if file already exist
        if os.path.isfile(path):
            print("WARNING!!! already {} exists".format(path))
        elif not os.path.isdir(os.path.dirname(path)):
            print("Create directory: {}".format(os.path.dirname(path)))
            os.makedirs(os.path.dirname(path))
        with open(path,mode='a', newline='', encoding='utf-8') as file:
            file.write(data)
            file.close()

    def _savetodb(self):
        pass

    def _nextpage(self):
        nextbtn = self.driver.find_element_by_xpath("//li[@class='next']/a")
        nextbtn.click()
        time.sleep(2)

    def _check_the_end(self):
        try:
            element = self.driver.find_element_by_xpath(".//*[contains(text(), 'Sorry, we can')]")
            self.nomorejobs = True
            print("All jobs are processed")
        except NoSuchElementException:
            pass

    def _parsepage(self):
        #update joblinks
        self.joblinks = self.driver.find_elements_by_xpath("//article[@id='MainCol']/div/ul[@class='jlGrid hover']/li[@class='jl' or @class = 'jl selected']")
        job_links_number = len(self.joblinks)

        for i in range (0, job_links_number):
            selected_job_link = self.joblinks[i]
            selected_job_link.click()

            #Sleep for dealing with "element is not attached to page document"

            time.sleep(1)
            company = ''
            location = ''
            position = ''
            href = ''
            jobdescr = ''

            if self.designtype == 1:
                company = selected_job_link.find_element_by_xpath(".//div[@class='jobInfoItem jobEmpolyerName']").text
                location = selected_job_link.find_element_by_xpath(".//div[@class='jobInfoItem empLoc' or @class='jobInfoItem empLoc withAllLabels']/span").text
                hrefElement = selected_job_link.find_element_by_xpath(".//div[@class='jobContainer']/a")
                href = hrefElement.get_attribute('href')
                position = hrefElement.text
                jobdescr = self.driver.find_element_by_xpath("//div[@class = 'jobDescriptionContent desc']").get_attribute('innerHTML')

            elif self.designtype == 2:
                company = selected_job_link.find_element_by_xpath(".//div[@class='flexbox empLoc']/div").text
                location = selected_job_link.find_element_by_xpath(".//span[@class='subtle loc']").text
                company = re.sub(str(location), '', company)[:-2]
                hrefElement = selected_job_link.find_element_by_xpath(".//div[@class='titleContainer']/a")
                href = hrefElement.get_attribute('href')
                position = hrefElement.text
                jobdescr = selected_job_link.find_element_by_xpath("//div[@class = 'jobDescriptionContent desc']").get_attribute(
                    'innerHTML')

            self.jobs_processed_num += 1

            print("Job number {}".format(self.jobs_processed_num))
            print("Company: {} ".format(company))
            print("Location: {}".format(location))
            print("Link : {}".format(href))
            print("Position : {}".format(position))
            print()
            print('----------------------------------------------------------------------------------')
            print()

            #headers = ['num', 'position', 'company', 'location','date', 'time', 'relpath', 'href']

            ts = datetime.datetime.utcnow()
            date_ = ts.date()
            time_ = ts.time()

            file_path_from_root = os.path.join(self.name, str(date_), "{}.txt".format(self.jobs_processed_num) )

            self.jobs_list.append({
                'num': self.jobs_processed_num,
                'position': position,
                'company': company,
                'location': location,
                'date': str(date_),
                'time': str(time_),
                "relpath": str(file_path_from_root),
                'href': href
            })

            pattern = """<div>
<ul>
<li>number:   {}</li>
<li>company:  {}</li>
<li>position: {}</li>
<li>location: {}</li>
<li>date:     {}</li>
<li>time:     {}</li>
<li>relpath:  {}</li>
<li>href:     <a href = {}>link</a></li>
</ul>
</div>
<div>
{}
</div>
            """.format(self.jobs_processed_num, company, position, location, str(date_),
                       str(time_), str(file_path_from_root), href, jobdescr)



            #lets save our data to file

            self._writejobtofile(os.path.join(self.filepath, file_path_from_root), pattern)

            time.sleep(2)

    def _closepopup(self):
        #!!!!!! Turn off to start from different page
        self.joblinks[1].click()
        time.sleep(2)
        closeButton = self.driver.find_element_by_xpath("//div[@id='JAModal']//*[contains(@class,'Btn')]")
        closeButton.click()
        time.sleep(1)

    def _figuredesign(self):
        try:
            element = self.joblinks[0].find_element_by_xpath(".//div[@class='jobInfoItem jobEmpolyerName']")
            self.designtype = 1
            print("Design №1 found!")
        except NoSuchElementException:
            pass

        try:
            element = self.joblinks[0].find_element_by_xpath(".//div[@class='flexbox empLoc']")
            self.designtype = 2
            print("Design №2 found!")
        except NoSuchElementException:
            pass

    def _parseconfig(self, config):
        # ToDo check for correctness
        self.name = config['provider']['name']
        self.searchurl = config['provider']['searchurl']
        self.filepath = config['general']['filepath']
        self.csvpath = config['general']['csvpath']
        self.csvfilename = config['general']['csvfilename']
        self.csvsep = config['general']['csvsep']

    def printconfig(self):
        print("name: {}".format(self.name))
        print("searchurl: {}".format(self.searchurl))
        print("searchstring: {}".format(self.searchstring))

        print("usedb: {}".format(self.usedb))
        print("usecsv: {}".format(self.usecsv))
        print("roothpath: {}".format(self.filepath))
        print("csvpath: {}".format(self.csvpath))

        if self.usedb:
            print("databasename: {}".format(self.databasename))
            print("databaseuser: {}".format(self.databaseuser))
            print("databasepassword: {}".format(self.databasepassword))
            print("databasehost: {}".format(self.databasehost))
            print("databaseport: {}".format(self.databaseport))

        if self.usecsv:
            print("csvpath: {}".format(self.csvpath))
            print("delcsvifexist: {}".format(self.delcsvifexist))
            print("csvsep: {}".format(self.csvsep))
            print("csvfilename: {}".format(self.csvfilename))
