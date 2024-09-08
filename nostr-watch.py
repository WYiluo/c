from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import schedule
import threading
import queue
import requests
from datetime import datetime
import json

options = Options()
options.add_argument('--headless=new')
driver = webdriver.Chrome(options=options)
driver.set_window_size(1920, 1080)

expand_xpath = '//*[@id="wrapper"]/section/div[5]/h2'
nip11_xpath = '//*[@id="wrapper"]/section/div[5]/div/div[1]/pre'
geo_xpath = '//*[@id="wrapper"]/section/div[5]/div/div[2]/pre'
dns_xpath = '//*[@id="wrapper"]/section/div[5]/div/div[3]/pre'
watch_xpath = '//*[@id="wrapper"]/section/div[5]/div/div[4]/pre'

elem_dic = {'nip11': nip11_xpath, 'geo': geo_xpath, 'dns': dns_xpath, 'watch': watch_xpath}

with open('./relay_info.json') as file:
    relay_info = json.load(file)

checked_relay = set()
check_failed_relay = set()

for r in relay_info.keys():
    if relay_info[r]['watch']['check']['connect']:
        checked_relay.add(r)


def process_line(d):
    d = d.replace('\\\\\\\"', '')
    d = d.replace('\\n', '')
    d = d.replace('\\', '')
    d = d.replace('\n', '')
    d = d.replace('"{', '{')
    d = d.replace('}"', '}')
    d = d.replace('true', 'True')
    d = d.replace('false', 'False')
    d = d.replace('null', 'None')

    ret = eval(d)

    return ret


def crawl_relay_watch(url, driver):
    driver.get(url)
    time.sleep(45)
    dummy = driver.find_elements(By.XPATH, nip11_xpath)
    if len(dummy) == 0:
        expand = driver.find_element(By.XPATH, expand_xpath)
        expand.click()
        time.sleep(1)
    ret = {}
    for k, v in elem_dic.items():
        elem = driver.find_element(By.XPATH, v)
        ret[k] = process_line(elem.text)
    return ret

jobqueue = queue.Queue()

def worker_main():
    while 1:
        job_func = jobqueue.get()
        job_func()
        jobqueue.task_done()
        time.sleep(1)

def get_online_relay():
    res = requests.get('https://api.nostr.watch/v1/online', timeout=10)
    if res.status_code != 200:
        return []
    try:
        ret = eval(res.text)
        ret = [a[6:] for a in ret]
        return ret
    except:
        return []

def check_available():
    ts = str(datetime.now())
    res = get_online_relay()
    with open('./availability.json', 'a+') as file:
        print(ts + ': ' + json.dumps(res), file=file)
    jobqueue.put(lambda: extra_crawl(res))

def extra_crawl(l):
    r_list = []
    for r in l:
        if r not in checked_relay and r not in check_failed_relay:
            r_list.append(r)


    ts = str(datetime.now())

    for r in r_list:
        ts = str(datetime.now())
        url = 'https://nostr.watch/relay/' + r
        try:
            res = crawl_relay_watch(url, driver)
            relay_info[r] = res
            if res['watch']['check']['connect']:
                checked_relay.add(r)
            else:
                check_failed_relay.add(r)
        except:
            check_failed_relay.add(r)
            
    
    
    with open('./relay_info.json', 'w') as file:
        json.dump(relay_info, fp=file)




worker_thread = threading.Thread(target=worker_main)
worker_thread.start()

schedule.every(12).hour.do(lambda: jobqueue.put(lambda: check_failed_relay.clear()))
schedule.every().hour.at(':00').do(check_available)
schedule.every().hour.at(':15').do(check_available)
schedule.every().hour.at(':30').do(check_available)
schedule.every().hour.at(':45').do(check_available)

while 1:
    schedule.run_pending()
    time.sleep(1)