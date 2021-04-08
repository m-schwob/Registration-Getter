import os 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
import urllib.request


DEBUG = True

dir_path = os.getcwd()
CAR_MOT_GOV_URL = "http://car.mot.gov.il/"
CHROME_DRIVER_PATH = dir_path + "\\drivers\\chromedriver.exe"

options = webdriver.ChromeOptions()
if not DEBUG: options.add_argument("headless")

print("open web driver..")
driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=options)
driver.get(CAR_MOT_GOV_URL)

print("waiting for site to be loaded..")
# elem = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.NAME, "cp_calendar_year")))   
while(driver.find_elements_by_xpath("//*[@class='error-code' and text()='ERR_EMPTY_RESPONSE']")):
    print("empty response. refreshing..")
    driver.refresh()
print("site loaded")

elem = driver.find_element_by_name("cp_calendar_year")    
elem.send_keys("2019")

elem = driver.find_element_by_name("submit_search")
elem.send_keys(Keys.RETURN)

results = driver.find_elements_by_class_name("cp_result")
#case of no result
#driver.find_element_by_id("jsn-mainbody").find_elements_by_class_name("info").text == "לא נמצאו מסמכים תואמים עבור החיפוש"

#get result
reg_num = results[0].find_element_by_class_name("contentheading").text
print(reg_num)
category = results[0].find_element_by_class_name("cp_category").text
print(category)
texts = results[0].find_element_by_class_name("cp_text").text.split('\n')
serial_num = texts[0].split().pop()
print(serial_num)
note = texts[1]
print(note)
trade_name = texts[2].split(':').pop() #case of more then one ':'
print(trade_name)
model = texts[3].split(':').pop() #case of more then one ':'
print(model)
# case of no size is not 4

file_link = results[0].find_element_by_class_name("jcepopup").get_attribute("href")
print(file_link)
urllib.request.urlretrieve(file_link, dir_path + '\\output\\pdf\\' + reg_num + '.pdf')

tags = [elem.text for elem in results[0].find_elements_by_xpath("./div[@class='cp_tags']/span[not(contains(@class,'cp_tag_label'))]")]
print(tags)
date = results[0].find_element_by_class_name("cp_create_date").text
print(date)

next_page = results[0].find_elements_by_xpath("//a[@class='pagenav' and text()='סיום']")



# def execute(driver):

    # for each year search records
    #   for each page get records, go to next page
    #   for each record
    
    



# assert "Python" in driver.title
# 
# elem.clear()
# elem.send_keys("2019")
# elem.send_keys(Keys.RETURN)
# assert "No results found." not in driver.page_source
#
# driver.close()


# def main():
    

#     if not DEBUG: driver.close()
#     #execute(driver)

# if __name__ == "__main__":
#     main()