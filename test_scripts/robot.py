from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from dotenv import load_dotenv
import os
from random_word import RandomWords
from applescript import tell
import pyperclip
import json

def generate_machine_name() -> str:
    return f"{r.get_random_word()}{r.get_random_word()}"


data_attributes = {
    "sync_interval_mins": 0.1,
    "capture_dir": "",
    "tags": [],
    "additional_sync_paths": [],
}

load_dotenv()
driver = webdriver.Chrome()
driver.get("https://app.viam.com")

goal_org = "Vijay's Org"

r = RandomWords()

# check if logged in
try:
    login = driver.find_element(By.XPATH, '//*[@id="login"]/div[1]/button[1]')
    email = driver.find_element(By.XPATH, '//*[@id="loginId"]')
    email.send_keys(os.getenv("USERNAME"))

    password = driver.find_element(By.XPATH, '//*[@id="password"]')
    password.send_keys(os.getenv("PASSWORD"))

    driver.find_element(By.XPATH, '//*[@id="login"]/form/div[2]/div/button').click()
    sleep(2)
except NoSuchElementException:
    print("already authed")

button = driver.find_element(
    By.XPATH, "/html/body/div[1]/nav[1]/div/div[2]/div/button[1]"
)
current_org = button.text
if current_org != goal_org:
    print("changing org")
    button.click()
    org_dropdown = driver.find_element(
        By.XPATH, '//*[@id="app"]/nav[1]/div/div[2]/article/ul'
    )
    org_list = org_dropdown.find_elements(By.TAG_NAME, "li")
    for org in org_list:
        print(org.text)
        if org.text == goal_org:
            print("trying to click other org")
            org.click()
            sleep(3)

# make a new robot
machine_name_shadow = driver.find_element(
    By.CSS_SELECTOR,
    "#app > div.flex.grow.flex-wrap.sm\\:min-h-\\[calc\\(100vh-52px\\)\\].sm\\:flex-nowrap > main > div.w-full.flex-wrap.items-start.justify-between.sm\\:flex > div.flex.h-full.items-start > div > v-input",
).shadow_root
machine_name_input = machine_name_shadow.find_element(By.CSS_SELECTOR, "label > input")
name = generate_machine_name()
machine_name_input.send_keys(name)
driver.find_element(
    By.CSS_SELECTOR,
    "#app > div.flex.grow.flex-wrap.sm\\:min-h-\\[calc\\(100vh-52px\\)\\].sm\\:flex-nowrap > main > div.w-full.flex-wrap.items-start.justify-between.sm\\:flex > div.flex.h-full.items-start > div > v-button",
).shadow_root.find_element(By.CSS_SELECTOR, "span > button").click()
sleep(2)
machine_page = driver.current_url

# in machine page now
# change to mac install (pre r2d2)
# driver.find_element(By.CSS_SELECTOR, '#app > div.flex.grow.flex-col.sm\\:min-h-\\[calc\\(100vh-52px\\)\\] > div.flex.grow.flex-col > div > div > div.mb-6.flex.flex-wrap.items-center.gap-4 > v-radio:nth-child(1)').shadow_root.find_element(By.CSS_SELECTOR, 'label > div.flex.flex-nowrap > button:nth-child(4)').click()
# #click download for config
# driver.find_element(By.CSS_SELECTOR, '#app > div.flex.grow.flex-col.sm\\:min-h-\\[calc\\(100vh-52px\\)\\] > div.flex.grow.flex-col > div > div > div:nth-child(3) > div:nth-child(6) > a > v-button').shadow_root.find_element(By.CSS_SELECTOR, 'span > button').click()
# select r2d2
driver.find_element(By.XPATH, '//*[@id="app"]/span[1]/div/a').click()
sleep(6)
add_component = driver.find_element(
    By.XPATH, "//*[@id[starts-with(., 'add-resource-menu')]]"
)
add_component.click()
add_component.send_keys("s")
sleep(1)
input_box = driver.find_element(By.XPATH, "//*[@id[starts-with(., 'add-resource-menu')]]/form/div[1]/label/input").send_keys('data')
sleep(.5)
data_service = driver.find_element(By.XPATH, "//*[@id[starts-with(., 'model-select-menu')]]/ul/li/p")
data_service.click()
sleep(.05)
data_service = driver.find_element(By.XPATH, "//*[@id[starts-with(., 'add-resource-menu')]]/form/div[2]/div[2]/label/div/input")
data_service.send_keys(Keys.RETURN)

sleep(1)
data_attributes_input = driver.find_element(By.XPATH, "//*[@id[starts-with(., 'card-collapse')]]/div/div/div/div/div[2]/div[2]")
data_attributes_input.send_keys(Keys.BACKSPACE)
data_attributes_input.send_keys(Keys.BACKSPACE)
data_attributes_input.send_keys(json.dumps(data_attributes))
#click save
driver.find_element(By.XPATH, '/html/body/div/div[1]/div[2]/menu/div/span[1]/button').click()
sleep(1)
# go to setup page/do terminal stuff
driver.find_element(By.XPATH, '/html/body/div/div[1]/div[2]/div/div/button').click()
sleep(.5)
setup_button = driver.find_element(
    By.XPATH, "//a[text()='View setup instructions']"
).click()
sleep(1)
driver.get(f"{driver.current_url}/mac#rdk")
sleep(3)
# click download
driver.find_element(By.XPATH, "/html/body/div/div[1]/main/div/div[2]/a/button").click()
# click copy
driver.find_element(
    By.XPATH, "/html/body/div/div[1]/main/div/figure/div/button"
).click()
sleep(1)
tell.app("Terminal", 'do script "' + pyperclip.paste() + '"')

driver.get(machine_page)
# # select r2d2 again

sleep(10)
