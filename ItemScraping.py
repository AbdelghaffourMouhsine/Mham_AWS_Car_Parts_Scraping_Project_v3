import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import time
import requests
import os
import re
import threading
import zipfile
import math
from collections import defaultdict
import re
# import boto3
import random

from ItemStorage import DataWithException

class GoogleImagesScraping:
    def __init__(self, PROXY_HOST=None, PROXY_PORT=None, PROXY_USER=None, PROXY_PASS=None, workerThread=None, with_selenium_grid=True):
        
        self.workerThread = workerThread
        if PROXY_HOST :
            # proxys from : https://www.webshare.io/
            
            # for run webdriver using a proxy without Authentication
            # define the proxy address and port
            # proxy = "45.127.248.127:5128"
            # options = Options()
            # options.add_argument(f"--proxy-server={proxy}")
            # self.driver = webdriver.Chrome(options=options)
    
            # for run webdriver using a proxy with Authentication
            self.PROXY_HOST = PROXY_HOST  # rotating proxy or host
            self.PROXY_PORT = PROXY_PORT # port
            self.PROXY_USER = PROXY_USER # username
            self.PROXY_PASS = PROXY_PASS # password
            
            self.options = self.init_proxy_and_get_chrome_options()
        else:
            self.options = webdriver.ChromeOptions()

        self.options.add_argument('--headless')  # Activer le mode headless
        self.options.add_argument('--no-sandbox')  # Recommandé pour les environnements serveur
        self.options.add_argument('--disable-dev-shm-usage')  # Pour éviter les problèmes de mémoire partagée
        self.options.add_argument('--disable-gpu')  # Option nécessaire pour certains environnements
        self.options.add_argument('--window-size=1920,1080')  # Définir une taille de fenêtre
        self.options.add_argument('--start-maximized')  # Démarrer en mode maximisé

        self.with_selenium_grid = with_selenium_grid
        if self.with_selenium_grid:
            self.HUB_HOST = "localhost"
            self.HUB_PORT = 4444
            self.server = f"http://{self.HUB_HOST}:{self.HUB_PORT}/wd/hub"
            self.driver=None
            with self.workerThread.lock_selenium_grid:
                self.driver = webdriver.Remote(command_executor=self.server, options=self.options)
                time.sleep(1)
        else:
            self.driver = webdriver.Chrome(options=self.options)
        
        self.driver.get('https://www.google.com')
        time.sleep(random.uniform(0.5, 2))
        
    def init_proxy_and_get_chrome_options(self): 
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """
        
        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
                }
            };
        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }
        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (self.PROXY_HOST, self.PROXY_PORT, self.PROXY_USER, self.PROXY_PASS)
        
        def get_chrome_options(use_proxy=True, user_agent=None):
            # path = os.path.dirname(os.path.abspath(_file_))
            chrome_options = webdriver.ChromeOptions()
            if use_proxy:
                pluginfile = 'proxy_auth_plugin.zip'
        
                with zipfile.ZipFile(pluginfile, 'w') as zp:
                    zp.writestr("manifest.json", manifest_json)
                    zp.writestr("background.js", background_js)
                chrome_options.add_extension(pluginfile)
            if user_agent:
                chrome_options.add_argument('--user-agent=%s' % user_agent)
            return chrome_options
        return get_chrome_options()

    def nom_valide(self, chaine):
        # Supprimer les espaces au début et à la fin
        chaine = chaine.strip()
        # Remplacer les espaces multiples par un seul tiret bas
        chaine = re.sub(r'\s+', '_', chaine)
        # Supprimer les caractères non autorisés (garde les lettres, chiffres, tirets bas et points)
        chaine = re.sub(r'[^\w.-\///]', '_', chaine)
        return chaine
        
    def click_elem(self, click_elem):
        t=2
        check = 0
        i = 0
        while not check and i<5:
            try:
                click_elem.click()
                time.sleep(t) ######
                check = 1
            except Exception as e:
                check = 0
            i += 1

    def get_element(self, path_to_elem, group=False, from_elem=None):
        i = 0
        while i<5:
            try:
                if not from_elem:
                    if not group:
                        elem = self.driver.find_element(By.XPATH, path_to_elem)
                    else :
                        elem = self.driver.find_elements(By.XPATH, path_to_elem)
                    return {"status": True, "data":elem }
                else:
                    if not group:
                        elem = from_elem.find_element(By.XPATH, path_to_elem)
                    else :
                        elem = from_elem.find_elements(By.XPATH, path_to_elem)
                    return {"status": True, "data":elem }
                        
            except Exception as e:
                i += 1
                if i == 5:
                    return {"status": False, "data":str(e) }
                
    def move_to_images_page(self):
        input_search_region = self.get_element('//*[@id="APjFqb"]')
        if input_search_region["status"]:
            input_search_region = input_search_region["data"]
            input_search_region.send_keys('some keys for get images')
            input_search_region.send_keys(Keys.ENTER)
        else:
            print({"status": False, "data":input_search_region["data"] })
            
        time.sleep(3)
        
        images_button = self.get_element('//*[@id="hdtb-sc"]/div/div/div[1]/div/div[2]/a')
        if images_button["status"]:
            images_button = images_button["data"]
            self.click_elem(images_button)
        else:
            print({"status": False, "data":images_button["data"] })
        time.sleep(random.uniform(1, 2))

    def get_images_with_key_words(self, key_words):
        try:
            time.sleep(random.uniform(0.5, 2))
            input_search = self.get_element('//*[@id="APjFqb"]')
            if input_search["status"]:
                input_search = input_search["data"]
                # Effacer le champ de saisie avant d'ajouter une nouvelle valeur
                input_search.clear()  # Supprime le contenu existant de l'input
                keywords = ' '.join(key_words.split(' || '))
                input_search.send_keys(keywords)  # Ajouter la nouvelle valeur
                time.sleep(random.uniform(0.5, 2))
                input_search.send_keys(Keys.ENTER)  # Envoyer le formulaire ou valider la recherch
            else:
                print({"status": False, "data":input_search["data"] })
            time.sleep(random.uniform(3,3.5))
            
            divs_images = self.get_element('//*[@id="rso"]/div/div/div[1]/div/div/div',group=True)
            if divs_images["status"]:
                divs_images = divs_images["data"]
                print(f"{key_words} ==> {len(divs_images)}")
                if(len(divs_images) == 0):
                    with self.workerThread.lock_file_exceptions :
                        DataWithException(value = key_words)
                    print('     if(len(divs_images) == 0)')
                else:
                    output_dir = f'./images/{' '.join([self.nom_valide(kw) for kw in key_words.split(' || ') if kw.strip() != ""])}'
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)
                    k=0
                    for i, div_image in enumerate(divs_images):
                        time.sleep(random.uniform(0.5, 1.5))
                        if k >= 5 or i == 20:
                            print("---> 5 images saved with success :)")
                            break
                        div_image.click()
                        time.sleep(random.uniform(1, 1.5))
                        img = self.get_element('//*[@id="Sva75c"]/div[2]/div[2]/div/div[2]/c-wiz/div/div[3]/div[1]/a/img[1]')
                        if img["status"]:
                            img = img["data"]
                            img_src = img.get_attribute('src')
                            try:
                                img_data = requests.get(img_src).content
                                if img_data :
                                    with open(f'{output_dir}/{' '.join([self.nom_valide(kw) for kw in key_words.split(' || ') if kw.strip() != ""])} {i} {random.uniform(0.5, 1.5)}.jpg', 'wb') as handler:
                                        handler.write(img_data)
                                        k+=1
                            except Exception as e:
                                print('cannot save this image **********************************************************',e)
                        else:
                            print('*************************************************************************************')
            else:
                print({"status": False, "data":divs_images["data"] })
                with self.workerThread.lock_file_exceptions :
                    DataWithException(value = key_words)
                
        except Exception as e:
            print(e)
            with self.workerThread.lock_file_exceptions :
                DataWithException(value = key_words)