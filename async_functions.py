import asyncio
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
import json
import re

# Глобальный счетчик вызовов функции parsing_brand
parsing_brand_counter = 0
counter_lock = asyncio.Lock()


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            return await response.text()
        elif response.status == 404:
            return "404"
        return None


async def parsing_brand(session: aiohttp.ClientSession, url: str, semaphore: asyncio.Semaphore) -> str:
    global parsing_brand_counter
    async with semaphore:
        # Увеличиваем счетчик вызовов
        async with counter_lock:
            parsing_brand_counter += 1
            

        html_content = await fetch(session, url)
        if html_content == "404" or html_content is None:
            return None

        soup = BeautifulSoup(html_content, 'html.parser')
        link = soup.find('a', class_="product-attributes__list-item-link reset-link active-blue-text")
        return link.get_text().strip() if link else None


async def parse_page(page_number: int, base_url: str, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore) -> list:
    url = base_url.format(page_number)
    html_content = await fetch(session, url)
    if html_content == "404":
        print(f"{page_number - 1} страница была последней")
        return []
    if html_content is None:
        print(f"Ошибка на странице {page_number}")
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    products_container = soup.find("div", id="products-inner")
    if not products_container:
        return []

    product_cards = products_container.find_all("div", class_="catalog-2-level-product-card product-card subcategory-or-type__products-item with-prices-drop")
    tasks = []
    products = []

    for card in product_cards:
        product_id = card.get("id")
        product_name = card.find("span", class_="product-card-name__text").text.strip() if card.find("span", class_="product-card-name__text") else "Неизвестное название"
        
        middle_section = card.find("div", class_="catalog-2-level-product-card__middle")
        product_link = middle_section.find("a", href=True)["href"] if middle_section and middle_section.find("a", href=True) else "Ссылка отсутствует"
        full_product_link = "https://online.metro-cc.ru" + product_link

        old_price_wrapper = card.find("div", class_="product-unit-prices__old-wrapper")
        old_price = None
        if old_price_wrapper:
            old_price_sum = old_price_wrapper.find("span", class_="product-price__sum")
            old_price_rubles = old_price_sum.find("span", class_="product-price__sum-rubles") if old_price_sum else None
            old_price = re.sub(r"\s+", "", old_price_rubles.text.strip()) if old_price_rubles else "отсутствует"

        actual_price_wrapper = card.find("div", class_="product-unit-prices__actual-wrapper")
        actual_price = None
        if actual_price_wrapper:
            actual_price_sum = actual_price_wrapper.find("span", class_="product-price__sum")
            actual_price_rubles = actual_price_sum.find("span", class_="product-price__sum-rubles") if actual_price_sum else None
            actual_price = re.sub(r"\s+", "", actual_price_rubles.text.strip()) if actual_price_rubles else "отсутствует"

        tasks.append(parsing_brand(session, full_product_link, semaphore))
        products.append({
            "id": product_id,
            "name": product_name,
            "link": full_product_link,
            "common_price": old_price,
            "promo_price": actual_price,
            "brand": "Без бренда"
        })

    brands = await asyncio.gather(*tasks)
    for product, brand in zip(products, brands):
        product["brand"] = brand if brand else "Без бренда"

    return products


async def parse_all_pages(base_url: str):
    global parsing_brand_counter
    total_products = 0
    all_products = []
    semaphore = asyncio.Semaphore(10)  
    async with aiohttp.ClientSession() as session:
        page = 1
        while True:
            print(f"Асинхронный парсинг страницы {page}...")
            products = await parse_page(page, base_url, session, semaphore)
            if not products:  
                break
            all_products.extend(products)
            total_products += len(products)
            page += 1

    async with aiofiles.open("products.json", "w", encoding="utf-8") as file:
        await file.write(json.dumps(all_products, ensure_ascii=False, indent=4))

    print(f"Парсинг завершён. Всего найдено продуктов: {total_products}. Данные сохранены в 'products.json'.")
    
