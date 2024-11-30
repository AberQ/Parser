from bs4 import BeautifulSoup
import requests
card_count = 0
# Загрузка страницы
url = "https://online.metro-cc.ru/category/rybnye/ohlazhdennaya-ryba"  # Замени на нужный URL
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}
response = requests.get(url, headers=headers)

if response.status_code == 200:
    # Парсим HTML с помощью Beautiful Soup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Находим контейнер с продуктами
    products_container = soup.find("div", id="products-inner")
    if products_container:
        # Ищем все карточки продуктов внутри
        product_cards = products_container.find_all("div", class_="catalog-2-level-product-card")
        for card in product_cards:
            # Извлекаем нужные атрибуты
            product_id = card.get("id")
            data_sku = card.get("data-sku")
            class_name = card.get("class")
            card_count = card_count + 1
            # Выводим данные
            print(f"Product ID: {product_id}, SKU: {data_sku}, Classes: {class_name}")
        print(card_count)
    else:
        print("Контейнер с продуктами не найден.")
else:
    print(f"Не удалось загрузить страницу. Код ошибки: {response.status_code}")
