import browser
import os 
import urllib.request
import aiohttp
import aiofiles 
import asyncio


DEBUG = True
dir_path = os.getcwd()

async def get_records():
    async with aiohttp.ClientSession() as session:
        browser.go_to_year(driver, '2019') # for each year search records #   for each page get records, go to next page
        results = browser.get_page_result(driver)
        for result in results:
            record = browser.get_record(result)
            print(str(record['reg_num']) + " fetched")
            asyncio.create_task(download_pdf(record, session))
            # print(record)
            # print("\n----------------------------------")
        browser.go_to_next_page(driver)
    await asyncio.gather(*asyncio.all_tasks())

async def download_pdf(record, session):
    print("downloading " + str(record['reg_num']))
    file_path = dir_path + '\\output\\pdf\\' + record['reg_num'] + '.pdf'
    async with session.get(record['file_link']) as response:
        content = await response.read()

    if(response.status != 200):
        print("fail to download " + str(record['reg_num']))
        return

    async with aiofiles.open(file_path, "+wb") as file:
        await file.write(content)
    
    print("download finished " + str(record['reg_num']))


if __name__ == "__main__":
    driver = browser.start(debug=DEBUG)
    # table = DataTable.create_empty()
    # logging
    # thread
    # progress and status holding
    asyncio.run(get_records())
    #export_excel()
    driver.close()
    


