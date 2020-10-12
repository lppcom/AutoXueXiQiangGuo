#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@project: AutoXue-multiuser
@file: __main__.py
@time: 2020年9月29日10:55:28
@Copyright © 2020. All rights reserved.
"""
import re
import time
import requests
import string
import subprocess
from datetime import datetime
from urllib.parse import quote
from itertools import accumulate
from collections import defaultdict
from appium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from xuexi.unit import Timer, logger, caps, rules, cfg
from xuexi.model import BankQuery
from xuexi.secureRandom import SecureRandom as random
from xuexi.model_local import TikuQuery


class Automation:
    # 初始化 Appium 基本参数
    def __init__(self):
        self.connect()
        self.desired_caps = {
            "platformName": caps["platformname"],
            "platformVersion": caps["platformversion"],
            "automationName": caps["automationname"],
            "unicodeKeyboard": caps["unicodekeyboard"],
            "resetKeyboard": caps["resetkeyboard"],
            "noReset": caps["noreset"],
            'newCommandTimeout': 8000,
            "deviceName": caps["devicename"],
            "uuid": caps["uuid"],
            "appPackage": caps["apppackage"],
            "appActivity": caps["appactivity"]
        }
        logger.info('打开 appium 服务,正在配置...')
        self.driver = webdriver.Remote('http://localhost:4723/wd/hub', self.desired_caps)
        self.wait = WebDriverWait(self.driver, 15)
        self.size = self.driver.get_window_size()

    def connect(self):
        logger.info(f'正在连接模拟器 {caps["uuid"]}，请稍候...')
        if 0 == subprocess.check_call(f'adb connect {caps["uuid"]}', shell=True, stdout=subprocess.PIPE):
            logger.info(f'模拟器 {caps["uuid"]} 连接成功')
        else:
            logger.info(f'模拟器 {caps["uuid"]} 连接失败')

    def disconnect(self):
        logger.info(f'正在断开模拟器 {caps["uuid"]}，请稍候...')
        if 0 == subprocess.check_call(f'adb disconnect {caps["uuid"]}', shell=True, stdout=subprocess.PIPE):
            logger.info(f'模拟器 {caps["uuid"]} 断开成功')
        else:
            logger.info(f'模拟器 {caps["uuid"]} 断开失败')

    # 屏幕方法
    def swipe_up(self):
        # 向上滑动屏幕
        self.driver.swipe(self.size['width'] * random.uniform(0.55, 0.65),
                          self.size['height'] * random.uniform(0.65, 0.75),
                          self.size['width'] * random.uniform(0.55, 0.65),
                          self.size['height'] * random.uniform(0.25, 0.35), random.uniform(800, 1200))
        logger.debug('向上滑动屏幕')

    def swipe_down(self):
        # 向下滑动屏幕
        self.driver.swipe(self.size['width'] * random.uniform(0.55, 0.65),
                          self.size['height'] * random.uniform(0.25, 0.35),
                          self.size['width'] * random.uniform(0.55, 0.65),
                          self.size['height'] * random.uniform(0.65, 0.75), random.uniform(800, 1200))
        logger.debug('向下滑动屏幕')

    def swipe_right(self):
        # 向右滑动屏幕
        self.driver.swipe(self.size['width'] * random.uniform(0.01, 0.11),
                          self.size['height'] * random.uniform(0.75, 0.89),
                          self.size['width'] * random.uniform(0.89, 0.98),
                          self.size['height'] * random.uniform(0.75, 0.89), random.uniform(800, 1200))
        logger.debug('向右滑动屏幕')

    def swipe_left(self):
        # 向右滑动屏幕
        self.driver.swipe(self.size['width'] * random.uniform(0.89, 0.98),
                          self.size['height'] * random.uniform(0.75, 0.89),
                          self.size['width'] * random.uniform(0.01, 0.11),
                          self.size['height'] * random.uniform(0.75, 0.89), random.uniform(800, 1200))
        logger.debug('向左滑动屏幕')

    def find_element(self, ele: str):
        logger.debug(f'find elements by xpath: {ele}')
        try:
            element = self.driver.find_element_by_xpath(ele)
        except NoSuchElementException as e:
            logger.error(f'找不到元素: {ele}')
            raise e
        return element

    def find_elements(self, ele: str):
        logger.debug(f'find elements by xpath: {ele}')
        try:
            elements = self.driver.find_elements_by_xpath(ele)
        except NoSuchElementException as e:
            logger.error(f'找不到元素: {ele}')
            raise e
        return elements

    # 返回事件
    def safe_back(self, msg='default msg'):
        logger.debug(msg)
        self.driver.keyevent(4)
        time.sleep(1)  # 返回后延时1秒，如果模拟器渲染较慢，可以适当增大这个延时

    def safe_click(self, ele: str):
        logger.debug(f'safe click {ele}')
        button = self.wait.until(EC.presence_of_element_located((By.XPATH, ele)))
        # button = self.find_element(ele)
        try:
            button.click()
        except Exception as ex:
            print(ex)
            return
        time.sleep(1)  # 点击后延时1秒，如果模拟器渲染较慢，可以适当增大这个延时

    # 发送文件
    def CodePic_to_phone(self, CodePicPath, PhonePath):
        logger.info(f'正在发送登录二维码图片，请稍候...')
        if 0 == subprocess.check_call(f'adb remount', shell=True, stdout=subprocess.PIPE):
            logger.info(f'adb remount 成功')
            time.sleep(5)
        else:
            logger.info(f'adb remount 失败')
        if 0 == subprocess.check_call(f'adb push {CodePicPath} {PhonePath}', shell=True, stdout=subprocess.PIPE):
            logger.info(f'发送二维码成功')
        else:
            logger.info(f'发送二维码失败')
    # def __del__(self):
    #     self.driver.close_app()
    #     self.driver.quit()


class App(Automation):
    def __init__(self, username="", password=""):
        self.username = username
        self.password = password
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
        }
        self.query = BankQuery()
        self.bank = None
        self.score = defaultdict(tuple)
        self.query_local = TikuQuery()

        super().__init__()

        # self.login_or_not()
        self.driver.wait_activity('com.alibaba.android.rimet.biz.home.activity.HomeActivity', 20, 3)
        # self.wait.until(EC.presence_of_element_located((
        #     By.XPATH, '//*[@resource-id="cn.xuexi.android:id/tvv_video_render"]')))
        # self.wait.until_not(EC.presence_of_element_located((
        #     By.XPATH, '//*[@resource-id="cn.xuexi.android:id/tvv_video_render"]')))
        # self.view_score()
        # self._read_init()
        # self._view_init()
        # self._daily_init()
        # self._challenge_init()
        # self._weekly_init()

    def initapp(self, username="", password=""):
        self.username = username
        self.password = password
        self.login_or_not()
        self.view_score()
        self._read_init()
        self._view_init()
        self._daily_init()
        self._challenge_init()
        self._weekly_init()
        self._special_init()
        self._zhengshangyou_init()
        self._shuangrenduizhan_init()

    def login_or_not(self):
        # com.alibaba.android.user.login.SignUpWithPwdActivity
        time.sleep(10)  # 首屏等待时间
        try:
            home = self.driver.find_element_by_xpath(rules["mine_entry"])
            # home = self.driver.find_element_by_xpath(rules["mine_entry"])
            logger.debug(f'已经登录')
            logger.info("发现app已经登录，退出重新登录")
            is_login = True
            # return
        except NoSuchElementException as e:
            logger.debug(self.driver.current_activity)
            logger.debug(e)
            is_login = False
            logger.debug(f"非首页，先进行登录")
            logger.info("app未登录")
            try:
                self.driver.find_element_by_xpath(rules["login_username"])
            except:
                logger.info("app出错，返回上一层！")
                self.safe_back()

        if is_login:
            self.safe_click(rules["mine_entry"])
            self.safe_click(rules["setting_submit"])
            self.safe_click(rules["logout_submit"])
            self.safe_click(rules["logout_confirm"])
            logger.info("已注销")

        if not self.username or not self.password:
            logger.error(f'未提供有效的username和password')
            logger.info(f'也许你可以通过下面的命令重新启动:')
            logger.info(f'\tpython -m xuexi ')
            raise ValueError('需要提供登录的用户名和密-u "your_username" -p "your_password"钥，或者提前在App登录账号后运行本程序')

        username = self.wait.until(EC.presence_of_element_located((
            By.XPATH, rules["login_username"]
        )))
        password = self.wait.until(EC.presence_of_element_located((
            By.XPATH, rules["login_password"]
        )))
        username.send_keys(self.username)
        password.send_keys(self.password)
        self.safe_click(rules["login_submit"])
        logger.info(f'开始学习{self.username}的账号')
        # time.sleep(15)
        self.wait.until(EC.presence_of_element_located((
            By.XPATH, rules["home_entry"])))
        try:
            home = self.driver.find_element_by_xpath(rules["home_entry"])
            logger.debug(f'无需点击同意条款按钮')
            return
        except NoSuchElementException as e:
            logger.debug(self.driver.current_activity)
            logger.debug(f"需要点击同意条款按钮")
            self.safe_click(rules["login_confirm"])
        # time.sleep(3)

    def logout_or_not(self):
        if cfg.getboolean("prefers", "keep_alive"):
            logger.debug("无需自动注销账号")
            return
        self.safe_click(rules["mine_entry"])
        self.safe_click(rules["setting_submit"])
        self.safe_click(rules["logout_submit"])
        self.safe_click(rules["logout_confirm"])
        logger.info("已注销")

    def view_score(self):
        self.safe_click(rules['score_entry'])
        titles = ["登录", "我要选读文章", "视听学习", "视听学习时长", "每日答题", "每周答题", "专项答题",
                  "挑战答题", "争上游答题", "双人对战", "订阅", "分享", "发表观点", "本地频道"]
        # time.sleep(15)
        try:
            self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@text="本地频道"]')))
        except:
            logger.info("没有等到得分页面！")
            try:
                cancel = self.wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, '//*[@text="取消"] or @text="退出"] or @text="等待"]')))
                logger.info("app响应慢，你的机器好卡顿啊！")
                cancel.click()
            except:
                logger.info("app响应慢，你的机器好卡顿啊！！")
                self.safe_back()
        score_list = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, rules['score_list'])))

        # score_list = self.find_elements(rules["score_list"])
        for t, score in zip(titles, score_list):
            s = score.get_attribute("name")
            self.score[t] = tuple([int(x) for x in re.findall(r'\d+', s)])

        # print(self.score)
        totalscore = 0
        for i in self.score:
            # logger.debug(f'{i}, {self.score[i]}')
            logger.info(f'{i}, {self.score[i]}')
            totalscore += self.score[i][0]
        logger.info(f'今日总得分：    {totalscore}')
        self.safe_back('score -> home')

    def back_or_not(self, title):
        # return False
        g, t = self.score[title]
        if g == t:
            logger.debug(f'{title} 积分已达成，无需重复获取积分')
            return True
        return False

    def _search(self, content, options, exclude=''):
        # 职责 网上搜索
        logger.debug(f'搜索 {content} <exclude = {exclude}>')
        logger.info(f"选项 {options}")
        content = re.sub(r'[\(（]出题单位.*', "", content)
        if options[-1].startswith("以上") and chr(len(options) + 64) not in exclude:
            logger.info(f'根据经验: {chr(len(options) + 64)} 很可能是正确答案')
            return chr(len(options) + 64)
        # url = quote('https://www.baidu.com/s?wd=' + content, safe=string.printable)
        url = quote("http://www.sogou.com/web?query=" + content, safe=string.printable)
        response = requests.get(url, headers=self.headers).text
        counts = []
        for i, option in zip(['A', 'B', 'C', 'D', 'E', 'F'], options):
            count = response.count(option)
            counts.append((count, i))
            logger.info(f'{i}. {option}: {count} 次')
        counts = sorted(counts, key=lambda x: x[0], reverse=True)
        counts = [x for x in counts if x[1] not in exclude]
        c, i = counts[0]
        if 0 == c:
            # 替换了百度引擎为搜狗引擎，结果全为零的机会应该会大幅降低       
            _, i = random.choice(counts)
            logger.info(f'搜索结果全0，随机一个 {i}')
        logger.info(f'根据搜索结果: {i} 很可能是正确答案')
        return i

    def _verify(self, category, content, options):
        # 职责: 检索题库 查看提示
        letters = list("ABCDEFGHIJKLMN")
        self.bank = self.query_local.post({
            "category": category,
            "content": content,
            "options": options
        })
        # answer = self.query_local.post(category, content, options)
        if not self.bank or not self.bank["answer"]:
            answer = None
        else:
            answer = self.bank["answer"]
        # logger.info(f'本地搜索答案如下: {answer}')
        if answer is not None:
            logger.info(f'本地搜索已知的正确答案: {answer}')
            return answer
        excludes = self.bank["excludes"] if self.bank else ""
        tips = self._view_tips()
        if not tips:
            logger.debug("本题没有提示")
            if "填空题" == category:
                return None
            elif "多选题" == category:
                return "ABCDEFG"[:len(options)]
            elif "单选题" == category:
                return self._search(content, options, excludes)
            elif "挑战题" == category:
                return self._search(content, options, excludes)
            else:
                logger.debug("题目类型非法")
        else:
            if "填空题" == category:
                dest = re.findall(r'.{0,2}\s+.{0,2}', content)
                logger.debug(f'dest: {dest}')
                if 1 == len(dest):
                    dest = dest[0]
                    logger.debug(f'单处填空题可以尝试正则匹配')
                    pattern = re.sub(r'\s+', '(.+?)', dest)
                    logger.debug(f'匹配模式 {pattern}')
                    res = re.findall(pattern, tips)
                    pattern_reverse = re.sub(r'\s+', '(.+?)', dest[::-1])
                    res_reverse = re.findall(pattern_reverse, tips[::-1])
                    # logger.info(res)
                    # logger.info(res_reverse)
                    if 1 == len(res) and 1 == len(res_reverse):
                        if res[0] <= res_reverse[0][::-1]:
                            return res[0]
                        else:
                            return res_reverse[0][::-1]

                logger.debug(f'多处填空题难以预料结果，索性不处理')
                return None

            elif "多选题" == category:
                check_res = [letter for letter, option in zip(letters, options) if (option in tips and len(option) > 0)]
                if len(check_res) > 1:
                    logger.debug(f'根据提示，可选项有: {check_res}')
                    return "".join(check_res)
                return "ABCDEFG"[:len(options)]
            elif "单选题" == category:
                radio_in_tips, radio_out_tips = "", ""
                for letter, option in zip(letters, options):
                    if len(option) > 0:
                        if option in tips:
                            logger.debug(f'{option} in tips')
                            logger.debug(f'{len(option)}')
                            radio_in_tips += letter
                        else:
                            logger.debug(f'{option} out tips')
                            logger.debug(f'{len(option)}')
                            radio_out_tips += letter

                logger.debug(f'含 {radio_in_tips} 不含 {radio_out_tips}')
                if 1 == len(radio_in_tips) and radio_in_tips not in excludes:
                    logger.debug(f'根据提示 {radio_in_tips}')
                    return radio_in_tips
                if 1 == len(radio_out_tips) and radio_out_tips not in excludes:
                    logger.debug(f'根据提示 {radio_out_tips}')
                    return radio_out_tips
                return self._search(content, options, excludes)
            else:
                logger.debug("题目类型非法")

    def _verify_tiaozhan(self, category, content, options):
        # 职责: 检索题库 查看提示
        letters = list("ABCDEFGHIJKLMN")
        # self.bank = self.query.post({
        #     "category": category,
        #     "content": content,
        #     "options": options
        # })
        answer = self.query_local.post(content, options)
        logger.info(f'本地搜索答案如下: {answer}')
        if answer is not None:
            logger.info(f'已知的正确答案: {answer}')
            return answer
        excludes = self.bank["excludes"] if self.bank else ""
        tips = self._view_tips()
        if not tips:
            logger.debug("本题没有提示")
            if "填空题" == category:
                return None
            elif "多选题" == category:
                return "ABCDEFG"[:len(options)]
            elif "单选题" == category:
                return self._search(content, options)
            elif "挑战题" == category:
                return self._search(content, options)
            else:
                logger.debug("题目类型非法")
        else:
            if "填空题" == category:
                dest = re.findall(r'.{0,2}\s+.{0,2}', content)
                logger.debug(f'dest: {dest}')
                if 1 == len(dest):
                    dest = dest[0]
                    logger.debug(f'单处填空题可以尝试正则匹配')
                    pattern = re.sub(r'\s+', '(.+?)', dest)
                    logger.debug(f'匹配模式 {pattern}')
                    res = re.findall(pattern, tips)
                    if 1 == len(res):
                        return res[0]
                logger.debug(f'多处填空题难以预料结果，索性不处理')
                return None

            elif "多选题" == category:
                check_res = [letter for letter, option in zip(letters, options) if (option in tips and len(option) > 0)]
                if len(check_res) > 1:
                    logger.debug(f'根据提示，可选项有: {check_res}')
                    return "".join(check_res)
                return "ABCDEFG"[:len(options)]
            elif "单选题" == category:
                radio_in_tips, radio_out_tips = "", ""
                for letter, option in zip(letters, options):
                    if len(option) > 0:
                        if option in tips:
                            logger.debug(f'{option} in tips')
                            logger.debug(f'{len(option)}')
                            radio_in_tips += letter
                        else:
                            logger.debug(f'{option} out tips')
                            logger.debug(f'{len(option)}')
                            radio_out_tips += letter

                logger.debug(f'含 {radio_in_tips} 不含 {radio_out_tips}')
                if 1 == len(radio_in_tips) and radio_in_tips not in excludes:
                    logger.debug(f'根据提示 {radio_in_tips}')
                    return radio_in_tips
                if 1 == len(radio_out_tips) and radio_out_tips not in excludes:
                    logger.debug(f'根据提示 {radio_out_tips}')
                    return radio_out_tips
                return self._search(content, options, excludes)
            else:
                logger.debug("题目类型非法")

    def _update_bank(self, item):
        if self.query_local.post_precise(item):
            return
        else:
            self.query_local.put(item)

    # 争上游模块初始化
    def _zhengshangyou_init(self):
        g, t = self.score["争上游答题"]
        if t == g:
            self.zhengshangyou_count = 0
        elif g == 0:
            self.zhengshangyou_count = 2
        else:
            self.zhengshangyou_count = 0

    # 争上游模块初始化
    def _shuangrenduizhan_init(self):
        g, t = self.score["双人对战"]
        if t == g:
            self.shuangrenduizhan_count = 0
        elif g == 1:
            self.shuangrenduizhan_count = 0
        else:
            self.shuangrenduizhan_count = 1

    # 挑战答题模块
    # class Challenge(App):
    def _challenge_init(self):
        # super().__init__()
        try:
            self.challenge_count = cfg.getint('prefers', 'challenge_count')
        except:
            g, t = self.score["挑战答题"]
            if t == g:
                self.challenge_count = 0
            else:
                self.challenge_count = random.randint(
                    cfg.getint('prefers', 'challenge_count_min'),
                    cfg.getint('prefers', 'challenge_count_max'))

        self.challenge_delay_bot = cfg.getint('prefers', 'challenge_delay_min')
        self.challenge_delay_top = cfg.getint('prefers', 'challenge_delay_max')
        logger.debug(f'挑战答题: {self.challenge_count}')

    def _challenge_cycle(self, num):
        self.safe_click(rules['challenge_entry'])
        offset = 0  # 自动答错的偏移开关
        while num > -1:
            content = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, rules['challenge_content']))).get_attribute("name")
            content = content.replace("\x20", " ")
            content = content.replace("\xa0", " ")
            # logger.info(content)
            # content = self.find_element(rules["challenge_content"]).get_attribute("name")
            option_elements = self.wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, rules['challenge_options'])))
            # option_elements = self.find_elements(rules['challenge_options'])
            options = [x.get_attribute("name") for x in option_elements]
            length_of_options = len(options)
            logger.info(f'<{num}> {content}')
            # 此处题目类型为”挑战题“，所有单选均改为挑战题
            answer = self._verify(category='挑战题', content=content, options=options)
            delay_time = random.randint(self.challenge_delay_bot, self.challenge_delay_top)
            if 0 == num:
                offset = random.randint(1, length_of_options - 1)  # randint居然包含上限值，坑爹！！！
                logger.info(f'已完成指定题量，设置提交选项偏移 -{offset}')
                # logger.info(
                #     f'随机延时 {delay_time} 秒提交答案: {chr((ord(answer) - 65 - offset + length_of_options) % length_of_options + 65)}')

                # logger.info(f'随机延时 {delay_time} 秒提交答案: {answer}')
            time.sleep(delay_time)
            # 利用python切片的特性，即使索引值为-offset，可以正确取值
            # if answer is None:
            #     answer = "A"
            option_elements[ord(answer) - 65 - offset].click()
            try:
                time.sleep(5)
                wrong = self.driver.find_element_by_xpath(rules["challenge_over"])
                logger.debug(f'很遗憾本题回答错误')
                self._update_bank({
                    "category": "挑战题",
                    "content": content,
                    "options": options,
                    "answer": "",
                    "excludes": answer,
                    "notes": ""
                })
                logger.debug("点击结束本局")
                wrong.click()  # 直接结束本局
                time.sleep(5)
                break
            except:
                logger.debug(f'恭喜本题回答正确')
                num -= 1
                self._update_bank({
                    "category": "挑战题",
                    "content": content,
                    "options": options,
                    "answer": answer,
                    "excludes": "",
                    "notes": ""
                })
        else:
            logger.debug("通过选项偏移，应该不会打印这句话，除非碰巧答案有误")
            logger.debug("那么也好，延时30秒后结束挑战")
            time.sleep(30)
            self.safe_back('challenge -> share_page')  # 发现部分模拟器返回无效
        # 更新后挑战答题需要增加一次返回
        self.safe_back('share_page -> quiz')  # 发现部分模拟器返回无效
        return num

    def _challenge_circle_test(self, num):
        self.safe_click(rules['challenge_entry'])
        offset = 0  # 自动答错的偏移开关
        while num > -1:
            content = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, rules['challenge_content']))).get_attribute("name")
            # content = content.decode(encoding='UTF-8')
            # content = re.sub("\"", "", content)
            content = content.replace("\x20", " ")
            content = content.replace("\xa0", " ")
            # logger.info(content)
            # content = self.find_element(rules["challenge_content"]).get_attribute("name")
            option_elements = self.wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, rules['challenge_options'])))
            # option_elements = self.find_elements(rules['challenge_options'])
            options = [x.get_attribute("name") for x in option_elements]
            length_of_options = len(options)
            logger.info(f'<{num}> {content}')
            # 此处题目类型为”单选题“，不应该是挑战题，目前所有挑战题都是单选题。
            answer = self._verify(category='挑战题', content=content, options=options)
            delay_time = random.randint(self.challenge_delay_bot, self.challenge_delay_top)
            if 0 == num:
                offset = random.randint(1, length_of_options - 1)  # randint居然包含上限值，坑爹！！！
                logger.info(f'已完成指定题量，设置提交选项偏移 -{offset}')
                logger.info(
                    f'随机延时 {delay_time} 秒提交答案: {chr((ord(answer) - 65 - offset + length_of_options) % length_of_options + 65)}')
            else:
                logger.info(f'随机延时 {delay_time} 秒提交答案: {answer}')
            time.sleep(delay_time)
            # 利用python切片的特性，即使索引值为-offset，可以正确取值
            # if answer is None:
            #     answer = "A"
            option_elements[ord(answer) - 65 - offset].click()
            try:
                time.sleep(5)
                wrong = self.driver.find_element_by_xpath(rules["challenge_over"])
                logger.debug(f'很遗憾本题回答错误')
                self._update_bank({
                    "category": "挑战题",
                    "content": content,
                    "options": options,
                    "answer": "",
                    "excludes": answer,
                    "notes": ""
                })
                logger.debug("点击结束本局")
                wrong.click()  # 直接结束本局
                time.sleep(5)
                break
            except:
                logger.debug(f'恭喜本题回答正确')
                num -= 1
                self._update_bank({
                    "category": "挑战题",
                    "content": content,
                    "options": options,
                    "answer": answer,
                    "excludes": "",
                    "notes": ""
                })
        else:
            logger.debug("通过选项偏移，应该不会打印这句话，除非碰巧答案有误")
            logger.debug("那么也好，延时30秒后结束挑战")
            time.sleep(30)
            self.safe_back('challenge -> share_page')  # 发现部分模拟器返回无效
        # 更新后挑战答题需要增加一次返回
        self.safe_back('share_page -> quiz')  # 发现部分模拟器返回无效
        return num

    def _zhengshangyou_cycle(self):
        time.sleep(3)
        self.safe_click(rules['zhengshangyou_entry'])
        num = 1
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@text="开始比赛"]')))
        self.safe_click('//*[@text="开始比赛"]')
        time.sleep(5)
        last_content = ""
        while True:
            try:
                content = self.wait.until(EC.presence_of_element_located(
                    (By.XPATH, rules['challenge_content']))).get_attribute("name")
                # logger.info(content)
            except:
                time.sleep(0.5)
                try:
                    # time.sleep(1)
                    self.driver.find_element_by_xpath('//*[@text="正确数/总题数"]')
                    # zsyend = self.driver.find_element_by_xpath('//*[@text="正确数/总题数"]')
                    logger.info(f'本轮挑战结束')
                    time.sleep(5)
                    # self.safe_back()
                    break
                except:
                    continue
            init_content = content
            if content == last_content:
                # logger.info(f'等待题目刷新！')
                continue
            content = content.replace("\x20", " ")
            content = content.replace("\xa0", " ")[3:]
            # content = content[3:]
            # logger.info(f'<{num}> {content}')
            option_elements = self.wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, rules['challenge_options'])))
            options = [x.get_attribute("name")[3:] for x in option_elements]
            # logger.info(f'<{num}> {content}')
            answer = self._verify(category='挑战题', content=content, options=options)
            try:
                option_elements[ord(answer) - 65].click()
            except:
                try:
                    self.driver.find_element_by_xpath('//android.widget.Image/android.widget.Image[3]')
                    logger.info(f'本轮挑战结束,居然tm输给了别人！！！')
                    break
                except:
                    break

            # logger.debug(f'本题回答完毕，抓紧继续下一题')
            last_content = init_content
            num += 1
        # 更新后挑战答题需要增加一次返回
        self.safe_back('share_page -> quiz')  # 发现部分模拟器返回无效
        return num

    def _zhengshangyou_fast_cycle(self):
        time.sleep(3)
        self.safe_click(rules['zhengshangyou_entry'])
        num = 1
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@text="开始比赛"]')))
        self.safe_click('//*[@text="开始比赛"]')
        time.sleep(5)
        last_content = ""
        while True:
            try:
                content = self.wait.until(EC.presence_of_element_located(
                    (By.XPATH, rules['challenge_content']))).get_attribute("name")
                # logger.info(content)
            except:
                time.sleep(0.5)
                try:
                    # time.sleep(1)
                    self.driver.find_element_by_xpath('//*[@text="正确数/总题数"]')
                    # zsyend = self.driver.find_element_by_xpath('//*[@text="正确数/总题数"]')
                    logger.info(f'本轮挑战结束')
                    time.sleep(5)
                    # self.safe_back()
                    break
                except:
                    continue
            init_content = content
            if content == last_content:
                # logger.info(f'等待题目刷新！')
                continue
            content = content.replace("\x20", " ")
            content = content.replace("\xa0", " ")[3:]
            # content = content[3:]
            # logger.info(f'<{num}> {content}')
            answer = self.query_local.query_with_content(content)
            if answer != "":
                option_elements = self.wait.until(EC.presence_of_all_elements_located(
                    (By.XPATH, rules['challenge_options'])))
                # logger.info(f"直接找到答案{answer}")
                try:
                    option_elements[ord(answer) - 65].click()
                except:
                    try:
                        self.driver.find_element_by_xpath('//android.widget.Image/android.widget.Image[3]')
                        logger.info(f'本轮挑战结束,居然tm输给了别人！！！')
                        break
                    except:
                        break
            else:
                option_elements = self.wait.until(EC.presence_of_all_elements_located(
                    (By.XPATH, rules['challenge_options'])))
                options = [x.get_attribute("name")[3:] for x in option_elements]
                # logger.info(f'<{num}> {content}')
                answer = self._verify(category='挑战题', content=content, options=options)
                try:
                    option_elements[ord(answer) - 65].click()
                except:
                    try:
                        self.driver.find_element_by_xpath('//android.widget.Image/android.widget.Image[3]')
                        logger.info(f'本轮挑战结束,居然tm输给了别人！！！')
                        break
                    except:
                        break

            # logger.debug(f'本题回答完毕，抓紧继续下一题')
            last_content = init_content
            num += 1
        # 更新后挑战答题需要增加一次返回
        self.safe_back('share_page -> quiz')  # 发现部分模拟器返回无效
        return num

    def _2_ren_cycle(self):
        self.safe_click(rules['shuangrenduizhan_entry'])
        num = 1
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@text="邀请对手"]')))
        self.safe_click('//*[@text="邀请对手"]//preceding-sibling::android.view.View')
        time.sleep(1)
        try:
            self.driver.find_element_by_xpath('//*[@text="开始对战"]//preceding-sibling::android.view.View//preceding'
                                              '-sibling::android.view.View/android.view.View/android.view.View'
                                              '/android.view.View/android.widget.Image')
        except:
            logger.info("没找到对手，独孤求败了")
            return
        # self.wait.until(EC.presence_of_element_located(
        #     (By.XPATH, '//*[@text="开始对战"]')))
        self.safe_click('//*[@text="开始对战"]')
        last_content = ""
        while True:
            try:
                content = self.wait.until(EC.presence_of_element_located(
                    (By.XPATH, rules['challenge_content']))).get_attribute("name")
                # logger.info(content)
            except:
                time.sleep(0.5)
                try:
                    # time.sleep(1)
                    self.driver.find_element_by_xpath('//*[@text="正确数/总题数"]')
                    # zsyend = self.driver.find_element_by_xpath('//*[@text="正确数/总题数"]')
                    logger.info(f'本轮挑战结束')
                    time.sleep(5)
                    # self.safe_back()
                    break
                except:
                    continue
            init_content = content
            if content == last_content:
                # logger.info(f'等待题目刷新！')
                continue
            content = content.replace("\x20", " ")
            content = content.replace("\xa0", " ")[3:]
            # content = content[3:]
            # logger.info(f'<{num}> {content}')
            option_elements = self.wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, rules['challenge_options'])))
            options = [x.get_attribute("name")[3:] for x in option_elements]
            # logger.info(f'<{num}> {content}')
            answer = self._verify(category='挑战题', content=content, options=options)
            try:
                option_elements[ord(answer) - 65].click()
            except:
                try:
                    self.driver.find_element_by_xpath('//android.widget.Image/android.widget.Image[3]')
                    logger.info(f'本轮挑战结束,居然tm输给了别人！！！')
                    break
                except:
                    break
            # logger.debug(f'本题回答完毕，抓紧继续下一题')
            last_content = init_content
            num += 1
        # 更新后挑战答题需要增加一次返回
        self.safe_back('share_page -> quiz')  # 发现部分模拟器返回无效
        return num

    def _challenge_test(self):
        self.challenge_count = 1000
        logger.info(f'挑战答题 目标 {self.challenge_count} 题, Go!')
        while True:
            result = self._challenge_cycle(self.challenge_count)
            if 0 >= result:
                logger.info(f'已成功挑战 {self.challenge_count} 题，正在返回')
                break
            else:
                delay_time = random.randint(2, 2)
                logger.info(f'本次挑战 {self.challenge_count - result} 题，{delay_time} 秒后再来一组')
                time.sleep(delay_time)
                continue

    def _challenge(self):
        logger.info(f'挑战答题 目标 {self.challenge_count} 题, Go!')
        while True:
            result = self._challenge_cycle(self.challenge_count)
            if 0 >= result:
                logger.info(f'已成功挑战 {self.challenge_count} 题，正在返回')
                break
            else:
                delay_time = random.randint(5, 10)
                logger.info(f'本次挑战 {self.challenge_count - result} 题，{delay_time} 秒后再来一组')
                time.sleep(delay_time)
                continue

    def _zhengshangyou(self):
        cyclenum = self.zhengshangyou_count
        # cyclenum = 5
        if cyclenum == 0:
            logger.info(f'争上游已经得到满分，跳过 ')
            return
        else:
            logger.info(f'争上游走{cyclenum}波！ ')
            while cyclenum > 0:
                result = self._zhengshangyou_cycle() - 1
                delay_time = random.randint(5, 10)
                logger.info(f'本次争上游作对 {result} 题')
                time.sleep(delay_time)
                cyclenum -= 1
                self.safe_back()
                continue

    def _shuangrenduizhan(self):
        if self.shuangrenduizhan_count == 0:
            logger.info(f'双人对战已经得到满分，跳过 ')
            return
        else:
            logger.info(f'双人对战走一波！ ')
            result = self._2_ren_cycle()
            delay_time = random.randint(5, 10)
            logger.info(f'本次双人对战作了 {result} 题')
            time.sleep(delay_time)
            self.safe_back()
            self.safe_click('//*[@text="退出"]')

    def challenge(self):
        if 0 == self.challenge_count:
            logger.info(f'挑战答题积分已达成，无需重复挑战')
            return
        self.safe_click(rules['mine_entry'])
        self.safe_click(rules['quiz_entry'])
        time.sleep(3)
        self._challenge()
        self.safe_back('quiz -> mine')
        self.safe_back('mine -> home')

    def challenge_test(self):

        self.safe_click(rules['mine_entry'])
        self.safe_click(rules['quiz_entry'])
        time.sleep(3)
        self._challenge_test()
        self.safe_back('quiz -> mine')
        self.safe_back('mine -> home')

    # 争上游答题模块
    def zhengshangyou(self):
        self.safe_click(rules['mine_entry'])
        self.safe_click(rules['quiz_entry'])
        time.sleep(3)
        self._zhengshangyou()
        self.safe_back('quiz -> mine')
        self.safe_back('mine -> home')

    # 双人对战模块
    def shuangrenduizhan(self):
        self.safe_click(rules['mine_entry'])
        self.safe_click(rules['quiz_entry'])
        time.sleep(3)
        self._shuangrenduizhan()
        self.safe_back('quiz -> mine')
        self.safe_back('mine -> home')

    # 每日答题模块
    # class Daily(App):
    def _daily_init(self):
        # super().__init__()
        self.g, self.t = 0, 6
        self.count_of_each_group = cfg.getint('prefers', 'daily_count_each_group')
        try:
            self.g, self.t = self.score["每日答题"]
            self.daily_count = self.t - self.g
            if self.daily_count > 0:
                self.daily_count = cfg.getint('prefers', 'daily_count')
            self.daily_force = False
        except:
            self.g, self.t = self.score["每日答题"]
            self.daily_count = self.t - self.g
            self.daily_force = False

        self.daily_delay_bot = cfg.getint('prefers', 'daily_delay_min')
        self.daily_delay_top = cfg.getint('prefers', 'daily_delay_max')

        self.delay_group_bot = cfg.getint('prefers', 'daily_group_delay_min')
        self.delay_group_top = cfg.getint('prefers', 'daily_group_delay_max')
        logger.debug(f"每日答题: {self.daily_count}")

    def _submit(self, delay=None):
        if not delay:
            delay = random.randint(self.daily_delay_bot, self.daily_delay_top)
            logger.info(f'随机延时 {delay} 秒...')
        time.sleep(delay)
        self.safe_click(rules["daily_submit"])
        time.sleep(random.randint(1, 3))

    def _view_tips(self):
        content = ""
        try:
            tips_open = self.driver.find_element_by_xpath(rules["daily_tips_open"])
            tips_open.click()
        except NoSuchElementException as e:
            logger.debug("没有可点击的【查看提示】按钮")
            return ""
        time.sleep(2)
        try:
            tips = self.wait.until(EC.presence_of_element_located((
                By.XPATH, rules["daily_tips"]
            )))
            content = tips.get_attribute("name")
            logger.debug(f'提示 {content}')
        except NoSuchElementException as e:
            logger.error(f'无法查看提示内容')
            return ""
        time.sleep(2)
        try:
            tips_close = self.driver.find_element_by_xpath(rules["daily_tips_close"])
            tips_close.click()

        except NoSuchElementException as e:
            logger.debug("没有可点击的【X】按钮")
        time.sleep(2)
        return content

    def _blank_answer_divide(self, ans: str, arr: list):
        accu_revr = [x for x in accumulate(arr)]
        print(accu_revr)
        temp = list(ans)
        for c in accu_revr[-2::-1]:
            temp.insert(c, " ")
        return "".join(temp)

    def _blank(self):
        contents = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, rules["daily_blank_content"])))
        # contents = self.find_elements(rules["daily_blank_content"])
        # content = " ".join([x.get_attribute("name") for x in contents])
        logger.debug(f'len of blank contents is {len(contents)}')
        # logger.info(contents)
        if 1 < len(contents):
            # 针对作妖的UI布局某一版
            content, spaces = "", []
            for item in contents:
                content_text = item.get_attribute("name")
                if "" != content_text:
                    content += content_text
                else:
                    length_of_spaces = len(item.find_elements(By.CLASS_NAME, "android.view.View")) - 1

                    spaces.append(length_of_spaces)
                    content += " " * (length_of_spaces)

        else:
            # 针对作妖的UI布局某一版
            contents = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, rules["daily_blank_container"])))
            content, spaces, _spaces = "", [], 0
            for item in contents:
                content_text = item.get_attribute("name")
                if "" != content_text:
                    content += content_text
                    if _spaces:
                        spaces.append(_spaces)
                        _spaces = 0
                else:
                    content += " "
                    _spaces += 1
            else:  # for...else...
                # 如果填空处在最后，需要加一个判断
                if _spaces:
                    spaces.append(_spaces)
                logger.debug(f'[填空题] {content} [{" ".join([str(x) for x in spaces])}]')
            logger.debug(f'空格数 {spaces}')
        blank_edits = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, rules["daily_blank_edits"])))
        # blank_edits = self.find_elements(rules["daily_blank_edits"])
        length_of_edits = len(blank_edits)
        logger.info(f'填空题 {content}')
        answer = self._verify("填空题", content, [])  #
        if not answer:
            words = (''.join(random.sample(string.ascii_letters + string.digits, 8)) for i in range(length_of_edits))
        else:
            words = answer.split(" ")
        logger.debug(f'提交答案 {words}')
        for k, v in zip(blank_edits, words):
            k.send_keys(v)
            time.sleep(1)

        self._submit()
        try:
            wrong_or_not = self.driver.find_element_by_xpath(rules["daily_wrong_or_not"])
            right_answer = self.driver.find_element_by_xpath(rules["daily_answer"]).get_attribute("name")
            answer = re.sub(r'正确答案： ', '', right_answer)
            logger.info(f"答案 {answer}")
            notes = self.driver.find_element_by_xpath(rules["daily_notes"]).get_attribute("name")
            logger.debug(f"解析 {notes}")
            self._submit(2)
            if 1 == length_of_edits:
                self._update_bank({
                    "category": "填空题",
                    "content": content,
                    "options": [""],
                    "answer": answer,
                    "excludes": "",
                    "notes": notes
                })
            else:
                logger.error("多位置的填空题待验证正确性")
                self._update_bank({
                    "category": "填空题",
                    "content": content,
                    "options": [""],
                    "answer": self._blank_answer_divide(answer, spaces),
                    "excludes": "",
                    "notes": notes
                })
        except:
            logger.debug("填空题回答正确")

    def _radio(self):
        content = self.wait.until(EC.presence_of_element_located((By.XPATH, rules["daily_content"]))).get_attribute(
            "name")
        content = content.replace("\x20", " ")
        content = content.replace("\xa0", " ")
        # content = self.find_element(rules["daily_content"]).get_attribute("name")
        option_elements = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, rules["daily_options"])))
        # option_elements = self.driver.find_elements(rules["daily_options"])
        options = [x.get_attribute("name") for x in option_elements]
        length_of_options = len(options)
        logger.info(f"单选题 {content}")
        logger.info(f"选项 {options}")
        answer = self._verify("单选题", content, options)
        choose_index = ord(answer) - 65
        logger.info(f"提交答案 {answer}")
        option_elements[choose_index].click()
        # 提交答案
        self._submit()
        try:
            wrong_or_not = self.driver.find_element_by_xpath(rules["daily_wrong_or_not"])
            right_answer = self.driver.find_element_by_xpath(rules["daily_answer"]).get_attribute("name")
            right_answer = re.sub(r'正确答案： ', '', right_answer)
            logger.info(f"答案 {right_answer}")
            # notes = self.driver.find_element_by_xpath(rules["daily_notes"]).get_attribute("name")
            # logger.debug(f"解析 {notes}")
            self._submit(2)
            self._update_bank({
                "category": "单选题",
                "content": content,
                "options": options,
                "answer": right_answer,
                "excludes": "",
                "notes": ""
            })
        except:
            self._update_bank({
                "category": "单选题",
                "content": content,
                "options": options,
                "answer": answer,
                "excludes": "",
                "notes": ""
            })
            return

    def _check(self):
        content = self.wait.until(EC.presence_of_element_located((By.XPATH, rules["daily_content"]))).get_attribute(
            "name")
        # content = self.find_element(rules["daily_content"]).get_attribute("name")
        option_elements = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, rules["daily_options"])))
        # option_elements = self.driver.find_elements(rules["daily_options"])
        options = [x.get_attribute("name") for x in option_elements]
        length_of_options = len(options)
        logger.info(f"多选题 {content}\n{options}")
        answer = self._verify("多选题", content, options)
        logger.debug(f'提交答案 {answer}')
        for k, option in zip(list("ABCDEFG"), option_elements):
            if k in answer:
                option.click()
                time.sleep(1)
            else:
                continue
        # 提交答案
        self._submit()
        try:
            wrong_or_not = self.driver.find_element_by_xpath(rules["daily_wrong_or_not"])
            right_answer = self.driver.find_element_by_xpath(rules["daily_answer"]).get_attribute("name")
            right_answer = re.sub(r'正确答案： ', '', right_answer)
            logger.info(f"答案 {right_answer}")
            # notes = self.driver.find_element_by_xpath(rules["daily_notes"]).get_attribute("name")
            # logger.debug(f"解析 {notes}")
            self._submit(2)
            self._update_bank({
                "category": "多选题",
                "content": content,
                "options": options,
                "answer": right_answer,
                "excludes": "",
                "notes": ""
            })
        except:
            # self._update_bank({
            #     "category": "多选题",
            #     "content": content,
            #     "options": options,
            #     "answer": answer,
            #     "excludes": "",
            #     "notes": ""
            # })
            return

    def _dispatch(self, count_of_each_group):
        time.sleep(3)  # 如果模拟器比较流畅，这里的延时可以适当调短
        for i in range(count_of_each_group):
            logger.debug(f'正在答题 第 {i + 1} / {count_of_each_group} 题')
            try:
                category = self.driver.find_element_by_xpath(rules["daily_category"]).get_attribute("name")
            except NoSuchElementException as e:
                logger.error(f'无法获取题目类型')
                raise e
            if "填空题" == category:
                self._blank()
            elif "单选题" == category:
                self._radio()
            elif "多选题" == category:
                self._check()
            else:
                logger.error(f"未知的题目类型: {category}")

    def _daily(self, num):
        self.safe_click(rules["daily_entry"])
        while num:
            num -= 1
            logger.info(f'每日答题 第 {num}# 组')
            self._dispatch(self.count_of_each_group)
            if not self.daily_force:
                score = self.wait.until(EC.presence_of_element_located((By.XPATH, rules["daily_score"]))).get_attribute(
                    "name")
                # score = self.find_element(rules["daily_score"]).get_attribute("name")
                try:
                    score = int(score)
                except:
                    raise TypeError('integer required')
                self.g += score
                if self.g >= self.t:
                    logger.info(f"今日答题已完成，返回")
                    break
            if num == 0:
                logger.debug(f'今日循环结束 <{self.g} / {self.t}>')
                break
            delay = random.randint(self.delay_group_bot, self.delay_group_top)
            logger.info(f'每日答题未完成 <{self.g} / {self.t}> {delay} 秒后再来一组')
            time.sleep(delay)
            self.safe_click(rules['daily_again'])
            continue
        else:
            logger.debug("应该不会执行本行代码")

        self.safe_back('daily -> quiz')
        try:
            back_confirm = self.driver.find_element_by_xpath(rules["daily_back_confirm"])
            back_confirm.click()
        except:
            logger.debug(f"无需点击确认退出")

    def daily(self):
        if 0 == self.daily_count:
            logger.info(f'每日答题积分已达成，无需重复答题')
            return
        self.safe_click(rules['mine_entry'])
        self.safe_click(rules['quiz_entry'])
        time.sleep(3)
        self._daily(self.daily_count)
        self.safe_back('quiz -> mine')
        self.safe_back('mine -> home')

    # 新闻阅读模块
    # class Read(App):
    def _read_init(self):
        # super().__init__()
        self.read_time = 720
        self.volumn_title = cfg.get("prefers", "article_volumn_title")
        self.star_share_comments_count = cfg.getint("prefers", "star_share_comments_count")
        self.titles = list()
        # try:
        #     self.read_count = cfg.getint("prefers", "article_count")
        #     self.read_delay = 30
        # except:
        g, t = self.score["我要选读文章"]
        if t == g:
            self.read_count = 0
            self.read_delay = random.randint(45, 60)
        else:
            self.read_count = (t - g) // 2 + 3
            # self.read_count = random.randint(
            #     cfg.getint('prefers', 'article_count_min'),
            #     cfg.getint('prefers', 'article_count_max'))
            self.read_delay = self.read_time // (self.read_count + 1) + 1
        logger.debug(f'我要选读文章: {self.read_count}')

    def _star_once(self):
        # if self.back_or_not("收藏"):
        #     return
        logger.debug(f'这篇文章真是妙笔生花呀！收藏啦！')
        self.safe_click(rules['article_stars'])
        # self.safe_click(rules['article_stars']) # 取消收藏

    def _comments_once(self, title="好好学习，天天强国"):
        # return # 拒绝留言
        # if self.back_or_not("发表观点"):
        #     return
        logger.debug(f'哇塞，这么精彩的文章必须留个言再走！')
        self.safe_click(rules['article_comments'])
        edit_area = self.wait.until(EC.presence_of_element_located((By.XPATH, rules['article_comments_edit'])))
        # edit_area = self.find_element(rules['article_comments_edit'])
        edit_area.send_keys(title)
        self.safe_click(rules['article_comments_publish'])
        time.sleep(2)
        self.safe_click(rules['article_comments_list'])
        self.safe_click(rules['article_comments_delete'])
        self.safe_click(rules['article_comments_delete_confirm'])

    def _share_once(self):
        # if self.back_or_not("分享"):
        #     return
        logger.debug(f'好东西必须和好基友分享，走起，转起！')
        self.safe_click(rules['article_share'])
        self.safe_click(rules['article_share_xuexi'])
        time.sleep(3)
        self.safe_back('share -> article')

    def _star_share_comments(self, title):
        logger.debug(f'好，支持，威武')
        if random.random() < 0.33:
            self._comments_once(title)
            if random.random() < 0.5:
                self._star_once()
                self._share_once()
            else:
                self._share_once()
                self._star_once()
        else:
            if random.random() < 0.5:
                self._star_once()
                self._share_once()
            else:
                self._share_once()
                self._star_once()
            self._comments_once(title)

    def _read(self, num, ssc_count):
        logger.info(f'预计阅读新闻 {num} 则')
        while num > 0:  # or ssc_count:
            try:
                articles = self.driver.find_elements_by_xpath(rules['article_list'])
            except:
                logger.debug(f'真是遗憾，一屏都没有可点击的新闻')
                articles = []
            for article in articles:
                try:
                    title = article.get_attribute("name")
                except Exception as ex:
                    logger.info(f'文章列表可能刷新了，找不到了，重新获取，请忽略以下错误：{ex}')
                    continue
                if title in self.titles:
                    continue
                try:
                    pic_num = article.parent.find_element_by_id("cn.xuexi.android:id/st_feeds_card_mask_pic_num")
                    logger.debug(f'这绝对是摄影集，直接下一篇')
                    continue
                except:
                    logger.debug(f'这篇文章应该不是摄影集了吧')
                article.click()
                num -= 1
                logger.info(f'<{num}> 当前篇目 {title}')
                article_delay = random.randint(60, 60 + min(10, self.read_count))
                logger.info(f'阅读时间估计 {article_delay} 秒...')
                while article_delay > 0:
                    if article_delay < 20:
                        delay = article_delay
                    else:
                        delay = random.randint(min(10, article_delay), min(20, article_delay))
                    logger.debug(f'延时 {delay} 秒...')
                    time.sleep(delay)
                    article_delay -= delay
                    self.swipe_up()
                else:
                    logger.debug(f'完成阅读 {title}')

                if ssc_count > 0:
                    try:
                        comment_area = self.driver.find_element_by_xpath(rules['article_comments'])
                        self._star_share_comments(title)
                        ssc_count -= 1
                    except Exception as ex:
                        logger.info(f'评论转发出现异常：    %s' % ex)
                        logger.debug('这是一篇关闭评论的文章，收藏分享留言过程出现错误')

                self.titles.append(title)
                self.safe_back('article -> list')
                if 0 >= num:
                    break
            self.swipe_up()

    def _comment_only(self, ssc_count):
        logger.info(f'评论，转发{ssc_count} 则')
        while ssc_count > 0:  # or ssc_count:
            try:
                articles = self.driver.find_elements_by_xpath(rules['article_list'])
            except:
                logger.debug(f'真是遗憾，一屏都没有可点击的新闻')
                articles = []
            for article in articles:
                title = article.get_attribute("name")
                if title in self.titles:
                    continue
                try:
                    pic_num = article.parent.find_element_by_id("cn.xuexi.android:id/st_feeds_card_mask_pic_num")
                    logger.debug(f'这绝对是摄影集，直接下一篇')
                    continue
                except:
                    logger.debug(f'这篇文章应该不是摄影集了吧')
                article.click()
                # ssc_count -= 1
                logger.info(f'<{ssc_count}> 当前篇目 {title}')
                article_delay = 10
                logger.info(f'阅读时间估计 {article_delay} 秒...')
                time.sleep(5)
                ssc_count = ssc_count - 1
                try:
                    comment_area = self.driver.find_element_by_xpath(rules['article_comments'])
                    self._star_share_comments(title)
                except Exception as ex:
                    logger.info(f'转发评论出现如下异常    %s' % ex)
                    logger.debug('这是一篇关闭评论的文章，收藏分享留言过程出现错误')

                self.titles.append(title)
                self.safe_back('article -> list')
                if 0 >= ssc_count:
                    break
            else:
                self.swipe_up()

    def _kaleidoscope(self):
        """ 本地频道积分 +1 """
        if self.back_or_not("本地频道"):
            return
        volumns = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, rules['article_volumn'])))
        volumns[3].click()
        time.sleep(10)
        # self.safe_click(rules['article_kaleidoscope'])
        target = None
        try:
            target = self.driver.find_element_by_xpath(rules['article_kaleidoscope'])
        except NoSuchElementException as e:
            logger.error(f'没有找到城市万花筒入口')

        if target:
            target.click()
            time.sleep(3)
            delay = random.randint(5, 15)
            logger.info(f"在本地学习平台驻足 {delay} 秒")
            time.sleep(delay)
            self.safe_back('学习平台 -> 文章列表')
            time.sleep(2)

    def _get_article_vol(self):
        vol_not_found = True
        while vol_not_found:
            # 顶多右划4次，找不到就返回
            right_slide = 3
            while right_slide >= 0:
                try:
                    volumns = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, rules['article_volumn'])))
                # volumns = self.find_elements(rules['article_volumn'])
                except:
                    self.safe_back('mine -> home')
                    volumns = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, rules['article_volumn'])))
                first_vol = volumns[1]
                for vol in volumns:
                    title = vol.get_attribute("name")
                    logger.debug(title)
                    if self.volumn_title == title:
                        vol.click()
                        # 找到约定栏目，标记退出循环
                        vol_not_found = False
                        right_slide = -2
                        break
                else:
                    logger.debug(f'未找到 {self.volumn_title}，右划')
                    # self.safe_click(rules['article_share'])
                    # self.safe_back('mine -> home')
                    self.driver.scroll(vol, first_vol, duration=500)
                    right_slide = right_slide - 1

    def read(self):
        logger.info(f"阅读 {self.read_count} 篇文章")

        if 0 == self.read_count:
            g, t = self.score["本地频道"]
            if t == g:
                logger.info(f'本地频道已达成，跳过')
            else:
                self.safe_click('//*[@resource-id="cn.xuexi.android:id/home_bottom_tab_button_work"]')
                self._kaleidoscope()
                self._get_article_vol()
            g, t = self.score["发表观点"]
            g1, t1 = self.score["分享"]
            if t == g and g1 == t1:
                logger.info(f'新闻阅读订阅均已达成，跳过')
                return
            else:
                self.safe_click('//*[@resource-id="cn.xuexi.android:id/home_bottom_tab_button_work"]')
                logger.info(f'新闻阅读已达成，无需重复阅读,只评论转发')
                self._comment_only(self.star_share_comments_count)
            return
        logger.debug(f'正在进行新闻学习...')
        # 找指定的新闻阅读频道
        # self.safe_click('//*[@resource-id="cn.xuexi.android:id/home_bottom_tab_button_work"]')
        # self._get_article_vol()
        self.safe_click('//*[@resource-id="cn.xuexi.android:id/home_bottom_tab_button_work"]')
        self._kaleidoscope()
        self._get_article_vol()
        self._read(self.read_count, self.star_share_comments_count)

    # 视听学习模块
    # class View(App):
    def _view_init(self):
        # super().__init__()
        self.has_bgm = cfg.get("prefers", "radio_switch")
        if "disable" == self.has_bgm:
            self.view_time = 1080
        else:
            self.view_time = 360
        self.radio_chanel = cfg.get("prefers", "radio_chanel")
        self.poem_chanel = cfg.get("prefers", "poem_chanel")
        try:
            self.video_count = cfg.getint("prefers", "video_count")
            self.view_delay = 15
        except:
            g, t = self.score["视听学习"]
            if t == g:
                self.video_count = 0
                self.view_delay = random.randint(15, 30)
            else:
                # self.video_count = random.randint(
                #     cfg.getint('prefers', 'video_count_min'),
                #     cfg.getint('prefers', 'video_count_max'))
                # self.view_delay = self.view_time // self.video_count + 1
                self.video_count = t - g
                self.view_delay = 30
        logger.debug(f'视听学习: {self.video_count}')

    def music(self):
        if "disable" == self.has_bgm:
            logger.debug(f'广播开关 关闭')
        elif "enable" == self.has_bgm:
            logger.debug(f'广播开关 开启')
            self._music()
        else:
            logger.debug(f'广播开关 默认')
            g, t = self.score["视听学习时长"]
            if g == t:
                logger.debug(f'视听学习时长积分已达成，无需重复收听')
                return
            else:
                self._music()

    def poem(self):
        if not self.video_count:
            logger.info('视听学习积分已达成，无须读诗歌')
            return
        logger.info(f'正在打开《{self.poem_chanel}》...')
        time.sleep(3)
        self._poem()
        time.sleep(1)
        self.safe_back()
        self.safe_back()
        self.safe_back()
        self.safe_back()

    def _poem(self):
        self.safe_click('//*[@resource-id="cn.xuexi.android:id/img_search_left"]')
        edit_area = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@resource-id="android:id/search_src_text"]')))
        # edit_area = self.find_element(rules['article_comments_edit'])
        edit_area.send_keys("唐诗三百首")
        self.driver.keyevent(66)
        time.sleep(8)
        self.safe_click('//android.view.View[@text="唐诗三百首·五言绝句"]')
        time.sleep(3)
        self.safe_click('//android.widget.TextView[@text="全部播放"]')

    def _music(self):
        logger.debug(f'正在打开《{self.radio_chanel}》...')
        self.safe_click('//*[@resource-id="cn.xuexi.android:id/home_bottom_tab_button_mine"]')
        self.safe_click('//*[@text="听新闻广播"]')
        self.safe_click(f'//*[@text="{self.radio_chanel}"]')
        self.safe_click(rules['home_entry'])
        self.safe_back("退到首页")

    def _watch(self, video_count=None):
        if not video_count:
            logger.info('视听学习积分已达成，无须重复视听')
            return
        logger.info("开始浏览百灵视频...")
        self.safe_click(rules['bailing_enter'])
        self.safe_click(rules['bailing_enter'])  # 再点一次刷新短视频列表
        self.safe_click(rules['video_first'])
        logger.info(f'预计观看视频 {video_count} 则')
        while video_count:
            video_count -= 1
            video_delay = random.randint(self.view_delay, self.view_delay + min(10, self.video_count))
            logger.info(f'正在观看视频 <{video_count}#> {video_delay} 秒进入下一则...')
            time.sleep(video_delay)
            self.swipe_up()
        else:
            logger.info(f'视听学习完毕，正在返回...')
            self.safe_back('video -> bailing')
            logger.debug(f'正在返回首页...')
            # self.safe_click(rules['//*[@resource-id="cn.xuexi.android:id/home_bottom_tab_button_work"'])
            self.view_score()
    def refresh(self, num):
        while num > 0:
            num -= 1
            if self.driver.current_package == caps["apppackage"]:
                try:
                    logger.info('尝试退出登录！')
                    self.logout_or_not()
                    break
                except Exception as ex:
                    logger.info(f'退出出现异常, 尝试捕获APP卡顿菜单')
                    try:
                        logger.info('尝试点击《等待》或者《取消》或者《退出》按钮')
                        self.safe_click('//*[@text="等待" or @text="取消" or @text="退出"]')
                        break
                    except:
                        logger.info('没有找到相关按钮，尝试返回上一层再试试运气')
                        self.safe_back()
            else:
                self.driver.activate_app(caps["apppackage"])
                time.sleep(5)
        if num == 0:
            logger.info('就是tm退不出，重启app')
            self.driver.close_app()
            self.driver.session.clear()
            self.driver.quit()
            self.__init__()

    def watch(self):
        self._watch(self.video_count)

    # class Weekly(App):
    def _weekly_init(self):
        self.workdays = cfg.get("prefers", "workdays")
        logger.debug(f"每周答题: {self.workdays}")

    def _weekly(self):
        self.safe_click(rules["weekly_entry"])
        titles = self.wait.until(
            EC.presence_of_all_elements_located((By.XPATH, rules["weekly_titles"])))

        states = self.wait.until(
            EC.presence_of_all_elements_located((By.XPATH, rules["weekly_states"])))

        # first, last = None, None
        for title, state in zip(titles, states):
            # if not first and title.location_in_view["y"]>0:
            #     first = title
            if self.size["height"] - title.location_in_view["y"] < 10:
                logger.debug(f'屏幕内没有未作答试卷')
                break
            logger.debug(f'{title.get_attribute("name")} {state.get_attribute("name")}')
            if "未作答" == state.get_attribute("name"):
                logger.info(f'{title.get_attribute("name")}, 开始！')
                state.click()
                time.sleep(random.randint(5, 9))
                self._dispatch(5)  # 这里直接采用每日答题
                break
        self.safe_back('weekly report -> weekly list')
        self.safe_back('weekly list -> quiz')

    def weekly(self):
        """ 每周答题
            复用每日答题的方法，无法保证每次得满分，如不能接受，请将配置workdays设为0
        """
        day_of_week = datetime.now().isoweekday()
        if str(day_of_week) not in self.workdays:
            logger.debug(f'今日不宜每周答题 {day_of_week} / {self.workdays}')
            return
        if self.back_or_not("每周答题"):
            return

        self.safe_click(rules['mine_entry'])
        self.safe_click(rules['quiz_entry'])
        time.sleep(3)
        self._weekly()
        self.safe_back('quiz -> mine')
        # self.safe_back('mine -> home')

    def _special_init(self):
        self.special_topic = cfg.get("prefers", "special_topic")
        logger.debug(f"专项答题: {self.special_topic}")

    def _special(self):
        self.safe_click(rules["special_entry"])
        # 这里需要增加下滑模块
        while True:
            titles = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, '//*[@text="开始答题"]')))
            if 0 == len(titles):
                logger.info("本页所有专题全部答完，下滑寻找新的专题！")
                self.swipe_up()
                try:
                    self.driver.find_elements_by_xpath('//*[@text="您已经看到了我的底线"]')
                    logger.info("滑到底了！,找不到未做的题目，退出。")
                    self.safe_back()
                    return
                except:
                    continue
            else:
                break
        titles[0].click()
        logger.info(f'专项答题, 开始！')
        time.sleep(random.randint(1, 3))
        self._special_dispatch(10)  # 这里和每日答题不一样，首先比对题库，其次在看提示蒙题
        self.safe_back('weekly report -> weekly list')
        self.safe_back('weekly list -> quiz')

    def special(self):
        """ 专项答题
            复用每日答题的方法，无法保证每次得满分，如不能接受，请将配置special_topic设为disable
        """
        if self.special_topic != 'enable':
            logger.info(f'没有打开专项答题开关，跳过！')
            return
        g, t = self.score["专项答题"]
        if g > 0:
            logger.info(f'专项答题已经有积分，不再重复答题！')
            return
        self.safe_click(rules['mine_entry'])
        self.safe_click(rules['quiz_entry'])
        time.sleep(3)
        self._special()
        self.safe_back('quiz -> mine')

    def _special_dispatch(self, count_of_each_group):
        time.sleep(3)  # 如果模拟器比较流畅，这里的延时可以适当调短
        for i in range(count_of_each_group):
            logger.debug(f'正在答题 第 {i + 1} / {count_of_each_group} 题')
            try:
                category = self.driver.find_element_by_xpath(rules["special_category"]).get_attribute("name")
            except NoSuchElementException as e:
                logger.error(f'无法获取题目类型')
                raise e
            if "填空题" in category:
                self._blank()
            elif "单选题" in category:
                self._radio()
            elif "多选题" in category:
                self._check()
            else:
                logger.error(f"未知的题目类型: {category}")
