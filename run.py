import browser
import os 
import logging
import urllib.request
import pandas as pd
from queue import Queue
#import subprocess.Popen

DEBUG = True
dir_path = os.getcwd()

# get the records in the current page and download pdf files
def get_records():
    results = browser.get_page_result(scrapper)
    for result in results:
        record = browser.get_record(result)
        records_list.append(record)
        # download_pdf(record)
        downloads.put(record)
    return len(results)


# download the pdf of a record
def download_pdf(record):
    file_path = dir_path + '\\output\\pdf\\' + record['reg_num'] + '.pdf'
    try:
        logging.info("download from: " + record['file_link'])
        urllib.request.urlretrieve(record['file_link'], file_path)
    except Exception as e:
        logging.error(str(e))
        raise 


# navigate between records pages of a given year
def get_year(year):
    logging.info('getting %d', year)
    browser.go_to_year(scrapper, year)
    while(True):
        record_num = get_records()
        logging.info('year %d page %s: %d record scrapped', year, browser.get_page_number(scrapper),record_num)
        if not browser.go_to_next_page(scrapper): break
    logging.info('%d done', year)


# export the records list to excel
def export_excel():
    columns = ['reg_num','serial_num','trade_name','model','date','category','tags','note','file_link']
    #df = pd.DataFrame(data=records_list ,columns=columns)
    df = pd.DataFrame.from_dict(records_list)
    df.to_excel(".\\output\\records_table.xlsx", index=False, columns=columns)


if __name__ == "__main__":
    logging.basicConfig(filename='.\\output\\logger.log', level=logging.DEBUG)
    scrapper = browser.start(debug=True)
    records_list = []
    downloads = Queue()

    # thread/async
    # progress and status holding
    try:
        for year in [2006]: #range(2004,2022,1):
            get_year(year)

        export_excel()
        print("excel exported")

        while not downloads.empty():
            print("downloads left " + str(downloads.qsize()))
            record = downloads.get_nowait()
            print("download " + record['reg_num'])
            try:           
                download_pdf(record)
            except Exception as e:
                print("fail: " + str(e))
                downloads.put(record)
    except:
        if not DEBUG:
            browser.quit(scrapper)
        raise
    


