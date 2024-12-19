import base64

import numpy as np
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
import random
import time
import cv2  # opencv库

def slider(driver):


    # 检查是否仍在滑块验证页面
    while "login" in driver.current_url:  # 确保页面已跳转
        print("请扫码验证")
        time.sleep(1)

    print('跳转页面')


    return driver

