# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import csv
from multiprocessing import Pool
from urllib.request import urlopen
from proxies_scraper import get_proxies
from random import choice, uniform
from time import sleep
titles = ['seller',
            'feed_product_type',
            'item_sku',
            'external_product_id',
            'external_product_id_type',
            'part_number',
            'model',
            'item_name',
            'brand_name',
            'manufacturer',
            'product_description',
            'update_delete',
            'condition_type',
            'standard_price',
            'quantity',
            'product_tax_code',
            'product_site_launch_date',
            'restock_date',
            'sale_price',
            'sale_from_date',
            'sale_end_date',
            'item_package_quantity',
            'offering_can_be_gift_messaged',
            'offering_can_be_giftwrapped',
            'fulfillment_latency',
            'number_of_items',
            'merchant_shipping_group_name',
            'list_price_with_tax',
            'website_shipping_weight',
            'website_shipping_weight_unit_of_measure',
            'item_length',
            'item_heigth',
            'item_width',
            'item_dimensions_unit_of_measure',
            'item_weight',
            'item_weight_unit_of_measure',
            'bullet_point1',
            'bullet_point2',
            'bullet_point3',
            'bullet_point4',
            'bullet_point5',
            'recommended_browse_nodes',
            'generic_keywords',
            'style_keywords1',
            'style_keywords2',
            'style_keywords3',
            'main_image_url',
            'other_image_url1',
            'other_image_url2',
            'other_image_url3',
            'swatch_image_url',
            'parent_child',
            'parent_sku',
            'relationship_type',
            'variation_theme',
            'safety_warning',
            'legal_disclaimer_description',
            'strap_type',
            'style_name',
            'department_name',
            'outer_material_type1',
            'outer_material_type2',
            'inner_material_type1',
            'inner_material_type2',
            'material_composition',
            'closure_type',
            'lifestyle1',
            'lifestyle2',
            'lifestyle3',
            'seasons',
            'material_type1',
            'material_type2',
            'are_batteries_included',
            'battery_cell_composition',
            'lithium_battery_weight',
            'warranty_type',
            'warranty_description',
            'occasion_type1',
            'occasion_type2',
            'care_instructions',
            'sole_material',
            'heel_type',
            'toe_style',
            'arch_type',
            'color_name',
            'size_name',
            'collection_name',
            'sport_type']


useragents = open('useragents.txt').read().split('\n')
proxies = get_proxies()
for i in range(10):
    proxys = {'http':'http://'+choice(proxies)}
    useragentr = {'User-Agent': choice(useragents[:20])}

def get_html(start_url, useragent=useragentr, proxy=proxys):
    sleep(uniform(0,1))
    try:
        r = requests.get(start_url, headers = useragentr, proxies = proxys, timeout = 10)
    except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
        pass
    return r.text
    
def get_ip(url):
    print('proxy and ua')
    soup = BeautifulSoup(get_html(url), 'lxml')
    ip = soup.find('span', class_ = 'ip')
    ua = soup.find('span', class_ = 'ip').find_next_sibling('span').text.strip()
    print(ip.text)
    print(ua)

def get_number_of_pages(start_url):
    soup = BeautifulSoup(get_html(start_url),'html5lib')
    for i in soup.findAll('span', class_ = 'pagnDisabled'):
        pages = i.text.strip()
    return int(pages)
#
def get_start_urls():
    with open('Start_Urls.csv') as infile:
        reader = csv.DictReader(infile)
        script_cat = {row['URL']:row['Script Category'] for row in reader}     
def write_titles():
    with open('amazon_test.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(titles)
def generate_all_pages(url):
    all_pages = []
    num = get_number_of_pages(url)
    for i in range(1, num + 1):
        base_url = 'https://www.amazon.com/s/ref=sr_pg_' + str(i)
        query_part1 = '?'+url.split('?')[1].split('bbn=')[0] +'page='+str(i)+'&bbn='
        query_part2 = '&ie='+url.split('&ie=')[1]
        new_url = base_url + query_part1 + query_part2
        all_pages.append(new_url)
    return all_pages

def get_product_links_all(start_url):
    links = []
    for i in generate_all_pages(start_url):
        for k in range(len(get_product_links_single_page(start_url))):
            links.append(get_product_links_single_page(start_url)[k])
    return links
def get_product_links_single_page(page_url):
    links = []
    soup = BeautifulSoup(get_html(page_url), 'html5lib')
    for k in soup.findAll('div', class_ = 'a-row a-gesture a-gesture-horizontal'):
        links.append(k.find('a', class_ = 'a-link-normal a-text-normal').get('href'))
        
    with open('ggwp.csv', 'a') as f:
            writer = csv.writer(f)
            for item in links:
                writer.writerow([item])
    return links

def main():
    l = []
    url = 'https://www.amazon.com/s/ref=sr_hi_6?rh=n%3A7141123011%2Cn%3A7147441011%2Cn%3A679255011%2Cn%3A6127770011%2Cn%3A679286011%2Cp_6%3AATVPDKIKX0DER%7CAH1YFAUS3NHX2%7CA38MYE29B8LFRT%7CA2I0YKRFYX9813%7CAG670YE9WDQRF%7CA1LEM297LNF1FK%7CA7QKSDTF5TXF5%7CA7ULJO7NAWM0L%7CA2BMBHD2OU3XDU%7CAU8KF031TC39C%7CA3SNLLVFZ6ABAC%7CA3VX72MEBB21JI%7CAUN61RNUNKNVG%7CA1BNXE6U3W2NOH%7CAM3NWFGAU67D%7CA2WOPAGVJGO3RL%7CA3NWHXTQ4EBCZS%7CA1UG884EF99PVQ%7CA15MDCTZU8FRDU%7CA2XDG44YY9CCCX%7CA5592GM03C9YR%7CA1YT150G3ARUNS%7CAL551XTSRGEN3&bbn=679286011&ie=UTF8&qid=1501746466'
    with Pool(10) as p:
        p.map(get_product_links_single_page, generate_all_pages(url))
        
#     for i in get_product_links_all(url):
#         print(i)
    
        
    
if __name__ == '__main__':
    main()
