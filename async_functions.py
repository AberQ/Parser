import json
from bs4 import BeautifulSoup
import requests
import re
import aiohttp
from aiohttp import ClientSession
# В этом файле функции парсера
async def parsing_brand(url: str) -> str:
    """
    Асинхронно извлекает название бренда продукта по переданной ссылке.

    Args:
        url (str): URL страницы продукта.

    Returns:
        str: Название бренда, если найдено. Иначе None.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    link = soup.find('a', class_="product-attributes__list-item-link reset-link active-blue-text")
                    
                    if link:
                        return link.get_text().strip()
                else:
                    print(f"Ошибка {response.status} при запросе {url}")
        except Exception as e:
            print(f"Ошибка при обработке {url}: {e}")
    
    return None

async def parse_page(page_number: int, base_url: str, products: list) -> int:
    """
    Асинхронно парсит одну страницу каталога и извлекает данные о продуктах.

    Args:
        page_number (int): Номер страницы для парсинга.
        base_url (str): Шаблон URL, где `{}` будет заменён на номер страницы.
        products (list): Список, куда добавляются найденные товары.

    Returns:
        int: Количество найденных товаров на странице.
             Возвращает -1, если страница не найдена (404).
             Возвращает 0 в случае других ошибок.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }
    url = base_url.format(page_number)
    
    async with ClientSession(headers=headers) as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    products_container = soup.find("div", id="products-inner")
                    if products_container:
                        product_cards = products_container.find_all(
                            "div", class_="catalog-2-level-product-card product-card subcategory-or-type__products-item with-prices-drop"
                        )
                        for card in product_cards:
                            product_id = card.get("id")
                            product_name = card.find("span", class_="product-card-name__text").text.strip() \
                                if card.find("span", class_="product-card-name__text") else "Неизвестное название"
                            
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

                            # Извлечение бренда
                            brand = await parsing_brand(full_product_link)

                            # Добавление данных товара в список для JSON
                            products.append({
                                "id": product_id,
                                "name": product_name,
                                "link": full_product_link,
                                "old_price": old_price,
                                "actual_price": actual_price,
                                "brand": brand
                            })

                        return len(product_cards)
                    else:
                        return 0
                elif response.status == 404:
                    print(f"{page_number - 1} страница была последней")
                    return -1
                else:
                    print(f"Ошибка {response.status} на странице {page_number}.")
                    return 0
        except Exception as e:
            print(f"Ошибка: {e}")
            return 0

async def parse_all_pages(base_url: str) -> None:
    """
    Асинхронно парсит все страницы каталога и сохраняет данные о продуктах в JSON-файл.

    Args:
        base_url (str): Шаблон URL, где `{}` будет заменён на номер страницы.

    Returns:
        None
    """
    total_products = 0
    products = []
    page = 1

    async def fetch_page(page_number):
        print(f"Асинхронный парсинг страницы {page_number}...")
        return await parse_page(page_number, base_url, products)

    while True:
        found_products = await fetch_page(page)
        if found_products == -1:  # Стоп, если страница не найдена
            break
        total_products += found_products
        page += 1

    # Сохранение данных в JSON
    with open("products.json", "w", encoding="utf-8") as file:
        json.dump(products, file, ensure_ascii=False, indent=4)

    print(f"Парсинг завершен. Всего найдено продуктов: {total_products}. Данные сохранены в 'products.json'.")

