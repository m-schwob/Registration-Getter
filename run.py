import browser
import os 
import urllib.request
#import subprocess.Popen

DEBUG = True
dir_path = os.getcwd()

def get_records():
    browser.go_to_year(driver, '2019') # for each year search records #   for each page get records, go to next page
    results = browser.get_page_result(driver)
    for result in results:
        record = browser.get_record(result)
        download_pdf(record)
        print(record + "\n----------------------------------")
    browser.go_to_next_page(driver)


def download_pdf(record):
    file_path = dir_path + '\\output\\pdf\\' + record['reg_num'] + '.pdf'
    try:
        urllib.request.urlretrieve(record['file_link'], file_path)
    except():
        return

if __name__ == "__main__":
    driver = browser.start(debug=DEBUG)
    # table = DataTable.create_empty()
    # logging
    # thread
    # progress and status holding
    get_records()
    #export_excel()
    driver.close()
    


