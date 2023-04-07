from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import *
from selenium.webdriver.common.by import By
import time
import random
from multiprocessing import Pool
import sys,os

baseDir = os.path.abspath(os.path.dirname(__file__))


def run(roam_time, plat):
    options = Options()
    options.add_argument('--ignore-certificate-errors')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('user-data-dir'+ baseDir)

    client = webdriver.Chrome(options=options)
    client.set_window_size(1200, 800)
    if plat == 'all':
        url = 'https://mr-stage.sensetime.com/nerf-press/stress-testing/'
    else:
        url = 'https://mr-stage.sensetime.com/nerf-press/stress-testing/?render=%s' % plat
    client.get(url)
    wait = WebDriverWait(client, 240)
    wait.until(visibility_of_element_located((By.CLASS_NAME, "enter-btn")))
    time.sleep(1)
    client.find_element(By.CLASS_NAME, 'enter-btn').click()
    wait.until(visibility_of_element_located((By.XPATH, "//div[contains(text(),'场景穿越')]")))
    # time.sleep(45)
    fly(roam_time, client)


def fly(roam_time, client):
    current_time = 0
    while current_time <= roam_time:
        step = 1
        if current_time > 0:
            client.find_element(By.CLASS_NAME, 'enter-btn').click()
            wait = WebDriverWait(client, 240)
            wait.until(visibility_of_element_located((By.XPATH, "//div[contains(text(),'场景穿越')]")))
        tag = client.find_element(By.XPATH, "//div[contains(text(),'场景穿越')]")
        random_fly_outdoor(client, tag)  # 室外飞行
        time.sleep(2)
        over = client.find_element(By.CLASS_NAME, "text")
        ActionChains(client).move_to_element(over).click().perform()
        wait = WebDriverWait(client, 240)
        wait.until(visibility_of_element_located((By.CLASS_NAME, 'more-item')))
        more = client.find_element(By.CLASS_NAME, 'more-item')  # 更多
        random_driving(client, more)
        time.sleep(2)
        more.click()
        time.sleep(1)
        home = client.find_element(By.XPATH, "//span[contains(text(),'返回首页')]")  # 返回首页
        home.click()
        time.sleep(60)  # XR释放容器时间
        current_time += step


def random_fly_outdoor(client, path):
    derections = [[-890, 580], [-980, 530], [-800, 520]]  # 下左右
    derection = random.choice(derections)
    ActionChains(client).move_to_element_with_offset(path, derection[0], derection[1]).click_and_hold().pause(
        125).release().perform()
    client.save_screenshot("flying" + time.strftime('%Y_%m_%d_%H:%M:%S') + '.png')
    time.sleep(0.5)
    ActionChains(client).move_to_element_with_offset(path, -105, 530).click_and_hold().pause(5).release().perform()


def random_driving(client, more):
    derections = [[-1020, 530]]  # 左转
    derection = random.choice(derections)
    ActionChains(client).move_to_element_with_offset(more, derection[0], derection[1]).click_and_hold().pause(
        25).release().perform()
    client.save_screenshot("driving" + time.strftime('%Y_%m_%d_%H:%M:%S') + '.png')
    # ActionChains(client).move_to_element_with_offset(more, -160, 530).click_and_hold().pause(5).release().perform() # 开车
    ActionChains(client).move_to_element_with_offset(more, -70, 530).click_and_hold().pause(5).release().perform()  # 倒车


if __name__ == '__main__':
    count = int(sys.argv[1])  # 启动线程数量
    roam_time = int(sys.argv[2])  # 循环飞行次数
    plat = sys.argv[3]  # 平台类型，可传hs,xr,all
    p = Pool(count)
    for i in range(count):
        p.apply_async(run, (roam_time, plat))
    p.close()
    p.join()

    # p = Pool(4)
    # for i in range(4):
    #     p.apply_async(run, (30, 'all'))
    # p.close()
    # p.join()
    # time.sleep(2)
