from bs4 import BeautifulSoup
import requests

# Базовый URL для пагинации
base_url = "https://online.metro-cc.ru/category/rybnye/ohlazhdennaya-ryba?page={}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

# Функция для парсинга одной страницы
def parse_page(page_number):
    url = base_url.format(page_number)
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        products_container = soup.find("div", id="products-inner")
        if not products_container:
            print(f"На странице {page_number} не найден контейнер с продуктами.")
            return 0
        
        # Ищем карточки продуктов
        product_cards = products_container.find_all("div", class_="catalog-2-level-product-card")
        if not product_cards:
            print(f"На странице {page_number} нет продуктов.")
            return 0
        
        for card in product_cards:
            # Извлекаем данные
            product_id = card.get("id")
            data_sku = card.get("data-sku")
            # Печатаем полный HTML, чтобы проверить, что мы находим
            # print(card.prettify())  # раскомментируйте для диагностики

            # Извлекаем имя продукта
            product_name_tag = card.find("a", class_="product-card-name__text")
            if not product_name_tag:
                # Пробуем найти имя через другие вложенные элементы
                middle_tag = card.find("div", class_="catalog-2-level-product-card__middle")
                if middle_tag:
                    name_tag = middle_tag.find("a", class_="product-card-name reset-link catalog-2-level-product-card__name style--catalog-2-level-product-card")
                    if name_tag:
                        product_name = name_tag.find("span", class_="product-card-name__text").text.strip()
                    else:
                        product_name = "Не найдено"
                else:
                    product_name = "Не найдено"
            else:
                product_name = product_name_tag.text.strip()

            print(f"Product ID: {product_id}, SKU: {data_sku}, Name: {product_name}")
        
        return len(product_cards)  # Возвращаем количество карточек продуктов
        
    else:
        print(f"Ошибка {response.status_code} на странице {page_number}.")
        return 0

# Цикл по всем страницам
total_products = 0
page = 1
while True:
    print(f"Парсинг страницы {page}...")
    found_products = parse_page(page)
    if found_products == 0:  # Останавливаемся, если страницы закончились
        break
    total_products += found_products
    page += 1

print(f"Парсинг завершен. Всего найдено продуктов: {total_products}")
