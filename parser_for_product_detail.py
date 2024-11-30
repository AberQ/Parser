import requests
from bs4 import BeautifulSoup

url = "https://online.metro-cc.ru/products/forel-murmanskaya-morskaya-5-6kg-inarctica"
response = requests.get(url)

soup = BeautifulSoup(response.content, 'html.parser')
link = soup.find('a', class_="product-attributes__list-item-link reset-link active-blue-text")

if link:
    print(link.get_text().strip())
