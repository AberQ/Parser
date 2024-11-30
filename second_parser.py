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
        
        # Поиск контейнера с продуктами
        products_container = soup.find("div", id="products-inner")
        if products_container:
            product_cards = products_container.find_all("div", class_="catalog-2-level-product-card product-card subcategory-or-type__products-item with-prices-drop")
            for card in product_cards:
                product_id = card.get("id")
                product_name = card.find("span", class_="product-card-name__text").text.strip() if card.find("span", class_="product-card-name__text") else "Неизвестное название"
                
                # Поиск ссылки на товар
                middle_section = card.find("div", class_="catalog-2-level-product-card__middle")
                product_link = middle_section.find("a", href=True)["href"] if middle_section and middle_section.find("a", href=True) else "Ссылка отсутствует"
                full_product_link = "https://online.metro-cc.ru" + product_link
                
                # Извлечение старой цены
                old_price_wrapper = card.find("div", class_="product-unit-prices__old-wrapper")
                old_price = None
                if old_price_wrapper:
                    old_price_sum = old_price_wrapper.find("span", class_="product-price__sum")
                    old_price_rubles = old_price_sum.find("span", class_="product-price__sum-rubles") if old_price_sum else None
                    old_price = old_price_rubles.text.strip() if old_price_rubles else "Цена отсутствует"

                # Извлечение текущей цены
                actual_price_wrapper = card.find("div", class_="product-unit-prices__actual-wrapper")
                actual_price = None
                if actual_price_wrapper:
                    actual_price_sum = actual_price_wrapper.find("span", class_="product-price__sum")
                    actual_price_rubles = actual_price_sum.find("span", class_="product-price__sum-rubles") if actual_price_sum else None
                    actual_price = actual_price_rubles.text.strip() if actual_price_rubles else "Цена отсутствует"

                print(f"ID: {product_id}, Название: {product_name}, Ссылка: {full_product_link}, Регулярная цена: {old_price}, Промо-цена: {actual_price}")
        
        return len(product_cards) if products_container else 0
        
    elif response.status_code == 404:
        print(f"Ошибка 404: Страница {page_number} не найдена.")
        return -1  # Возвращаем -1, чтобы остановить цикл на ошибке 404
    else:
        print(f"Ошибка {response.status_code} на странице {page_number}.")
        return 0

# Цикл по всем страницам
total_products = 0
page = 1
while True:
    print(f"Парсинг страницы {page}...")
    found_products = parse_page(page)
    if found_products == -1:  # Останавливаемся на ошибке 404
        break
    total_products += found_products
    page += 1

print(f"Парсинг завершен. Всего найдено продуктов: {total_products}")
