import browser
import os 
import logging
import urllib.request
import pandas as pd
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
    return results


# download the pdf of a record
def download_pdf(record):
    file_path = dir_path + '\\output\\pdf\\' + record['reg_num'] + '.pdf'
    try:
        urllib.request.urlretrieve(record['file_link'], file_path)
    except:
        return


# navigate between records pages of a given year
def get_year(year):
    logging.info('getting %d', year)
    browser.go_to_year(scrapper, year)
    while(True):
        get_records()
        if not browser.go_to_next_page(scrapper): break
    logging.info('%d done')


# export the records list to excel
def export_excel():
    df = pd.DataFrame.from_dict(records_list,)
    df.to_excel(".\\output\\records_table.xlsx", index=False)


if __name__ == "__main__":
    logging.basicConfig(filename='.\\output\\logger.log', level=logging.DEBUG)
    scrapper = browser.start(debug=DEBUG)
    records_list = []

    # thread/async
    # progress and status holding
    for year in [2005]: #(2004,2022,1):
        get_year(year)

    export_excel()
    browser.close(scrapper)
    


