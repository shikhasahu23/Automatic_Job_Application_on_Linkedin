from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import json
import time
import re



class EasyApplyLinkedin:

    def __init__(self, data):

        self.email = data['email']
        self.password = data['password']
        self.keywords = data['keywords']
        self.location = data['location']
        self.driver = webdriver.Chrome(data['driver_path'])

    def login_linkedin(self):
        """ This function logs data into your personal linkedin profile"""

        #make driver go to linkedin login url
        self.driver.get("https://www.linkedin.com/login")

        #introduce our email and password and hit enter
        login_email = self.driver.find_element_by_name("session_key")
        login_email.clear()
        login_email.send_keys(self.email)

        login_password = self.driver.find_element_by_name("session_password")
        login_password.clear()
        login_password.send_keys(self.password)
        login_password.send_keys(Keys.RETURN)

    def job_search(self):
        """ THIS FUNCTION GOES TO JOB SECTION AND LOOKS FOR ALL THE JOBS THAT MATCHES THE KEYWORD"""

        #go to job section
        jobs_link = self.driver.find_element_by_link_text('Jobs')
        jobs_link.click()
        time.sleep(1)

        #introduce our keyword, location and hit enter button
        search_keyword = self.driver.find_element_by_xpath("//input[starts-with(@id,'jobs-search-box-keyword')]")
        search_keyword.clear()
        search_keyword.send_keys(self.keywords)
        time.sleep(2)

        search_location = self.driver.find_element_by_xpath("//input[starts-with(@id,'jobs-search-box-location')]")
        search_location.clear()
        search_location.send_keys(self.location)
        search_location.send_keys(Keys.RETURN)

    def filter(self):
        """ THIS FUNCTION FILTERS THE JOBS BY EASY APPLY"""

        #select all filters then click on easy apply and then apply the filter
        all_filters_button = self.driver.find_element_by_xpath("//button[@data-control-name='all_filters']")
        all_filters_button.click()
        time.sleep(1)
        easy_apply_button = self.driver.find_element_by_xpath("//label[@for='linkedinFeatures-f_AL']")
        easy_apply_button.click()
        time.sleep(1)
        apply_filter_button = self.driver.find_element_by_xpath("/html/body/div[4]/div/div/div[1]/div/div[2]/button[2]")
        apply_filter_button.click()

    def find_offers(self):
        """THIS FUN FIND ALL THE OFFERS THROUGH ALL THE RESULT OF SEARCH AND FILTERING"""
        #find the total amount of results(in case there are more than just 24 of them)
        total_results = self.driver.find_element_by_class_name("display-flex.t-12.t-black--light.t-normal")
        total_results_int = int(total_results.text.split(' ',1)[0].replace(",",""))
        print(total_results_int )
        time.sleep(2)

        #get result fo 1st page
        current_page = self.driver.current_url
        results = self.driver.find_elements_by_class_name("job-card-container.relative.job-card-list.job-card-container--clickable.job-card-list--underline-title-on-hover.jobs-search-two-pane__job-card-container--viewport-tracking-0")

        #for each job adds, submit application if no more questions are asked
        for result in results:
            hover = ActionChains(self.driver).move_to_element(result)
            hover.perform()
            titles = result.find_elements_by_class_name("full-width.artdeco-entity-lockup__title.ember-view")
            for title in titles:
                self.submit_apply(title)
        
        #if there is more than 1 page, find the pages and apply to rsults of each page
        if total_results_int > 24:
            time.sleep(2)

            #find the last page and construct url of each page
            find_pages = self.driver.find_elements_by_class_name("artdeco-pagination__indicator.artdeco-pagination__indicator--number.ember-view")
            total_pages = find_pages[len(find_pages)-1].text
            total_pages_int = int(re.sub(r"[^\d.]", "",total_pages))
            get_last_page = self.driver.find_element_by_xpath("//button[@aria-label='Page "+str(total_pages_int)+"']")
            get_last_page.send_keys(Keys.RETURN)
            time.sleep(2)
            last_page = self.driver.current_url
            total_jobs = int(last_page.split('start=',1)[1])

        #go through all available pages and job offers and apply
            for page_number in range(25, total_jobs+25,25):
                self.driver.get(current_page+'&start='+str(page_number))
                time.sleep(2)
                results_ext = self.driver.find_elements_by_class_name("job-card-container.relative.job-card-list.job-card-container--clickable.job-card-list--underline-title-on-hover.jobs-search-two-pane__job-card-container--viewport-tracking-0")
                for result_ext in results_ext:
                    hover_ext = ActionChains(self.driver).move_to_element(result_ext)
                    hover_ext.perform()
                    titles_ext = result_ext.find_elements_by_class_name("full-width.artdeco-entity-lockup__title.ember-view")
                    for title_ext in titles_ext:
                        self.submit_apply(title_ext)

        else:
            self.close_session

    def submit_apply(self,job_ad):
        """FUN SUBMITS THE JOB APPLICATION FOR THE JOB AD"""

        print("You are applying for the position of:", job_ad.text)
        job_ad.click()
        time.sleep(2)

        #click on easy apply button, skip if already applied earlier
        try:
            in_apply = self.driver.find_element_by_xpath("//button[@data-contro-name='jobdetails-topcard-inapply']")
            in_apply.click()
        except NoSuchElementException:
            print("You already appied for this job ad. Go to Next!")
            pass
        time.sleep(1)

        #try to submit if available
        try:
            submit = self.driver.find_element_by_xpath("//button[@data-control-name='submit_unify']")
            submit.send_keys(Keys.RETURN)
        #If button is not available then discard application
        except NoSuchElementException:
            print("No direct application")
            try:
                discard = self.driver.find_element_by_xpath("//button[@data-test-modal-close-btn']")
                discard.send_keys(Keys.RETURN)
                time.sleep(1)
                discard_confirm = self.driver.find_element_by_xpath("//button[@data-test-dialog-primary-btn']")
                discard_confirm.send_keys(Keys.RETURN)
                time.sleep(1)
            except NoSuchElementException:
                pass
        
        time.sleep(1)
        
    def close_session(self):
        """This function closes the actual session"""

        print("END OF SESSION")
        self.driver.close()

    
    def apply(self):
        """ Apply to job offers """

        self.driver.maximize_window()
        self.login_linkedin()
        time.sleep(5)
        self.job_search()
        time.sleep(5)
        self.filter()
        time.sleep(3)
        self.find_offers()
        time.sleep(3)
        self.close_session()




if __name__ =="__main__":

    with open('config.json') as config_file:
        data = json.load(config_file)

    bot = EasyApplyLinkedin(data)
    bot.apply()
