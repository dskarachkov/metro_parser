import requests
from bs4 import BeautifulSoup
import csv
import unicodedata

CSV = 'products.csv'
HOST = 'https://online.metro-cc.ru'
URL = 'https://online.metro-cc.ru/category/chaj-kofe-kakao/kofe?from=under_search'
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}


def get_html(url, params=''):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_content(html):
    """Получение данных"""
    page_soup = BeautifulSoup(html, 'html.parser')
    items = page_soup.find_all('div', class_='catalog-2-level-product-card')
    products = []
    products_counter = 0

    """Проходимся по каждому товару на одной сранице"""
    for item in items:
        products_counter += 1
        print(f'товар {products_counter}')

        product_link = HOST + item.find('div', class_='catalog-2-level-product-card__middle').find('a').get('href')
        #print(product_link)

        html_product = get_html(product_link)
        product_soup = BeautifulSoup(html_product.text, 'html.parser')

        """Проверка наличия товара, если его нет, то выходим из цикла"""
        if item.find('div', class_='product-unit-prices__actual-wrapper'):

            """Проверка наличия промо цены"""
            if item.find('div', class_='product-unit-prices__old-wrapper').find('span',
                                                                                class_='product-price__sum-rubles'):
                products.append(
                    {
                        'id': product_soup.find("p", itemprop="productID").get_text(strip=True).replace('Артикул: ',
                                                                                                        ''),
                        'title': product_soup.find('h1', class_='product-page-content__product-name').get_text(
                            strip=True),
                        'product_link': product_link,
                        'actual_price': unicodedata.normalize("NFKD", item.find('div',
                                                                                class_='product-unit-prices__actual-wrapper').find(
                            'span', class_='product-price__sum-rubles').get_text()),
                        'old_price': unicodedata.normalize("NFKD", item.find('div',
                                                                             class_='product-unit-prices__old-wrapper').find(
                            'span', class_='product-price__sum-rubles').get_text()),
                        'brand': product_soup.find("meta", itemprop="brand").get('content')
                    }
                )
            else:
                products.append(
                    {
                        'id': product_soup.find("p", itemprop="productID").get_text(strip=True).replace('Артикул: ',
                                                                                                        ''),
                        'title': product_soup.find('h1', class_='product-page-content__product-name').get_text(
                            strip=True),
                        'product_link': product_link,
                        'actual_price': unicodedata.normalize("NFKD", item.find('div',
                                                                                class_='product-unit-prices__actual-wrapper').find(
                            'span', class_='product-price__sum-rubles').get_text()),
                        'old_price': unicodedata.normalize("NFKD", item.find('div',
                                                                             class_='product-unit-prices__actual-wrapper').find(
                            'span', class_='product-price__sum-rubles').get_text()),
                        'brand': product_soup.find("meta", itemprop="brand").get('content')
                    }
                )
        else:
            return products
    return products


def save_doc(items, path):
    """Запись данных в csv файл"""
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['id товара', 'наименование', 'ссылка на товар', 'промо цена', 'регулярная цена', 'бренд'])
        for item in items:
            writer.writerow([item['id'], item['title'], item['product_link'], item['actual_price'], item['old_price'],
                             item['brand']])


def parser():
    PAGINATION = 17
    html = get_html(URL)
    if html.status_code == 200:
        products = []
        for page in range(1, PAGINATION + 1):
            print(f'Парсинг страницы {page}')
            html = get_html(URL, params={'page': page})
            products.extend(get_content(html.text))
            save_doc(products, CSV)
    else:
        print('Error')


parser()
