import csv
import json
import os
from urllib.parse import unquote
from requests import get
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver

p = 100  # number of products to scrape

debug = False

headless = False  # make it headless to speed up
images = False  # disable images to save bandwidth
max = False

incognito = True
file = 'veranstaltungen_bayern_by.csv'
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu "
                  "Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36"}


def main():
    driver = getChromeDriver()
    driver.get('https://veranstaltungen.bayern.by/region/')
    sleep(5)
    for i in range(8, p):
        url = driver.find_elements_by_xpath(f'//div[@class="content"]/h4/a')[i].get_attribute('href')
        try:
            btn = driver.find_element_by_xpath('//button[@id="mehrladen"]')
            try:
                driver.execute_script("arguments[0].scrollIntoView();", btn)
                btn.click()
            except:
                driver.execute_script("arguments[0].click();", btn)
            soup = BeautifulSoup(get(url, headers=headers).content, "lxml")
            data = {"name": soup.find('h2').text,
                    "date": soup.find('p', {'class': 'date'}).text.strip().replace("\n", "").replace("\t",
                                                                                                     "".replace(r"\r",
                                                                                                                "")),
                    "time": soup.find('span', {'class': 'time'}).text.strip(),
                    "location": soup.find('p', {'class': 'location'}).text.strip(),
                    "description": soup.find('div', {'class': 'desc'}).text.strip(),
                    "url": url,
                    "img": unquote(soup.find('a', {'rel': 'by_lightbox[rce]'})['href'].split("&src=")[1])
                    }
            print(json.dumps(data, indent=4))
            writeCSV(data)
            download(data["img"])
        except Exception as e:
            print("Error on url: ", url, e)


def download(url):
    with open("./img/" + os.path.basename(url), 'wb') as img:
        response = get(url, headers=headers)
        img.write(response.content)


def writeCSV(data):
    with open(file, mode='a', newline="", encoding="utf8") as csv_file:
        csv.writer(csv_file).writerow(
            [data["name"], data["date"], data["time"], data["location"], data["description"], data["img"],
             data["url"]])


def getChromeDriver(proxy=None):
    options = webdriver.ChromeOptions()
    if debug:
        # print("Connecting existing Chrome for debugging...")
        options.debugger_address = "127.0.0.1:9222"
    if not images:
        # print("Turning off images to save bandwidth")
        options.add_argument("--blink-settings=imagesEnabled=false")
    if headless:
        # print("Going headless")
        options.add_argument("--headless")
        options.add_argument("--window-size=1920x1080")
    if max:
        # print("Maximizing Chrome ")
        options.add_argument("--start-maximized")
    if proxy:
        # print(f"Adding proxy: {proxy}")
        options.add_argument(f"--proxy-server={proxy}")
    if incognito:
        # print("Going incognito")
        options.add_argument("--incognito")
    return webdriver.Chrome(options=options)


def getFirefoxDriver():
    options = webdriver.FirefoxOptions()
    if not images:
        # print("Turning off images to save bandwidth")
        options.set_preference("permissions.default.image", 2)
    if incognito:
        # print("Enabling incognito mode")
        options.set_preference("browser.privatebrowsing.autostart", True)
    if headless:
        # print("Hiding Firefox")
        options.add_argument("--headless")
        options.add_argument("--window-size=1920x1080")
    return webdriver.Firefox(options)


def logo():
    print("""
        __________                                   
        \______   \_____  ___.__. ___________  ____  
         |    |  _/\__  \<   |  |/ __ \_  __ \/    \ 
         |    |   \ / __ \\\\___  \  ___/|  | \/   |  \\
         |______  /(____  / ____|\___  >__|  |___|  /
                \/      \/\/         \/           \/ 
    ==========================================================
       Developed by https://www.fiverr.com/muhammadhassan7
    ==========================================================""")


if __name__ == "__main__":
    if not os.path.isdir("img"):
        os.mkdir("img")
    if not os.path.isfile(file):
        with open(file, mode='w', newline="") as csv_file:
            csv.writer(csv_file).writerow(["Name", "Date", "Time", "Location", "Description", "Image", "URL"])
    logo()
    main()
