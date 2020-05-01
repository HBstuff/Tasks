from car import Car
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import json

# what number of pages to read
num = 5

# first page url
my_url = 'https://en.autoplius.lt/ads/used-cars?make_id=99'

loop_count = 0

car_list = []
for number in range(num):
    # read page
    uClient = uReq(my_url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")
    products = page_soup.findAll('a', {'class': 'announcement-item'})

    # main loop
    for product in products:
        # info from main page (make, model, mileage, price)
        try:
            name = product.findAll('div', {'class': 'announcement-title'})[0].getText(strip=True)
            make = name.split(',')[0].strip()
            model = name.split(',')[-1].strip()
        except:
            make = None
            model = None
        try:
            km = product.findAll('span', {'title': 'Mileage'})[0].getText(strip=True)
            mileage = km.replace(' km', '').replace(' ', '')
        except:
            mileage = None
        try:
            eu = product.strong.getText()
            price = eu.replace(' €', '').replace(' ', '')
        except:
            price = None

        # read car page
        link = product.get('href')
        uCli = uReq(link)
        feats_html = uCli.read()
        uCli.close()
        new_page_soup = soup(feats_html, "html.parser")

        # get FEATURES/EQUIPMENT
        feats = {}
        all_features = new_page_soup.findAll('div', {'class': 'feature-row'})
        if all_features:
            for categ in all_features:
                entry = []
                category = categ.findAll('div', {'class': 'feature-label'})[0].getText(strip=True)
                features = categ.findAll('span', {'class': 'feature-item'})
                for feature in features:
                    entry.append(feature.getText(strip=True))
                    upd = {category: entry}
                    feats.update(upd)
        else:
            upd = {'Features': None}
            feats.update(upd)

        # create list of objects
        car_list.append(Car(make, model, mileage, price, feats))

        loop_count += 1
        print('Fetching car: ' + str(loop_count))

    # find link to the next page
    next_button = page_soup.find('a', {'class': 'next'})
    link = next_button.get('href')
    my_url = 'https://en.autoplius.lt' + link

# write JSON
with open('information.json', 'w') as f:
    file_content = {}
    cars = []
    for item in car_list:
        data = {
            'Make': item.make,
            'Model': item.model,
            'Mileage': item.mileage,
            'Price': item.price,
            'Features': item.feats,
        }
        cars.append(data)
    file_content.update({'car': cars})
    json.dump(file_content, f, indent=2)

# output statistics
with open('information.json', 'r') as f:
    data = json.load(f)
    # make a list of cars from json file
    car_list = []
    for car in data['car']:
        car_list.append([car['Make'] + ' ' + car['Model'], car['Mileage'], car['Price'], car['Features']])
    unique_car_list = []
    # find unique cars
    for unique_car in car_list:
        if unique_car[0] not in unique_car_list:
            unique_car_list.append(unique_car[0])
    print('There are ' + str(len(unique_car_list)) + ' unique cars.')
    with open('stats.txt', 'a', encoding='utf8') as txt_f:
        txt_f.write('There are ' + str(len(unique_car_list)) + ' unique cars.\n')
    # amount of each car and statistics of each unique car
    for car in unique_car_list:
        t = 0
        total_price = 0
        total_mileage = 0
        total_features = 0
        cars_with_price = 0
        cars_with_mileage = 0
        cars_with_features = 0
        for match in car_list:
            if car == match[0]:
                t += 1
                if match[1] is not None:
                    cars_with_mileage += 1
                    total_mileage = total_mileage + int(match[1])
                if match[2] is not None:
                    cars_with_price += 1
                    total_price = total_price + int(match[2])
                for feature in match[3]:
                    if feature is not None:
                        cars_with_features += 1
                        total_features = total_features + len(feature)
        if cars_with_mileage > 0:
            avg_mileage = round(total_mileage/cars_with_mileage, 2)
        else:
            avg_mileage = 'N/A'
        if cars_with_price > 0:
            avg_price = round(total_price/cars_with_price, 2)
        else:
            avg_price = 'N/A'
        if cars_with_features > 0:
            avg_features = round(total_features/cars_with_features, 2)
        else:
            avg_features = 'N/A'
        print(car + ' - total cars: ' + str(t) + ', with an average price of: ' + str(avg_price)
              + '€, an average mileage of: ' + str(avg_mileage) + ' and it has ' + str(avg_features)
              + ' average features.')
        with open('stats.txt', 'a', encoding='utf8') as txt_f:
            txt_f.write(car + ' - total cars: ' + str(t) + ', with an average price of: ' + str(avg_price)
              + '€, an average mileage of: ' + str(avg_mileage) + ' and it has ' + str(avg_features)
              + ' average features.\n')
