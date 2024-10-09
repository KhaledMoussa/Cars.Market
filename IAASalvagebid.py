import math

from selenium.common import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver import ChromeOptions, Chrome, Keys
from selenium.webdriver.common.by import By
from time import sleep
import scrapy
from multiprocessing import Process
from Chrome import run_debugger_browser, terminate_chrome, remove_user_chrome
import csv
import pandas as pd
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime

headers_csv = ['Handle', 'Title', 'Body (HTML)', 'Vendor', 'Product Type', 'Type', 'Tags', 'Published', 'Option1 Name',
               'Option1 Value', 'Option2 Name', 'Option2 Value', 'Option3 Name', 'Option3 Value', 'Option4 Name',
               'Option4 Value',
               'Variant SKU', 'Odometer', 'Odometer Status', 'Manufactured in', 'Vehicle Class', 'Body Style',
               'Vehicle',
               'Variant Inventory Tracker', 'Variant Inventory Qty', 'Variant Inventory Policy', 'Engine',
               'Transmission',
               'Variant Fulfillment Service', 'Variant Price', 'Variant Requires Shipping', 'Variant Barcode',
               'Mileage', 'Google Product Category', 'Custom Product',
               'Image Src', 'Image Position', 'carTitle', 'Cylinders', 'Start Code', 'Airbags', 'Loss Type', 'Series',
               'Fuel Type',
               'Exterior/Interior', 'Options', 'Damage', 'Car Location', 'Stock #', 'Year', 'Drive Line Type',
               'Primary Damage', 'Secondary Damage', 'Price', 'Key', 'Make', 'Restraint System', 'Model', 'Vin']
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
csv_file_name = f"iaai_data_{timestamp}.csv"
csvfile = open(csv_file_name, 'w', newline='', encoding='utf-8-sig')
writer = csv.DictWriter(csvfile, fieldnames=headers_csv)
if csvfile.tell() == 0:
    writer.writeheader()
    csvfile.flush()


def start_driver():
    options = ChromeOptions()
    options.add_argument("--headless=new")
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = Chrome(options=options)
    driver.implicitly_wait(0.5)
    return driver


def start_browser_process():
    process = Process(target=run_debugger_browser)
    process.start()
    return process


def calculateFinalPrice(price):
    profit = 1000
    constantFees = 400

    #########Calculating Variable Fees Below##################

    if price < 50:
        price = price + 25
    elif price < 100:
        price = price + 45
    elif price < 200:
        price = price + 130
    elif price < 300:
        price = price + 180
    elif price < 350:
        price = price + 200
    elif price < 400:
        price = price + 210
    elif price < 450:
        price = price + 220
    elif price < 500:
        price = price + 230
    elif price < 550:
        price = price + 260
    elif price < 600:
        price = price + 265
    elif price < 700:
        price = price + 295
    elif price < 800:
        price = price + 320
    elif price < 900:
        price = price + 340
    elif price < 1000:
        price = price + 365
    elif price < 1200:
        price = price + 435
    elif price < 1300:
        price = price + 460
    elif price < 1400:
        price = price + 480
    elif price < 1500:
        price = price + 490
    elif price < 1600:
        price = price + 510
    elif price < 1700:
        price = price + 530
    elif price < 1800:
        price = price + 540
    elif price < 2000:
        price = price + 555
    elif price < 2400:
        price = price + 600
    elif price < 2500:
        price = price + 625
    elif price < 3000:
        price = price + 650
    elif price < 3500:
        price = price + 750
    elif price < 4000:
        price = price + 800
    elif price < 4500:
        price = price + 835
    elif price < 5000:
        price = price + 860
    elif price < 6000:
        price = price + 885
    elif price < 7000:
        price = price + 940
    elif price < 8000:
        price = price + 965
    elif price < 10000:
        price = price + 1000
    elif price < 15000:
        price = price + 1050
    elif price >= 15000:
        price = price + math.ceil(price * 0.075)

    price = price + profit + constantFees
    return price


def parsing_function(driver):
    # scrapy response

    resp_main = scrapy.Selector(text=driver.page_source)
    main_window_handle = driver.current_window_handle
    pageNum = 1
    driver.get(
        'https://www.salvagebid.com/search?destination_zip=08837&distance=200&page=' + str(
            pageNum) + '&per_page=100&sales_type=buy_it_now')

    time.sleep(3)

    whileLoop = True
    while whileLoop:

        carContOuter = driver.find_element(By.CLASS_NAME, 'search-result')
        carCont = carContOuter.find_element(By.CLASS_NAME, 'result-list')
        cars = carCont.find_elements(By.CLASS_NAME, 'result-container')

        print(len(cars))

        carsDict = {}

        for car in cars:
            try:
                engine = car.find_element(By.CLASS_NAME, 'engine').text.splitlines()[1]
            except:
                engine = 'No engine'
            carTitle = car.find_element(By.CLASS_NAME, 'title').text.splitlines()[1]

            if (engine == 'Run & Drive') and (("CLEAR" in carTitle) or ("ORIGINAL" in carTitle)):
                # item id
                itemId = car.find_element(By.CLASS_NAME, 'result-item').get_attribute('id')
                print(itemId)

                # the url link
                itemLink = car.find_element(By.XPATH, '//*[@id="' + itemId + '"]/div[2]/div/h3/a').get_attribute('href')
                print(itemLink)

                # The car price
                carPrice = car.find_elements(By.CLASS_NAME, 'ellipsis')[1].text
                carPrice = carPrice.replace('$', '')
                carPrice = carPrice.replace('USD', '')
                carPrice = carPrice.replace(' ', '')
                carPrice = int(carPrice.replace(',', ''))

                carsDict['Price'] = calculateFinalPrice(carPrice)

                # car odometer
                odometer = int(
                    car.find_element(By.CLASS_NAME, 'odometer').text.splitlines()[1].replace('MI', '').replace(',',
                                                                                                               '').strip())
                carsDict['Mileage'] = odometer

                # car title
                carTitle = car.find_element(By.CLASS_NAME, 'title').text.splitlines()[1]

                # car damage
                damage = car.find_element(By.CLASS_NAME, 'damage').text.splitlines()[1]

                carsDict['Damage'] = damage

                # car location
                carLocation = car.find_element(By.CLASS_NAME, 'location').text.splitlines()[1]

                carsDict['Car Location'] = carLocation

                # getting specific car page
                originalWindow = driver.current_window_handle
                driver.switch_to.new_window('tab')
                driver.get(itemLink)
                time.sleep(3)

                # pulling data from car page
                try:
                    yearMake = driver.find_element(By.CLASS_NAME, 'lot-page-title').text.split(' ')
                except NoSuchElementException:
                    continue
                carYear = yearMake[0]
                carMake = yearMake[1]
                carsDict['Year'] = carYear
                carsDict['Product Type'] = carMake
                carsDict['Make'] = carMake
                carsDict['Options'] = 'N/A'

                carDetails1 = driver.find_element(By.CLASS_NAME, 'vin-details').text.splitlines()
                carDetails1.pop(0)  # delete "VIN DETAILS?"
                carDetails1.pop(2)  # delete "Get Full History Report"
                carDetails1[0] = 'Vin'
                print(carDetails1)

                for i in range(int(len(carDetails1) / 2)):
                    carsDict[carDetails1[0].strip()] = carDetails1[1].strip()
                    carDetails1.pop(0)
                    carDetails1.pop(0)
                carDetails2 = driver.find_element(By.CLASS_NAME, 'condition-details').text
                # '//*[@id="spa-react-root"]/div/div/div[2]/article/div[1]/div[3]').text

                print(carDetails2)
                carDetails2 = carDetails2.splitlines()

                carDetails2[0] = str(carDetails2[0]).replace('IAA CONDITION DETAILS STOCK# ', '')
                carDetails2[0] = str(carDetails2[0]).replace('?', '').strip()
                stockNum = carDetails2[0]
                carsDict['Stock #'] = stockNum
                carsDict['Secondary Damage'] = 'N/A'
                carDetails2.pop(0)
                for i in range(int(len(carDetails2) / 2)):
                    carsDict[carDetails2[0].strip()] = carDetails2[1].strip()
                    carDetails2.pop(0)
                    carDetails2.pop(0)
                print(carDetails2)

                carsDict['Odometer Status'] = carsDict['Odometer'].split('(')[1].replace(')', '')

                # print(carDetails2)
                # print(carDetails1)

                carDetails3 = driver.find_element(By.CLASS_NAME, 'sale-info').text.lower()
                carDetails3 = carDetails3.splitlines()
                # print(carDetails3)
                if 'title/sale doc brand' in carDetails3:
                    carTitle = str(carTitle) + str(
                        ' (' + carDetails3[carDetails3.index('title/sale doc brand') + 1].upper() + ')')

                carsDict['carTitle'] = carTitle
                if (('CLEAR' in carTitle) or ('ORIGINAL' in carTitle)) and (
                        ('SALV' not in carTitle) and ('907' not in carTitle)):
                    if ('REBUILT' not in carTitle) and ('RECON' not in carTitle):
                        carsDict['Tags'] = 'Clean Title'
                    else:
                        carsDict['Tags'] = 'Rebuilt Title'
                elif ('REBUILT' in carTitle) or ('RECON' in carTitle):
                    carsDict['Tags'] = 'Rebuilt Title'
                elif 'UNKNOWN SALVAGE HISTORY' not in carTitle:
                    carsDict['Tags'] = 'Possible Salvage History'
                else:
                    carsDict['Tags'] = 'Clean Title'
                print(carsDict['Tags'])
                # print("car detail 3: "+str(carDetails3))

                carsDict['Primary Damage'] = carsDict['Primary Damage'].replace('?', '')
                carsDict['Start Code'] = carsDict['Start Code'].replace('?', '')

                # Writting to file

                try:
                    carsDict['Title'] = carsDict['Year'] + ' ' + carsDict['Make'] + ' ' + carsDict['Model']
                except:
                    pass
                    a = 1

                try:
                    carsDict['Handle'] = carsDict['Year'] + carsDict['Make'] + '-' + carsDict['Stock #']
                except:
                    pass
                    a = 1

                carsDict['Google Product Category'] = '916'
                carsDict['Custom Product'] = 'TRUE'

                try:
                    carsDict['Published'] = 'True'
                except:
                    pass
                    a = 1

                try:
                    carsDict['Variant SKU'] = carsDict['Stock #']
                except:
                    pass
                    a = 1

                try:
                    carsDict['Option1 Name'] = 'Year'
                except:
                    pass
                    a = 1
                try:
                    carsDict['Option1 Value'] = int(carsDict['Year'])
                except:
                    pass
                    a = 1

                try:
                    carsDict['Option2 Name'] = 'Model'
                except:
                    pass
                    a = 1
                try:
                    carsDict['Option2 Value'] = carsDict['Model']
                except:
                    pass
                    a = 1

                try:
                    carsDict['Option3 Name'] = 'Mileage'
                except:
                    pass
                    a = 1
                try:
                    carsDict['Option3 Value'] = carsDict['Mileage']
                except:
                    pass
                    a = 1
                try:
                    carsDict['Option4 Name'] = 'Odometer Status'
                except:
                    pass
                    a = 1
                try:
                    carsDict['Option4 Value'] = carsDict['Odometer Status']
                except:
                    pass
                    a = 1

                try:
                    carsDict['Variant Inventory Tracker'] = "shopify"
                except:
                    pass
                    a = 1
                try:
                    carsDict['Variant Inventory Qty'] = "1"
                except:
                    pass
                    a = 1
                try:
                    carsDict['Variant Inventory Policy'] = "deny"
                except:
                    pass
                    a = 1
                try:
                    carsDict['Variant Fulfillment Service'] = "manual"
                except:
                    pass
                    a = 1
                try:
                    carsDict['Variant Price'] = carsDict['Price']
                except:
                    pass
                    a = 1
                try:
                    carsDict['Variant Requires Shipping'] = "TRUE"
                except:
                    pass
                    a = 1

                try:

                    carsDict['Body (HTML)'] = f'''<ul class="data-list data-list--details" data-mce-fragment="1">
                              <li>
                              <strong><span class="data-list__value" data-mce-fragment="1">Being sold As-is only</span></strong>
                              </li>
                              <li class="data-list__item" data-mce-fragment="1">
                              <span class="data-list__label" data-mce-fragment="1">Vendor: </span><strong><span class="data-list__value" data-mce-fragment="1">{'Cars.market'}</span></strong>
                              </li>
                              <li class="data-list__item" data-mce-fragment="1">
                              <span class="data-list__label" data-mce-fragment="1">Vehicle Type: </span><strong><span class="data-list__value" data-mce-fragment="1">{carsDict['Vehicle Class']} </span></strong>
                              </li>
                              <li class="data-list__item" data-mce-fragment="1">
                              <span class="data-list__label" data-mce-fragment="1">Make: </span><strong><span class="data-list__value" data-mce-fragment="1">{carsDict['Make']} </span></strong>
                              </li>
                              <li class="data-list__item" data-mce-fragment="1">
                              <span class="data-list__label" data-mce-fragment="1">Model: </span><strong><span class="data-list__value" data-mce-fragment="1">{carsDict['Model']} </span></strong>
                              </li>
                              <li class="data-list__item" data-mce-fragment="1">
                              <span class="data-list__label" data-mce-fragment="1">Year: </span><strong><span class="data-list__value" data-mce-fragment="1">{carsDict['Year']} </span></strong>
                              </li>
                              <li class="data-list__item" data-mce-fragment="1">
                              <span class="data-list__label" data-mce-fragment="1">Car Location: </span><strong><span class="data-list__value" data-mce-fragment="1">{carsDict['Car Location']} </span></strong>
                              </li>
                              <li class="data-list__item" data-mce-fragment="1">
                              <span class="data-list__label" data-mce-fragment="1">Loss: </span><strong><span class="data-list__value" data-mce-fragment="1">{carsDict['Loss Type']} </span></strong>
                              </li>
                              <li class="data-list__item" data-mce-fragment="1">
                              <span class="data-list__label" data-mce-fragment="1">Primary Damage: </span><strong><span class="data-list__value" data-mce-fragment="1">{carsDict['Primary Damage']} </span></strong>
                              </li>
                              <li class="data-list__item" data-mce-fragment="1">
                              <span class="data-list__label" data-mce-fragment="1">Secondary Damage: </span><strong><span class="data-list__value" data-mce-fragment="1">{carsDict['Secondary Damage']} </span></strong>
                              </li>
                              <li class="data-list__item" data-mce-fragment="1">
                              <span class="data-list__label" data-mce-fragment="1">Title/Sale Doc: </span><strong><span class="data-list__value" data-mce-fragment="1">{carsDict['carTitle']} </span></strong>
                              </li>
                              <li class="data-list__item" data-mce-fragment="1">
                              <span class="data-list__label" data-mce-fragment="1">Start Code: </span><strong><span class="data-list__value" data-mce-fragment="1">{carsDict['Start Code']}</span></strong>
                              </li>
                              <li class="data-list__item" data-mce-fragment="1">
                              <span class="data-list__label" data-mce-fragment="1">Key: </span><strong><span class="data-list__value" data-mce-fragment="1">{carsDict['Key']} </span></strong>
                              </li>
                              <li class="data-list__item" data-mce-fragment="1">
                              <span class="data-list__label" data-mce-fragment="1">Odometer: </span><strong><span class="data-list__value" data-mce-fragment="1">{carsDict['Odometer']} </span></strong>
                              </li>
                              <li class="data-list__item" data-mce-fragment="1">
                              <span class="data-list__label" data-mce-fragment="1">Airbags : </span><strong><span class="data-list__value" data-mce-fragment="1">{carsDict['Airbags']} </span></strong>
                              </li>
                              <li class="data-list__item" data-mce-fragment="1">
                              <span class="data-list__label" data-mce-fragment="1">BodyStyle: </span><strong><span class="data-list__value" data-mce-fragment="1">{carsDict['Body Style']} </span></strong>
                              </li>
                              <li class="data-list__item" data-mce-fragment="1">
                              <span class="data-list__label" data-mce-fragment="1">Engine: </span><strong><span class="data-list__value" data-mce-fragment="1">{carsDict['Engine']} </span></strong>
                              </li>
                              <li class="data-list__item" data-mce-fragment="1">
                              <span class="data-list__label" data-mce-fragment="1">Fuel Type: </span><strong><span class="data-list__value" data-mce-fragment="1">{carsDict['Fuel Type']} </span></strong>
                              </li>
                              <li class="data-list__item" data-mce-fragment="1">
                              <span class="data-list__label" data-mce-fragment="1">Cylinders: </span><strong><span class="data-list__value" data-mce-fragment="1">{carsDict['Cylinders']} </span></strong>
                              </li>
                              <li class="data-list__item" data-mce-fragment="1">
                              <span class="data-list__label" data-mce-fragment="1">Transmission: </span><strong><span class="data-list__value" data-mce-fragment="1">{carsDict['Transmission']} </span></strong>
                              </li>
                              <li class="data-list__item" data-mce-fragment="1">
                              <span class="data-list__label" data-mce-fragment="1">Driveline: </span><strong><span class="data-list__value" data-mce-fragment="1">{carsDict['Drive Line Type']} </span></strong>
                              </li>
                              <li class="data-list__item" data-mce-fragment="1">
                              <span class="data-list__label" data-mce-fragment="1">VIN: </span><strong><span class="data-list__value" data-mce-fragment="1">{carsDict['Vin']} </span></strong>
                              </li>
                              </ul>'''

                except:
                    pass
                    a = 1

                # getting images
                images = []
                popupNotOpen = True
                while popupNotOpen:

                    try:

                        largeImagebtnCont = driver.find_element(By.CLASS_NAME, 'lot-page-gallery')
                        largePicButtton = largeImagebtnCont.find_element(By.CLASS_NAME, 'large-photo-btn')
                        driver.implicitly_wait(3)
                        largePicButtton.click()
                        driver.implicitly_wait(3)
                    except (NoSuchElementException, ElementClickInterceptedException) as e:
                        print("unable to view large image button")
                        continue

                    print('large image btn clicked')

                    popup = driver.find_elements(By.CLASS_NAME, 'popup-content')
                    print(popup)

                    if popup:
                        popupNotOpen = False
                    else:
                        try:
                            popup = driver.find_element(By.CLASS_NAME, 'popup-content')
                        except NoSuchElementException:
                            largePicButtton.click()

                imagesCont = driver.find_element(By.CLASS_NAME, 'lot-page-photos-modal')
                imagesCont2 = imagesCont.find_element(By.CLASS_NAME, 'lot-page-photos-modal-content')
                imagesCont3 = imagesCont2.find_element(By.CLASS_NAME, 'lot-page-photos-modal-images')

                imagesList = imagesCont3.find_elements(By.CSS_SELECTOR, 'img')
                for img in imagesList:
                    img = img.get_attribute('src')

                    print(img)
                    images.append(img)

                counter = 1
                flag1 = 1
                for image in images:

                    try:
                        carsDict['Image Src'] = image
                        carsDict['Image Position'] = f"{counter}"
                        counter += 1
                    except:
                        pass
                    carsDict['Image Src'] = image.strip()
                    if flag1 == 1:
                        writer.writerow(carsDict)
                        csvfile.flush()
                        flag1 = 2
                    else:
                        item2 = dict()
                        item2['Handle'] = carsDict['Handle']
                        item2['Image Src'] = image
                        if item2['Image Src'] != '':
                            item2['Image Position'] = f"{counter - 1}"
                            writer.writerow(item2)
                            csvfile.flush()
                            print(item2)
                        else:
                            counter -= 1
                            pass
                carsDict.clear()

                driver.close()

                driver.switch_to.window(originalWindow)


            else:
                print('stationary car')

        pageNum += 1
        nextPageLink = 'https://www.salvagebid.com/search?destination_zip=08837&distance=200&page=' + str(
            pageNum) + '&per_page=100&sales_type=buy_it_now'

        driver.get(nextPageLink)
        driver.implicitly_wait(3)
        try:
            driver.find_element(By.CLASS_NAME, 'search-not-found')
            whileLoop = False
        except NoSuchElementException:
            pass

    print('Program finished successfully')
    driver.close()


def main():
    process = start_browser_process()
    driver = start_driver()
    # singleCar(driver)
    parsing_function(driver)


if __name__ == '__main__':
    main()
