from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep, gmtime, strftime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import csv
import time
import pytest



# csv file name
order_details_file = "details.csv"
timings_file = "OutputResult.csv"
environment_config_file = "environment_config.csv"

def load_user_data():
    rows = []
    with open(order_details_file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)        
        # extracting field names through first row
        fields = csvreader.next()
        
        # extracting each data row one by one
        for row in csvreader:
            data = {fields[0] : row[0], fields[1] : row[1], fields[2] : row[2], fields[3] : row[3], fields[4] : row[4], fields[5] : row[5],fields[6] : row[6]}
            rows.append(data)
            
    return rows

data_rows = load_user_data()

def load_environment_config():
    rows = {}
    with open(environment_config_file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)        
        # extracting field names through first row
        fields = csvreader.next()
        # extracting data through second row
        data = csvreader.next()       
        for i in range(len(data)):
            rows[fields[i]] = data[i]
            
    return rows

environment_config_data = load_environment_config()

@pytest.fixture
def session_object():

    driver = webdriver.Chrome()   
    # Set default timeout for locating and element in the DOM (30 seconds)
    driver.implicitly_wait((int(environment_config_data["WaitTime"])/1000))
    
    # Maximize window (Need to comment when using Headless browser)
    driver.maximize_window()    
    yield driver
    driver.quit()

@pytest.mark.parametrize("data_row", data_rows)
def test_create_portal_order(session_object, data_row): 
    test_case_date_time = time.strftime("%Y-%m-%d %H:%M:%S")
    Git_test = CreateGitsignup(test_case_date_time, session_object)
    assert Git_test.create_User(data_row) == True

class CreateGitsignup():
    
    def __init__(self, test_case_date_time, driver):
        self.driver = driver
        self.test_case_status = "Fail"
        self.test_case_date_time = test_case_date_time
                      
    def create_User(self, data_row):
        try:
            self.driver.get(environment_config_data["URL"])
            self.login(data_row)
            time.sleep(5)
            self.test_case_status = "Pass"
            return True
        except Exception as error:
            print error
            return False
        finally:
            self.save_timings(data_row)
            
    def login(self, user_details):
        driver = self.driver
        wait=WebDriverWait(driver, 15)
        try:
            sleep(1)    
            self.loginErrorMessage=False     
            self.emailErrorMessage=False
            self.passErrorMessage=False
            self.finalErrorMessage=False
            driver.find_element_by_id("user[login]").clear()
            driver.find_element_by_id("user[login]").send_keys(user_details["UserName"])
            
            try:
                if user_details["ExpectedUsernameErrorMessage"]=="TRUE":
                    self.loginErrorMessage=wait.until(EC.text_to_be_present_in_element((By.XPATH,"/html/body/div[4]/div[1]/div/div/div[2]/div/form/dl[1]/dd[2]"), "Username is already taken"))     
            except Exception as error:
                self.loginErrorMessage=False    
            print "login error message"
            print self.loginErrorMessage
            
            driver.find_element_by_id("user[email]").clear()
            driver.find_element_by_id("user[email]").send_keys(user_details["Email"])
            
            try:
                if user_details["ExpectedEmailErrorMessage"]=="TRUE":
                    self.emailErrorMessage=wait.until(EC.text_to_be_present_in_element((By.XPATH,"/html/body/div[4]/div[1]/div/div/div[2]/div/form/dl[2]/dd[2]"), "Email is invalid or already taken"))     
            except Exception as error:
                self.emailErrorMessage=False    
            print "Email error message"
            print self.emailErrorMessage

            driver.find_element_by_id("user[password]").clear()
            driver.find_element_by_id("user[password]").send_keys(user_details["Password"])
            pass_note=driver.find_elements_by_class_name("form-control-note")
            try:
                for i in range(1,4):
                    pass_Error=driver.find_element_by_xpath("/html/body/div[4]/div[1]/div/div/div[2]/div/form/password-strength/dl/p/span["+str(i)+"]")  
                    print "Attribute name"
                    print pass_Error.get_attribute("class")
                    if pass_Error.get_attribute("class")=="text-red":
                        self.passErrorMessage=True
            except Exception as error:
                self.passErrorMessage=False       
            print "Password error message"
            print self.passErrorMessage      
            driver.find_element_by_class_name("btn-mktg").click();
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME,"steps")))
            if user_details["FinalErrorMessage"]=="TRUE":
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,".flash.flash-error.my-3")))  
                self.finalErrorMessage=True;   
            else:
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,".octicon.octicon-check.text-green")))
                self.finalErrorMessage=False    
            sleep(5)
        except Exception as error:
            self.save_screenshot("login_page")
            raise Exception("Failed to login : " + error.message)
                                   
    def save_screenshot(self, name):
        """ Save screenshot """
        self.driver.get_screenshot_as_file(name + "_" + (self.test_case_date_time).strip().replace(" ", "_").replace(":", "-") + ".png")
       
    def write_data_in_csv(self, data_row):
        with open(timings_file, 'a') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(data_row)
            
    def save_timings(self, user_details):
        data_row = [self.test_case_date_time, user_details["UserName"],user_details["Email"],user_details["Password"],
                    user_details["ExpectedUsernameErrorMessage"],self.loginErrorMessage,
                    user_details["ExpectedEmailErrorMessage"],self.emailErrorMessage, 
                    user_details["ExpectedPasswordErrorMessage"],self.passErrorMessage,user_details["FinalErrorMessage"],self.finalErrorMessage]
        self.write_data_in_csv(data_row)