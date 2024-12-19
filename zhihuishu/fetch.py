import json
import os
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver import ActionChains
import time
from spark_api import get_answer
from verify import slider
from duplicates import remove_duplicates_dicts


# 保存和加载处理位置的函数
def save_position(position, file_path="last_position.txt"):
    with open(file_path, "w") as f:
        f.write(str(position))

def load_position(file_path="last_position.txt"):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                return int(f.read().strip())
            except ValueError:
                pass  # 如果文件内容无效，忽略异常
    return 0  # 默认从头开始

def fetch():
    url = 'https://qah5.zhihuishu.com/qa.html#/web/home/1000070937?recruitId=257364&role=2&VNK=d43cde16'

    driver = webdriver.Chrome()
    driver.get(url)

    # 先登录并验证
    driver = slider(driver)  # 假设 slider 是完成验证的方法

    # 读取已保存的处理位置
    last_position = load_position()
    print(f"从位置 {last_position} 开始处理")

    with open('data1.json', 'r', encoding='utf-8') as file:
        items = json.load(file)

    items = remove_duplicates_dicts(items)

    for i in range(last_position, len(items)):
        time.sleep(3)  # 控制访问频率

        question_id = items[i]['questionId']
        recruit_id = items[i]['recruitId']
        question = items[i]['content']

        question_url = f'https://qah5.zhihuishu.com/qa.html#/web/questionDetail/1000070937/{question_id}?recruitId={recruit_id}&role=2'
        driver.execute_script(f"window.location.href = '{question_url}';")

        # 刷新当前页面
        driver.refresh()

        # 定义两个正则表达式
        pattern_remove_symbols = r"[#\-\*]"  # 去掉 #, -, *
        pattern_remove_brackets = r"\[\^[^\[\]]+\^\]"  # 去掉 [^...^] 结构



        # 等待并点击回答按钮
        try:
            button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[contains(@class, 'my-answer-btn') and contains(@class, 'tool-show')]"))
            )
            button.click()

            # 使用 API 获取答案
            answer = get_answer(question)

            # 依次替换
            answer = re.sub(pattern_remove_symbols, "", answer)  # 去掉 #, -, *
            answer = re.sub(pattern_remove_brackets, "", answer)  # 去掉 [^...^] 结构
        except Exception as e:
            print(f"Error locating or clicking button, 第{i+1}题已经回答过了")
            continue

        # 等待文本框加载并输入答案
        try:
            textarea = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'el-textarea__inner'))
            )
            textarea.send_keys(answer)
        except Exception as e:
            print(f"Error locating or interacting with textarea: {e}")
            continue

        # 提交答案
        try:
            driver.find_element(By.CLASS_NAME, 'up-btn').click()
            time.sleep(2)
        except Exception as e:
            print(f"Error submitting answer: {e}")

        # 点赞
        try:
            driver.find_element(By.CLASS_NAME, 'give-like.ZHIHUISHU_QZMD').click()
        except Exception as e:
            print(f"Error liking answer: {e}")

        # 保存当前进度
        save_position(i + 1)
        print(f"问题 {i + 1} 处理完成")

fetch()
