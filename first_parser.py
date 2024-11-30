import requests
from bs4 import BeautifulSoup as BS

metro_site = requests.get("https://online.metro-cc.ru/category/rybnye/ohlazhdennaya-ryba")
html = BS(metro_site.content, 'html.parser')



for element in html.select(".subcategory-or-type__products > .catalog-2-level-product-card product-card subcategory-or-type__products-item with-prices-drop"):
    title = element.select(".caption > a")
    print( title[0].text)