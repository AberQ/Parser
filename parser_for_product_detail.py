import requests
from bs4 import BeautifulSoup
def parsing_brand(url):
    response = requests.get(url)

    soup = BeautifulSoup(response.content, 'html.parser')
    link = soup.find('a', class_="product-attributes__list-item-link reset-link active-blue-text")

    if link:
        return link.get_text().strip()
print(parsing_brand('https://online.metro-cc.ru/products/forel-murmanskaya-morskaya-5-6kg-inarctica'))