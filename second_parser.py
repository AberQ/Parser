from bs4 import BeautifulSoup
import requests

# Базовый URL для пагинации
base_url = "https://online.metro-cc.ru/category/rybnye/ohlazhdennaya-ryba?page={}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}
count_fish = 0
# Функция для парсинга одной страницы
def parse_page(page_number):
    url = base_url.format(page_number)
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        products_container = soup.find("div", id="products-inner")
        if not products_container:
            print(f"На странице {page_number} не найден контейнер с продуктами.")
            return False
        
        # Ищем карточки продуктов
        product_cards = products_container.find_all("div", class_="catalog-2-level-product-card")
        if not product_cards:
            print(f"На странице {page_number} нет продуктов.")
            return False
        
        for card in product_cards:
            # Извлекаем данные
            product_id = card.get("id")
            data_sku = card.get("data-sku")
            print(f"Product ID: {product_id}, SKU: {data_sku}")
        
        return True
        
    else:
        print(f"Ошибка {response.status_code} на странице {page_number}.")
        return False

# Цикл по всем страницам
page = 1
while True:
    print(f"Парсинг страницы {page}...")
    success = parse_page(page)
    if not success:  # Останавливаемся, если страницы закончились
        break
    page += 1
    
print("Парсинг завершен.")
