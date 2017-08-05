# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from proxies_scraper import get_proxies
import re
import csv
import urllib
import html5lib
from multiprocessing import Pool
from distutils.filelist import findall
from random import choice, uniform
from time import sleep
from itertools import product
from htmlmin.minify import html_minify
from django.core.management import color

URL = 'https://www.amazon.com/s/ref=sr_hi_6?rh=n%3A7141123011%2Cn%3A7147441011%2Cn%3A679255011%2Cn%3A6127770011%2Cn%3A679286011%2Cp_6%3AATVPDKIKX0DER%7CAH1YFAUS3NHX2%7CA38MYE29B8LFRT%7CA2I0YKRFYX9813%7CAG670YE9WDQRF%7CA1LEM297LNF1FK%7CA7QKSDTF5TXF5%7CA7ULJO7NAWM0L%7CA2BMBHD2OU3XDU%7CAU8KF031TC39C%7CA3SNLLVFZ6ABAC%7CA3VX72MEBB21JI%7CAUN61RNUNKNVG%7CA1BNXE6U3W2NOH%7CAM3NWFGAU67D%7CA2WOPAGVJGO3RL%7CA3NWHXTQ4EBCZS%7CA1UG884EF99PVQ%7CA15MDCTZU8FRDU%7CA2XDG44YY9CCCX%7CA5592GM03C9YR%7CA1YT150G3ARUNS%7CAL551XTSRGEN3&bbn=679286011&ie=UTF8&qid=1501746466'
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
        get_html(start_url, useragent, proxy)
    minified_html = html_minify(r.text)    
    return minified_html
def get_urls_dict():
    with open('Amazon_URLS.csv') as infile:
        reader = csv.DictReader(infile)
        dict = {row['URL']:row['Script Category'] for row in reader} 
    return dict

def get_code(url):
    category = get_urls_dict().get(url)
    codes = {
                'Electronics' : 'ELECTRNCS',
                'Sports Equipment': 'SPRTSEQIP',
                'Health and Beauty': 'HLTHBTY',
                "Women's Fashion Accessories" : 'WMNFSHACCSS',
                'Toys and Games': 'TOYS',
                "Men's Fashion Shoes": 'MNFSHSHOE',
                "Other Sports Shoes": 'OTHSPRTSSHOE',
                "Women's Sports Shoes": 'WMNSPORTSHOE',
                "Men's Running Shoes": 'MNSRUNSHOE',
                "Amazon Global-Toys": 'GLBTOYS',
                "Women's Running Shoes": 'WMNRUNSHOE',
                "Women's Fashion Shoes": 'WMNFSHSHOE',
                "Computer & Accessories": 'CMPTRACCS',
                "Office Supplies" : "OFFSUPPLIES",
                "Clothing Accessories" : "CLTHACCSS",
                "TigerDirect" : "TDRCT"
                }

    return codes.get(category)
    
def get_number_of_pages(start_url):
    soup = BeautifulSoup(get_html(start_url),'html5lib')
    for i in soup.findAll('span', class_ = 'pagnDisabled'):
        pages = i.text.strip()
    return int(pages)

def get_product_links(start_url):
    links = []
    for i in generate_all_pages(start_url):
        soup = BeautifulSoup(get_html(i), 'html5lib')
        for k in soup.findAll('div', class_ = 'a-row a-gesture a-gesture-horizontal'):
            links.append(k.find('a', class_ = 'a-link-normal a-text-normal').get('href'))
    return links

def get_product_info(url, product_link):
    data = {'seller': '',
            'feed_product_type':'SHOES',
            'item_sku':'',
            'external_product_id': '',
            'external_product_id_type': 'ASIN',
            'part_number': '',
            'model': '',
            'item_name': '',
            'brand_name': '',
            'manufacturer':'',
            'product_description':'',
            'update_delete': 'update',
            'condition_type':'new',
            'standard_price':'',
            'quantity':'10',
            'product_tax_code':'',
            'product_site_launch_date':'',
            'restock_date':'',
            'sale_price':'',
            'sale_from_date':'',
            'sale_end_date':'',
            'item_package_quantity':'1',
            'offering_can_be_gift_messaged':'',
            'offering_can_be_giftwrapped':'',
            'fulfillment_latency':'20',
            'number_of_items':'',
            'merchant_shipping_group_name':'',
            'list_price_with_tax':'',
            'website_shipping_weight':'',
            'website_shipping_weight_unit_of_measure':'',
            'item_length':'',
            'item_heigth':'',
            'item_width':'',
            'item_dimensions_unit_of_measure':'IN',
            'item_weight':'',
            'item_weight_unit_of_measure':'LB',
            'bullet_point1':'',
            'bullet_point2':'',
            'bullet_point3':'',
            'bullet_point4':'',
            'bullet_point5':'',
            'recommended_browse_nodes':'',
            'generic_keywords':'',
            'style_keywords1':'',
            'style_keywords2':'',
            'style_keywords3':'',
            'main_image_url':'',
            'other_image_url1':'',
            'other_image_url2':'',
            'other_image_url3':'',
            'swatch_image_url':'',
            'parent_child':'parent',
            'parent_sku':'',
            'relationship_type':'',
            'variation_theme':'',
            'safety_warning':'',
            'legal_disclaimer_description':'',
            'strap_type':'',
            'style_name':'',
            'department_name': '',
            'outer_material_type1':'',
            'outer_material_type2':'',
            'inner_material_type1':'',
            'inner_material_type2':'',
            'material_composition':'',
            'closure_type':'',
            'lifestyle1':'',
            'lifestyle2':'',
            'lifestyle3':'',
            'seasons':'',
            'material_type1':'',
            'material_type2':'',
            'are_batteries_included':'',
            'battery_cell_composition':'',
            'lithium_battery_weight':'',
            'warranty_type':'',
            'warranty_description':'',
            'occasion_type1':'',
            'occasion_type2':'',
            'care_instructions':'',
            'sole_material':'',
            'heel_type':'',
            'toe_style':'',
            'arch_type':'',
            'color_name':'',
            'size_name':'',
            'collection_name':'',
            'sport_type':''}
    
    soup = BeautifulSoup(get_html(product_link), 'html5lib')
    empty = []
    
    try:
        brand = soup.find('a', id = 'brand').get('href').split('/')[1]
    except:
        brand = ' '
    with open('accepted_brand.csv', 'r') as f:
        list_ab = []
        reader = csv.reader(f)
        accepted_brands = list(reader)
        for row in accepted_brands:
            list_ab.append(row[0])
    with open('Restricted-Brands.csv', 'r') as f:
        list_rb = []
        reader = csv.reader(f)
        restricted_brands = list(reader)
        for row in restricted_brands:
            list_rb.append(row[0])
    if brand in list_ab and brand not in list_rb:
        data['brand_name'] = brand
    else: 
        return empty
    
    try:
        name = soup.find('span', id = 'productTitle').text.strip()
    except: 
        name= ''
    
    try:
        ASIN = get_ASIN(product_link)
    except:
        ASIN = ''
    with open('Restricted-Asins.csv', 'r') as f:
        reader = csv.reader(f)
        restricted_asins = list(reader)
        list_ra = ''.join(str(x) for x in restricted_asins)
    if ASIN not in list_ra:
        data['external_product_id'] = ASIN
    else:
        return empty
    bullets = []
    try:
        for i in soup.find('ul', class_ = 'a-unordered-list a-vertical a-spacing-none').findAll('li'):
            bullets.append(i.text.strip())
    except: bullets = []
    try:desc = soup.find('p').text.strip()
    except: desc = ' '  
    
    with open('Restricted-Keywords.csv', 'r') as f:
        restricted_kw = []
        reader = csv.reader(f)
        l = list(reader)
        for row in l:
            restricted_kw.append(row[0]) 
    for rkw in restricted_kw:
        if rkw in name:
            return empty
           
    imgs = []
    for i in soup.findAll('span', class_ = 'a-button-text'):
        a = i.find('img')
        if a != None:
            imgs.append(a['src'])
    if 'Men' or 'Boy' in name:
        department_name = 'Men'
    else:
        department_name = 'Women'
    
    data['item_name'] = name
    data['part_number'] = 'LYS'+ ASIN + '-' +get_code(url)
    data['item_sku'] = 'LYS'+ ASIN + '-'+ get_code(url)
    data['external_product_id'] = ASIN
    data['department_name'] = department_name
    data['lifestyle1'] = 'Casual'
    data['outer_material_type1'] = "Synthetic"
    data['outer_material_type2'] = "Mesh"
    data['variation_theme'] = 'SizeName-ColorName'
    data['product_description'] = desc
    data['manufacturer'] = brand
    data['generic_keywords'] = name
    data['main_image_url'] = imgs[0]
    data['other_image_url1'] = imgs[1]
    data['other_image_url2'] = imgs[2]
    data['other_image_url3'] = imgs[3]
    data['bullet_point1'] = bullets[0]
    data['bullet_point2'] = bullets[1]
    data['bullet_point3'] = bullets[2]
    
    return list(data.values())
def get_ASIN(product_link):
    soup = BeautifulSoup(get_html(product_link), 'html5lib')
    for i in soup.findAll('span', class_='a-text-bold'):
        if 'ASIN' in i.text.strip():
            asin = i.find_next_sibling('span').text
        else:
            continue
    return asin
    

def get_variations(url, product_link):
    var_page = 'https://www.amazon.com/gp/offer-listing/'+get_ASIN(product_link) + '?ie=UTF8&condition=new'
    var_links = get_variations_links(url, product_link)
    soup = BeautifulSoup(get_html(var_page), 'html5lib')
    variations = []
    
    
    sellers = []
    for i in soup.findAll("h3", class_ ='a-spacing-none olpSellerName'):
        try:
            if i.find('a').text.strip() == '' or i.find('a').text.strip() == None:
                sellers.append('Amazon')
            else:
                sellers.append(i.find('a').text.strip())
        except:
            sellers.append('Amazon')
    
    standard_prices = []
    for i in soup.findAll('span', class_ = 'a-size-large a-color-price olpOfferPrice a-text-bold'):
        standard_prices.append(i.text.strip())
    
      
    for i in range(0, len(sellers)):
        product = get_product_info(url, product_link) 
        if product == None:
            try:
                product = get_product_info(url, product_link)
            except:
                continue
            
        soup2 = BeautifulSoup(get_html(var_links[i]), 'html5lib')
        new_ASIN = var_links[i].split('offer-listing/')[1].split('/')[0]    
        for k in soup2.findAll('h1', class_ = 'a-size-large a-spacing-none'):
            if k != None:
                new_name = k.text.strip()
                pass
            else:
                new_name = ''
        
        color_size = []
        for j in soup2.findAll('span', class_ = 'a-dropdown-prompt'):
            if j != None:
                color_size.append(j.text.strip())
                pass
            else:
                color_size = ''
        new_imgs = []
        for n in soup2.findAll('a', id = 'olpDetailPageLink'):
            if n != None:
                prod_page = n.get('href')
                soup3 = BeautifulSoup(get_html(prod_page), 'html5lib')
                for y in soup3.findAll('span', class_ = 'a-button-text'):
                    a = y.find('img')
                    if a != None:
                        new_imgs.append(a['src'])
        
        with open('accepted_seller.csv', 'r') as f:
            reader = csv.reader(f)
            accepted_sellers = list(reader)
            list_as = ''.join(str(x) for x in accepted_sellers)
        if sellers[i] in list_as:    
            product[0] = sellers[i]
            product[2] = 'LYS'+new_ASIN+'-'+get_code(url)
            product[3] = new_ASIN
            product[7] = new_name
            product[13] = standard_prices[i]
            product[46] = new_imgs[0]
            product[47] = new_imgs[1]
            product[48] = new_imgs[2]
            product[49] = new_imgs[3]
            product[51] = 'child'
            product[84] = color_size[1]
            product[85] = color_size[0]
            variations.append(product)
        else:
            product = []
        
    return variations
def get_variations_links(url, product_link):
    var_page = 'https://www.amazon.com/gp/offer-listing/'+get_ASIN(product_link) + '?ie=UTF8&condition=new'
    soup = BeautifulSoup(get_html(var_page), 'html5lib')
    var_links = []
    for i in soup.findAll('a', class_ = 'a-link-normal', attrs={'href': re.compile('/gp/offer-listing/')}):
        var_links.append('https://www.amazon.com' + i.get('href'))
    return var_links    
def get_prod_descr(product_link):
    description = []
    soup = BeautifulSoup(get_html(product_link), 'html5lib')
    try:
        text = soup.find('p').text
    except:
        text = ''
    description.append(text)
    try:
        for i in soup.find('div', id ='detailBullets_feature_div').findAll('span', class_ = 'a-list-item'):
            for d in i.findAll('span'):
                description.append(d.text.split('\n'))
    except:
        return
    return description

def write_to_csv(data):
    with open('amazon_test.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(data)
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
def get_product_links_single_page(page_url):
    links = []
    soup = BeautifulSoup(get_html(page_url), 'html5lib')
    for k in soup.findAll('div', class_ = 'a-row a-gesture a-gesture-horizontal'):
        links.append(k.find('a', class_ = 'a-link-normal a-text-normal').get('href'))
            
    with open('1.csv', 'a') as f:
            writer = csv.writer(f)
            for item in links:
                writer.writerow([item])
    return links
def write_titles():
    with open('amazon_test.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(titles)
        
def make_all(product_link):
    #product_links = get_product_links(start_url)
    product = get_product_info(URL, product_link)
    variations = get_variations(URL, product_link)
    print(product)
    if product != []:
        write_to_csv(product)
    else:
        pass
    for item in variations:
        if product != []:
            write_to_csv(item)
        else:
            pass
        
            
def read_product_links():
    with open('1.csv', 'r') as f:
        product_links = []
        reader = csv.reader(f)
        l = list(reader)
        for row in l[0::2]:
            product_links.append(row[0])
    return product_links

def main():
    
    write_titles()
    make_all('https://www.amazon.com/Saucony-Jazz-Sneaker-Toddler-Periwinkle/dp/B00ZXQV2TY/ref=sr_1_1?s=apparel&ie=UTF8&qid=1501876479&sr=8-1&keywords=Saucony+Jazz+Hook+%26+Loop+Sneaker+%28Toddler%2FLittle+Kid%29')
    
    
if __name__ == '__main__':
    main()
