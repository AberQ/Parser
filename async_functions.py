import asyncio
import aiohttp
import aiofiles  
from bs4 import BeautifulSoup
import json
import re
#Асинхронные фукнции парсера

async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    """
    Асинхронно выполняет запрос к URL и возвращает содержимое ответа.

    Args:
        session (ClientSession): Сессия aiohttp.
        url (str): URL для запроса.

    Returns:
        str: HTML-содержимое ответа.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            return await response.text()
        elif response.status == 404:
            return "404"
        return None


async def parsing_brand(session: aiohttp.ClientSession, url: str) -> str:
    """
    Асинхронно извлекает название бренда продукта по переданной ссылке.

    Args:
        session (ClientSession): Сессия aiohttp.
        url (str): URL страницы продукта.

    Returns:
        str: Название бренда, если найдено. Иначе None.
    """
    html_content = await fetch(session, url)
    if html_content == "404" or html_content is None:
        return None

    soup = BeautifulSoup(html_content, 'html.parser')
    link = soup.find('a', class_="product-attributes__list-item-link reset-link active-blue-text")
    return link.get_text().strip() if link else None


async def parse_page(page_number: int, base_url: str, session: aiohttp.ClientSession, products: list) -> int:
    """
    Асинхронно парсит одну страницу каталога и извлекает данные о продуктах.

    Args:
        page_number (int): Номер страницы для парсинга.
        base_url (str): Шаблон URL, где `{}` будет заменён на номер страницы.
        session (ClientSession): Сессия aiohttp.
        products (list): Список, куда добавляются найденные товары.

    Returns:
        int: Количество найденных товаров на странице.
    """
    url = base_url.format(page_number)
    html_content = await fetch(session, url)
    if html_content == "404":
        print(f"{page_number - 1} страница была последней")
        return -1
    if html_content is None:
        print(f"Ошибка на странице {page_number}")
        return 0

    soup = BeautifulSoup(html_content, 'html.parser')
    products_container = soup.find("div", id="products-inner")
    if not products_container:
        return 0

    product_cards = products_container.find_all("div", class_="catalog-2-level-product-card product-card subcategory-or-type__products-item with-prices-drop")
    tasks = []

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

        
        tasks.append(parsing_brand(session, full_product_link))

        
        products.append({
            "id": product_id,
            "name": product_name,
            "link": full_product_link,
            "old_price": old_price,
            "actual_price": actual_price,
            "brand": "Без бренда"  
        })

    brands = await asyncio.gather(*tasks)
    for i, brand in enumerate(brands):
        products[i]["brand"] = brand

    return len(product_cards)


async def parse_all_pages(base_url: str):
    """
    Асинхронно парсит все страницы каталога и сохраняет данные о продуктах в JSON-файл.

    Args:
        base_url (str): Шаблон URL, где `{}` будет заменён на номер страницы.

    Returns:
        None
    """
    total_products = 0
    products = []
    async with aiohttp.ClientSession() as session:
        page = 1
        while True:
            print(f"Асинхроный парсинг страницы {page}...")
            found_products = await parse_page(page, base_url, session, products)
            if found_products == -1:
                break
            total_products += found_products
            page += 1

    # Сохранение данных в JSON
    async with aiofiles.open("products.json", "w", encoding="utf-8") as file:
        await file.write(json.dumps(products, ensure_ascii=False, indent=4))

    print(f"Парсинг завершён. Всего найдено продуктов: {total_products}. Данные сохранены в 'products.json'.")



