from async_functions import *
import asyncio
# Файл для запуска

#Запуск асихнронного парсинга
if __name__ == "__main__":
    base_url_template = "https://online.metro-cc.ru/category/chaj-kofe-kakao/kofe?from=under_search&page={}"
    asyncio.run(parse_all_pages(base_url_template))