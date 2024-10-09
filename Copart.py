import math
from faulthandler import is_enabled

from selenium.common import NoSuchElementException, ElementClickInterceptedException, TimeoutException, \
    ElementNotInteractableException, StaleElementReferenceException
from selenium.webdriver import ChromeOptions, Chrome, Keys
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.by import By
from time import sleep
from selenium import webdriver

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
               'Vehicle', 'Seller', 'Google Product Category', 'Custom Product',
               'Variant Inventory Tracker', 'Variant Inventory Qty', 'Variant Inventory Policy', 'Engine',
               'Transmission', 'Has Engine?',
               'Variant Fulfillment Service', 'Variant Price', 'Variant Requires Shipping', 'Variant Barcode',
               'Mileage','Estimated Retail Value',
               'Image Src', 'Image Position', 'carTitle', 'Cylinders', 'Start Code', 'Airbags', 'Loss Type', 'Series',
               'Fuel Type', 'Interior Color', 'Exterior Color', 'Trim', 'Notes',
               'Exterior/Interior', 'Options', 'Damage', 'Car Location', 'Stock #', 'Year', 'Drive Line Type',
               'Primary Damage', 'Secondary Damage', 'Price', 'Key', 'Make', 'Restraint System', 'Model', 'Vin']
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
csv_file_name = f"copart_data_{timestamp}.csv"
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

def pageGetter(pgNum):
    driver = start_driver()
    for i in range(pgNum-1):
        try:
            footer = driver.find_element(By.CLASS_NAME, "p-paginator-bottom")
            driver.execute_script("arguments[0].scrollIntoView();", footer)
            driver.implicitly_wait(3)
            nextPageBTN = driver.find_element(By.CLASS_NAME, 'p-paginator-next')
            driver.implicitly_wait(1)
            nextPageBTN.click()
            driver.implicitly_wait(3)
        except:
            driver.execute_script("arguments[0].scrollIntoView();", nextPageBTN)
            driver.implicitly_wait(1)
            nextPageBTN.click()


def parsing_function(driver):
    # scrapy response

    resp_main = scrapy.Selector(text=driver.page_source)
    main_window_handle = driver.current_window_handle
    LastPage = False
    driver.get(
        'https://www.copart.com/lotSearchResults?free=false&displayStr=Search%20vehicles&from=%2FvehicleFinder&fromSource=widget&searchCriteria=%7B%22query%22:%5B%22*%22%5D,%22filter%22:%7B%22ODM%22:%5B%22odometer_reading_received:%5B0%20TO%209999999%5D%22%5D,%22YEAR%22:%5B%22lot_year:%5B1920%20TO%202025%5D%22%5D,%22MISC%22:%5B%22%23LocRange:%7B%5C%22latitude%5C%22:40.518491,%5C%22longitude%5C%22:-74.349682,%5C%22miles%5C%22:%5C%22200%5C%22,%5C%22zip%5C%22:%5C%2208837%5C%22%7D%22%5D,%22TITL%22:%5B%22title_group_code:TITLEGROUP_C%22%5D,%22FETI%22:%5B%22buy_it_now_code:B1%22,%22lot_condition_code:CERT-D%22%5D,%22VEHT%22:%5B%22veh_cat_code:VEHCAT_S%22,%22vehicle_type_code:VEHTYPE_V%22%5D%7D,%22searchName%22:%22%22,%22watchListOnly%22:false,%22freeFormSearch%22:false%7D')
    time.sleep(3)

    pageGetter(0)



    while not LastPage:

        footer = driver.find_element(By.CLASS_NAME, "p-paginator-bottom")
        driver.execute_script("arguments[0].scrollIntoView();", footer)
        driver.implicitly_wait(3)
        nextPageBTN = driver.find_element(By.CLASS_NAME, 'p-paginator-next')

        if not nextPageBTN.is_enabled():
            LastPage = True

        moreCarsPerPageBTN = driver.find_element(By.CLASS_NAME, 'p-paginator-rpp-options')
        moreCarsPerPageBTN.click()
        time.sleep(3)
        hundredBTN = driver.find_element(By.XPATH,
                                         '/html/body/div[3]/div[3]/div/app-root/lot-search-results/search-results/div/div[2]/div[2]/search-table-component/copart-table/div/p-table/div/p-paginator/div/p-dropdown/div/p-overlay/div/div/div/div/ul/p-dropdownitem[5]')
        hundredBTN.click()
        time.sleep(10)

        cars = driver.find_elements(By.CLASS_NAME, 'p-selectable-row')
        print(len(cars))

        unfetchedLinks = []
        originalWindow = driver.current_window_handle

        for car in cars[:]:

            lotNum = car.find_element(By.CLASS_NAME, 'search_result_lot_number').text
            itemLink = 'https://www.copart.com/lot/' + lotNum

            driver.switch_to.new_window('tab')
            driver.get(itemLink)

            # get specific car data here

            # getting images
            carsDict = {}

            #non variable assignments
            carsDict['Loss Type'] = 'N/A'
            carsDict['Airbags'] = 'N/A'
            carsDict['Secondary Damage'] = 'N/A'
            carsDict['Body Style'] = 'Unknown'
            carsDict['Car Location'] = 'N/A'
            carsDict['Stock #'] = 'N/A'
            carsDict['Drive'] = 'N/A'
            carsDict['VIN'] = 'N/A'
            carsDict['Title Code'] = 'N/A'
            carsDict['Engine Type'] = 'N/A'
            carsDict['Fuel'] = 'N/A'
            carsDict['Vehicle Type'] = 'N/A'

            images = []
            try:
                try:
                    WebDriverWait(driver, 20).until(
                        EC.visibility_of_element_located((By.CLASS_NAME, 'bid-information')))
                except:
                    driver.refresh()
                    print('refreshed page #1')
                    driver.implicitly_wait(10)
            except:

                print('Car skipped and added to unfetched list')
                unfetchedLinks.append(itemLink)
                driver.close()
                driver.switch_to(originalWindow)
                continue

            try:

                # imagesCont = driver.find_element(By.CLASS_NAME, 'thumbImgContainer')
                largePic = driver.find_element(By.XPATH, '//*[@id="show-img"]')
                imgHDbtn = driver.find_element(By.CLASS_NAME, 'view-hd')
                thumbnails = driver.find_elements(By.CLASS_NAME, 'thumbImgblock')

                regularImage = False
                for thumbnail in thumbnails:

                    try:
                        thumbnail.click()
                    except ElementClickInterceptedException:
                        try:
                            driver.execute_script("arguments[0].scrollIntoView();", thumbnail)
                            driver.implicitly_wait(1)
                            thumbnail.click()
                        except ElementClickInterceptedException:
                            print("skipped thumbnail")
                            continue
                    except StaleElementReferenceException:
                        print('stale thumb click')

                    if not regularImage:
                        try:
                            imgHDbtn.click()
                        except ElementNotInteractableException:
                            #driver.refresh()
                            print('HD button not interactable')
                            regularImage = True
                        except StaleElementReferenceException:
                            regularImage = True

                    try:
                        img = largePic.get_attribute('src')
                    except:
                        largePicCont = driver.find_element(By.CLASS_NAME,'spZoomImg')
                        largePic = largePicCont.find_element(By.ID,'show-img')
                        img = largePic.get_attribute('src')

                    while 'hrs.jpg' not in str(img) and regularImage == False:
                        try:
                            print('No HD image detected')
                            imgHDbtn.click()
                            print('HD Button Clicked')
                            img = largePic.get_attribute('src')
                        except:
                            regularImage = True
                            pass
                    # if regularImage:
                    #     img = largePic.get_attribute('src')

                    images.append(img)
                # if regularImage:
                #     viewAllBtn = driver.find_element(By.CLASS_NAME, 'view-all-photos')
                #     viewAllBtn.click()
                #     driver.implicitly_wait(3)
                #     imageWrapers = driver.find_elements(By.CLASS_NAME, 'viewAllPhotosRelative')
                #     for image in imageWrapers:
                #         img = image.get_attribute('src')
                #         images.append(img)
                #     backToLotBtn = driver.find_element(By.XPATH,'//*[@id="lot-images-wrapper"]/div/div[13]/a')
                #     backToLotBtn.click()
                # driver.implicitly_wait(3)

                carPrice = driver.find_elements(By.CLASS_NAME, 'bid-price')[1].text
                carsDict['Price'] = calculateFinalPrice(
                    int(carPrice.split('.')[0].replace(',', '').replace('$', '')))
                pgTitle = driver.find_element(By.CLASS_NAME, 'title').text
                carInfo = driver.find_element(By.CLASS_NAME, 'lot-information').text
                carInfo = carInfo.splitlines()
                carLocation = driver.find_element(By.XPATH,
                                                  '//*[@id="sale-information-block"]/div[2]/div[2]/span/a').text

                for line in carInfo:
                    if (':' in line) and ('According to the auction' not in line):
                        carsDict[line.replace(':', '')] = carInfo[carInfo.index(line) + 1]



            except NoSuchElementException:

                try:
                    pgTitle = driver.find_element(By.XPATH,
                                                  '//*[@id="lot-details"]/div/div[1]/div/lot-details-header-component/div/div[1]/div/h1').text
                    largePic = driver.find_element(By.CLASS_NAME, 'p-image-container-box')
                    largePic = largePic.find_element(By.CLASS_NAME, 'p-image-item-box')
                    thumbnails = driver.find_elements(By.CLASS_NAME, 'p-galleria-thumbnail-item')
                    for thumbnail in thumbnails:
                        thumbnail.click()
                        driver.implicitly_wait(3)
                        img = largePic.get_attribute('src')

                        images.append(img)
                    carPrice = driver.find_element(By.XPATH, '//*[@id="buyItNowBtn"]').text
                    carsDict['Price'] = calculateFinalPrice(
                        int(carPrice.split('$')[1].replace(',', '').replace(',', '').replace('.00 USD)', '')))
                    # carTitle = driver.find_element(By.CLASS_NAME, 'title').text
                    carInfo = driver.find_element(By.XPATH,
                                                  '//*[@id="lot-details"]/div/vehicle-details-component/div/div'
                                                  '/div[2]/div').text
                    carInfo = carInfo.splitlines()
                    # carInfo.pop(carInfo.index('ENGINE & TRANSMISSION'))
                    # carInfo.pop(carInfo.index('BASIC INFO'))
                    carLocation = driver.find_element(By.XPATH, '//*[@id="lot-details"]/div/div['
                                                                '1]/div/lot-details-header-component/div/div['
                                                                '1]/div/div/div/div[1]/span[3]/span/span[2]').text
                    print(carInfo)
                    for line in carInfo:
                        if (':' in line):
                            key = line.split(':')[0]
                            value = line.split(':')[1].strip()
                            carsDict[key] = value
                    carInfo2 = driver.find_element(By.XPATH, '//*[@id="lot-details"]/div/div[2]/div/div/div[1]/div['
                                                             '1]/div[1]/vehicle-information-component/div[2]').text
                    carInfo2 = carInfo2.splitlines()
                    print('carInfo2')
                    print(carInfo2)
                    for line in carInfo2:
                        if (':' in line) and (line not in carsDict):
                            carsDict[line.replace(':', '')] = carInfo2[carInfo2.index(line) + 1]

                    print(carsDict)
                except NoSuchElementException as e:
                    print(e)
                    unfetchedLinks.append(itemLink)
                    continue


            print(images)
            driver.implicitly_wait(3)

            carYear = pgTitle.split(' ')[0]
            if 'land rover' in pgTitle.lower():
                carMake = 'Land Rover'
            else:
                carMake = pgTitle.split(' ')[1]


            if 'range rover' in pgTitle.lower():
                carModel = 'Range Rover'
            elif 'grand cherokee' in pgTitle.lower():
                carModel = 'Grand Cherokee'
            else:
                carModel = pgTitle.split(' ')[2]


            carsDict['Handle'] = carYear + carMake + '-' + str(lotNum)
            carsDict['Title'] = pgTitle
            carsDict['Year'] = carYear
            carsDict['Product Type'] = carMake
            carsDict['Make'] = carMake
            carsDict['Model'] = carModel
            carsDict['Car Location'] = carLocation
            carsDict['Lot Number'] = lotNum
            carsDict['Stock #'] = carsDict.pop('Lot Number')
            carsDict['Drive Line Type'] = carsDict.pop('Drive')
            carsDict['Vin'] = carsDict.pop('VIN')
            carsDict['carTitle'] = carsDict.pop('Title Code')
            carsDict['Engine'] = carsDict.pop('Engine Type')
            carsDict['Fuel Type'] = carsDict.pop('Fuel')
            carsDict['Vehicle Class'] = carsDict.pop('Vehicle Type')

            carsDict['Mileage'] = int(carsDict['Odometer'].split('mi')[0].replace(',',''))


            if 'Keys' in carsDict:
                carsDict['Key'] = carsDict.pop('Keys')
            else:
                carsDict['Key'] = 'N/A'

            if 'Color' in carsDict:
                carsDict['Exterior Color'] = carsDict.pop('Color')
            else:
                carsDict['Exterior Color'] = 'N/A'

            if 'Number of Cylinders' in carsDict:
                carsDict['Cylinders'] = carsDict.pop('Number of Cylinders')
            else:
                try:
                    carsDict['Cylinders'] = carsDict['Engine'].split(' ')[1]
                except:
                    carsDict['Cylinders'] = 'N/A'

            if 'Highlights' in carsDict:
                carsDict['Start Code'] = carsDict.pop('Highlights')
            else:
                carsDict['Start Code'] = 'Run and Drive'

            carTitle = carsDict['carTitle']
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

            if 'Primary Damage' in carsDict:
                carsDict['Primary Damage'] = carsDict['Primary Damage'].replace('?', '')
            else:
                carsDict['Primary Damage'] = 'Unknown'
            carsDict['Start Code'] = carsDict['Start Code'].replace('?', '')

            if 'Transmission' not in carsDict:
                carsDict['Transmission'] = 'Unspecified'

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
                carsDict['Variant Inventory Tracker'] = "shopify"
            except:
                pass
                a = 1

            carsDict['Google Product Category'] = '916'
            carsDict['Custom Product'] = 'TRUE'


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

            except Exception as e:
                print('Body HTML not written '+ str(e))
                pass
                a = 1

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

                    else:
                        counter -= 1
                        pass
            print(itemLink + ' ' + str(carsDict))
            carsDict.clear()

            driver.close()

            driver.switch_to.window(originalWindow)

        nextPageBTN.click()
        time.sleep(5)

    driver.close()


def main():
    process = start_browser_process()
    driver = start_driver()
    # singleCar(driver)
    parsing_function(driver)


if __name__ == '__main__':
    main()
