import browser
import data_table
import os 
import urllib.request
import pandas as pd
#import subprocess.Popen

DEBUG = True
dir_path = os.getcwd()

def get_records():
     #   for each page get records, go to next page
    results = browser.get_page_result(scrapper)
    for result in results:
        record = browser.get_record(result)
        records_list.append(record)
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

def export_excel():
    df = pd.DataFrame.from_dict(records_list,)
    df.to_excel(".\\output\\records_table.xlsx", index=False)

if __name__ == "__main__":
    scrapper = browser.start(debug=DEBUG)
    records_list = []

    # logging
    # thread/async
    # progress and status holding
    for year in [2005]: #(2004,2022,1):
        get_year(year)

    export_excel()
    browser.close(scrapper)
    


