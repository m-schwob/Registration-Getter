import os 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 

dir_path = os.getcwd()
CAR_MOT_GOV_URL = "http://car.mot.gov.il/"
CHROME_DRIVER_PATH = dir_path + "\\drivers\\chromedriver.exe"

def start(debug):
    options = webdriver.ChromeOptions()
    if not debug: options.add_argument("headless")

    print("open web driver..")
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=options)
    print("loading site..")
    driver.get(CAR_MOT_GOV_URL)
    handle_empty_response(driver)
    print("site loaded")
    return driver


def handle_empty_response(driver):
    while(driver.find_elements_by_xpath("//*[@class='error-code' and text()='ERR_EMPTY_RESPONSE']")):
        print("empty response. refreshing..")
        driver.refresh()


def go_to_year(driver, year):
    year_list_box = driver.find_element_by_name("cp_calendar_year")    
    year_list_box.send_keys(year)
    search_btn = driver.find_element_by_name("submit_search")
    search_btn.send_keys(Keys.RETURN)
    handle_empty_response(driver)


def go_to_next_page(driver):
    next_page = driver.find_elements_by_xpath("//a[@class='pagenav' and text()='סיום']")
    if(next_page): 
        next_page.click()
        handle_empty_response(driver)
        return True
    return False


def get_page_result(driver):
    results = driver.find_elements_by_class_name("cp_result")
    #case of no result
    #driver.find_element_by_id("jsn-mainbody").find_elements_by_class_name("info").text == "לא נמצאו מסמכים תואמים עבור החיפוש"
    return results


def get_record(record_elem):
    texts = record_elem.find_element_by_class_name("cp_text").text.split('\n')
    record = {}
    record.update({'reg_num': record_elem.find_element_by_class_name("contentheading").text})
    record.update({'category': record_elem.find_element_by_class_name("cp_category").text})
    record.update({'serial_num': texts[0].split().pop()})
    record.update({'note': texts[1]})
    record.update({'trade_name': texts[2].split(':').pop()}) #case of more then one ':'
    record.update({'model': texts[3].split(':').pop()}) #case of more then one ':' # case of no size is not 4
    record.update({'file_link': record_elem.find_element_by_class_name("jcepopup").get_attribute("href")})
    record.update({'tags': [elem.text for elem in record_elem.find_elements_by_xpath("./div[@class='cp_tags']/span[not(contains(@class,'cp_tag_label'))]")]})
    record.update({'date': record_elem.find_element_by_class_name("cp_create_date").text})
    return record