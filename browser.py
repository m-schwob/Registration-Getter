import os 
import logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


dir_path = os.getcwd()
CAR_MOT_GOV_URL = "http://car.mot.gov.il/"
CHROME_DRIVER_PATH = dir_path + "\\drivers\\chromedriver.exe"

# start the web driver and reload the search page
def start(debug):
    options = webdriver.ChromeOptions()
    if not debug: options.add_argument("headless")

    logging.info("open web driver..")
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=options, service_log_path='.\\output\\driver.log')
    logging.info("loading site..")
    driver.get(CAR_MOT_GOV_URL)
    handle_empty_response(driver)
    logging.info("site loaded")
    return driver


# check for EMPTY_RESPONSE. reload the page until not getting EMPTY_RESPONSE
def handle_empty_response(driver):
    while(driver.find_elements_by_xpath("//*[@class='error-code' and text()='ERR_EMPTY_RESPONSE']")):
        logging.info("empty response. refreshing..")
        driver.refresh()


# go to the first page of the given year
def go_to_year(driver, year):
    year_list_box = driver.find_element_by_xpath("//select[@name='cp_calendar_year']") 
    select = Select(year_list_box)
    select.select_by_value(str(year))
    #year_list_box.send_keys(year)
    search_btn = driver.find_element_by_name("submit_search")
    search_btn.send_keys(Keys.RETURN)
    handle_empty_response(driver)


# go to the next records page in the current year
def go_to_next_page(driver):
    next_page = driver.find_elements_by_xpath("//a[@class='pagenav' and text()='הבא']")
    if(next_page):
        next_page[0].click()
        handle_empty_response(driver)
        return True
    return False

# get th page number
def get_page_number(driver):
    page_navs = driver.find_elements_by_xpath("//span[@class='pagenav']")
    for nav in page_navs:
        if nav.text.isnumeric():
            return nav.text
    return "1" 


# get a list of the records elements
def get_page_result(driver):
    results = driver.find_elements_by_class_name("cp_result")
    #case of no result
    #driver.find_element_by_id("jsn-mainbody").find_elements_by_class_name("info").text == "לא נמצאו מסמכים תואמים עבור החיפוש"
    return results


# scrrap data from record element to dictionary 
def get_record(record_elem):
    record = {}
    record.update({'reg_num': record_elem.find_element_by_class_name("contentheading").text})
    record.update({'category': record_elem.find_element_by_class_name("cp_category").text})
    record.update({'file_link': record_elem.find_element_by_class_name("jcepopup").get_attribute("href")})
    record.update({'tags': [elem.text for elem in record_elem.find_elements_by_xpath("./div[@class='cp_tags']/span[not(contains(@class,'cp_tag_label'))]")]})
    record.update({'date': record_elem.find_element_by_class_name("cp_create_date").text})

    texts = record_elem.find_element_by_class_name("cp_text").text.split('\n')
    record.update(scrap_record_text(texts, record))
    return record

# scraping the information from the texts part of the record to the dictionary
def scrap_record_text(texts, record):
    condition = lambda text: 'הוראת רישום' in text and text.split().pop().isdecimal()
    extractor = lambda text: text.split().pop()
    record.update({'serial_num': extract_from_texts(texts, condition, extractor)})

    condition = lambda text: text.startswith('כינוי מסחרי:')
    extractor = lambda text: text.split(':').pop()
    record.update({'trade_name': extract_from_texts(texts, condition, extractor)})

    condition = lambda text: text.startswith('דגם:')
    extractor = lambda text: text.split(':').pop()
    record.update({'model': extract_from_texts(texts, condition, extractor)})

    condition = lambda text: text == 'קובץ להורדה'
    extractor = lambda text: text.split(':').pop()
    extract_from_texts(texts, condition, extractor)

    record.update({'note': ("\n").join(texts)})

    return record


# note: delete text item if condition is match
def extract_from_texts(texts, condition, extractor):
    for i in range(len(texts)):
        if condition(texts[i]):
            return extractor(texts.pop(i))
    return None


# close driver
def close(driver):
    driver.close()