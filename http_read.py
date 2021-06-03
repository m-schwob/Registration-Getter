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
async_logger.setLevel(logging.DEBUG)


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


#TODO find currect_reg_num - rise warning or error if not
def format_record(record):
    format =  { # include the information about how to format the record to new dictionary format
        "registration_number": "Data/title",
        "year_of_manufacture": "Data/year_of_manufacture",
        "manufacturer": "Data/manufacturer",
        "instruction_number": "Data/instruction_number",
        "vehicle_type": "Data/vehicle_type",
        "extension_of_validity": "Data/extension_of_validity",
        "Description": "Description",
        "UrlName": "UrlName",
        "url": "Data/link1/URL"
    }
     #re.search("\d{2,3}-\d{4}", record["Data"]["title"]).group(0),
    for key,data in format.items():
        path = data.split('/')
        data = record
        for p in path:
            data = data.get(p,None)
            if not data: 
                data = ""
                logger.warning("missing information: no {} info in {}".format(key,record["UrlName"])) #TODO change after finding currect reg_num
                break
        record[key] = data
    return format
    
    
# search filter available by the optional paramters -> "manufacturer","year_of_manufacture","instruction_number","vehicle_type" 
async def get_records(result=None, session=None, offset=0, **kwargs):
    if session is None:
        session = aiohttp.ClientSession()
    payload = json.loads(await payload_factory(offset=offset, kwargs=kwargs))
    async with session.post(URL,json=payload) as resp: #TODO handle ClientConnectorError Cannot connect to host www.gov.il:443 ssl:default [The specified network name is no longer available]
        data = await resp.json()
    if type(result) is queues.Queue:
        for res in data["Results"]:
            await result.put(format_record(res))
    else:
        return data

async def get_total_records():
    return (await get_records())["TotalResults"]

# loop on queue.. (wraping 'get_records' enabling 'get_total_records' to use 'get_record' too)
async def request_record(requests_queue):
    while True:
        coro = await requests_queue.get()  # get a coroutine from the queue and execute it
        try:
            await coro
        except Exception:
            logger.exception("fail",exc_info=True)
        finally:
            requests_queue.task_done()

async def create_requests(records_queue, task_num):
    requests_queue = queues.Queue()    
    async with aiohttp.ClientSession() as session:
        for i in range(0, await get_total_records(), RECORDS_FOR_PAGE):
            await requests_queue.put(get_records(offset=i, session=session, result=records_queue))
        tasks = []
        for i in range(task_num):
            tasks.append(asyncio.create_task(request_record(requests_queue)))
        await requests_queue.join() # wait until all request are made (queue is empty)
        for t in tasks:
            t.cancel() 
        await asyncio.gather(*tasks, return_exceptions=True)    # wait until all tasks are cancelled.



if __name__ == "__main__":
    async def print_record(i, records: queues.Queue):
        while True:
            reg_num = await records.get()
            print("consumer {} done with {}".format(i,reg_num["registration_number"]))
            records.task_done()

    async def main():       
        task_num = 10
        records = queues.Queue()
        producer = asyncio.create_task(create_requests(records, task_num))
        consumers = [asyncio.create_task(print_record(i,records)) for i in range(task_num)]
        await asyncio.gather(producer)
        producer.cancel()
        await records.join()
        for c in consumers:
            c.cancel()
        await asyncio.gather(*consumers, return_exceptions=True)

    start = time.perf_counter()
    asyncio.run(main())
    elapsed = time.perf_counter() - start
    logger.info(f"Program completed in {elapsed:0.5f} seconds.")    

