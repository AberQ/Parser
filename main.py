from async_functions import *
import asyncio
# Файл для запуска


if __name__ == "__main__":
    base_url_template = "https://online.metro-cc.ru/category/rybnye/ohlazhdennaya-ryba?page={}"
    asyncio.run(parse_all_pages(base_url_template))