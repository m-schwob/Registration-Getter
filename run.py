import browser
import os 
import urllib.request
#import subprocess.Popen

DEBUG = True
dir_path = os.getcwd()

def get_records():
     #   for each page get records, go to next page
    results = browser.get_page_result(scrapper)
    for result in results:
        record = browser.get_record(result)
        # download_pdf(record)



def download_pdf(record):
    file_path = dir_path + '\\output\\pdf\\' + record['reg_num'] + '.pdf'
    try:
        urllib.request.urlretrieve(record['file_link'], file_path)
    except:
        return

def get_year(year):
    browser.go_to_year(scrapper, year) # for each year search records
    while(True):
        get_records()
        if not browser.go_to_next_page(scrapper): return


if __name__ == "__main__":
    scrapper = browser.start(debug=DEBUG)
    # table = DataTable.create_empty()
    # logging
    # thread/async
    # progress and status holding
    for year in range(2004,2021,1):
        get_year(year)
    
    #export_excel()
    browser.close(scrapper)
    


