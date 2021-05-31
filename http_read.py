import aiohttp
import aiofiles
import asyncio
from asyncio import queues
import json

RECORDS_FOR_PAGE = 10
URL = "https://www.gov.il/he/api/DynamicCollector"

async def main():
    async with aiohttp.ClientSession() as session:
        async with  session.post(URL,json=PAYLOAD) as resp:
            # data = await resp.json()
            data = await resp.json()
            print(data)
    
    #     async with session.post(url, json=req):
    #         async with session.get(url) as resp:
    #             # print(resp)
    #             data = await resp.json()
    # # print(data)
    # # hashrate = json.loads(data) 

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
        "register_number": record["Data"]["year_of_manufacture"],
        "year_of_manufacture": record["Data"]["year_of_manufacture"],
        "manufacturer": record["Data"]["manufacturer"],
        "instruction_number": record["Data"]["instruction_number"],
        "vehicle_type": record["Data"]["vehicle_type"],
        "extension_of_validity": record["Data"]["extension_of_validity"],
        "Description": record["Description]"],
        "UrlName": record["UrlName"]
    }
    
# search filter available by the optional paramters -> "manufacturer","year_of_manufacture","instruction_number","vehicle_type" 
async def get_records(result=None, session=None, offset=0, **kwargs):
    if session is None:
        session = await aiohttp.ClientSession()
    payload = json.loads(payload_factory(offset=offset, kwargs=kwargs))
    async with session.post(URL,json=payload) as resp:
        data = await resp.json()
    if type(result) is queues.Queue():
        for res in data["Results"]:
            result.put(await format_record(res))
    else:
        return data

get_total_records()

async def create_tasks(loop, queue): 
    async with aiohttp.ClientSession() as session:
        for i in range(start=0, stop=get_total_records(), step=RECORDS_FOR_PAGE):
            loop.create_task(get_records(offset=i, res=queue))


records = queues.Queue()
loop = asyncio.get_event_loop()
create_tasks(loop, records)
loop.run_until_complete(main())


