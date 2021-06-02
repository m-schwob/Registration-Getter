import asyncio
import logging
import aiofiles
import aiohttp
from asyncio import queues
import json
import re
import time


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

file_handler = logging.FileHandler('scraper.log')
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

async_logger = logging.getLogger("asyncio")
async_logger.addHandler(logging.FileHandler('async.log'))


RECORDS_FOR_PAGE = 10
URL = "https://www.gov.il/he/api/DynamicCollector"

# 
#     search()
#     #compare
#     #update

# optional paramters for filter -> "manufacturer","year_of_manufacture","instruction_number","vehicle_type" 
async def payload_factory(offset=0, **kwargs):  
    format = lambda key,value: {key: { "Query": value}}
    filter = format("skip", offset)
    filter_args = ["manufacturer","year_of_manufacture","instruction_number","vehicle_type"]
    for key,value in kwargs.items():
        if key in filter_args:
            filter.update(format(key,value))
    payload =  {
                "DynamicTemplateID": "80d0fbf7-bf74-41c4-8bb3-1b6dd716f4b4",
                "QueryFilters": filter,
                "From": offset 
            }  
    return json.dumps(payload)


async def format_record(record):
    return {
        "registration_number": re.search("\d{2,3}-\d{4}", record["Data"]["title"]),
        "year_of_manufacture": record["Data"]["year_of_manufacture"],
        "manufacturer": record["Data"]["manufacturer"],
        "instruction_number": record["Data"]["instruction_number"],
        "vehicle_type": record["Data"]["vehicle_type"],
        "extension_of_validity": record["Data"]["extension_of_validity"],
        "Description": record["Description"],
        "UrlName": record["UrlName"],
        "url": record["Data"]["link1"]["URL"]
    }
    
# search filter available by the optional paramters -> "manufacturer","year_of_manufacture","instruction_number","vehicle_type" 
async def get_records(result=None, session=None, offset=0, **kwargs):
    if session is None:
        session = aiohttp.ClientSession()
    payload = json.loads(await payload_factory(offset=offset, kwargs=kwargs))
    async with session.post(URL,json=payload) as resp:
        data = await resp.json()
    if type(result) is queues.Queue:
        for res in data["Results"]:
            print(await format_record(res))
            #result.put(await format_record(res))
    else:
        return data

async def get_total_records():
    return (await get_records())["TotalResults"]

async def request_record(requests_queue):
    while True:
        await requests_queue.get()
        requests_queue.task_done()

async def create_requests(records_queue, task_num):
    requests_queue = queues.Queue()    
    async with aiohttp.ClientSession() as session:
        for i in range(0, await get_total_records(), RECORDS_FOR_PAGE):
            requests_queue.put(get_records(offset=i, session=session, result=records_queue))
        tasks = [] 
        for i in range(task_num):
            tasks.append(asyncio.create_task(request_record(requests_queue, records_queue)))   
    return requests_queue



if __name__ == "__main__":
    async def main():       
        task_num = 10
        records = queues.Queue()
        requests = create_requests(records, task_num)
        process = []
        
        # while(not records.empty()):
        #     print(records.get())
    start = time.perf_counter()
    asyncio.run(main())
    elapsed = time.perf_counter() - start
    logging.info(f"Program completed in {elapsed:0.5f} seconds.")    

