from async_functions import *
#Файл для исполнения команд
import asyncio
website = "https://online.metro-cc.ru/category/rybnye/ohlazhdennaya-ryba?page={}"   
asyncio.run(parse_all_pages(website))
