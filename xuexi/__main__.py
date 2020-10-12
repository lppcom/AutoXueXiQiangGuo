#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@project: AutoXue-multiuser
@file: __main__.py
@time: 2020年9月29日10:55:28
@Copyright © 2020. All rights reserved.
"""
import sys
import time

from . import App
from .secureRandom import SecureRandom as random
from .unit import logger, usernames


# parse = ArgumentParser(description="Accept username and password if necessary!")
#
# parse.add_argument("-u", "--username", metavar="username", type=str, default='', help='User Name')
# parse.add_argument("-p", "--password", metavar="password", type=str, default='', help='Pass Word')
# args = parse.parse_args()
# app = App(args.username, args.password)


def shuffle(funcs):
    random.shuffle(funcs)
    for func in funcs:
        func()
        time.sleep(5)


def start():
    logger.debug(f'视听学习置后')
    app.music()
    # app.poem()
    shuffle([app.daily, app.challenge, app.zhengshangyou, app.shuangrenduizhan, app.special, app.read, app.weekly])
    app.view_score()
    app.watch()
    app.logout_or_not()
    # app.driver.close_app()
    # app.driver.session.clear()
    # app.driver.quit()


def connect_error(exMess):
    if "An unknown server-side error occurred while processing the command" in exMess:
        return True
    else:
        return False


def test():
    # app.CodePic_to_phone("C:/Users/yangz/Desktop/下载.png", "/system/temp/")
    # app.challenge_test()
    # app.zhengshangyou()
    logger.info(f'测试完毕')


if __name__ == "__main__":

    # 更新题库
    # xuexitiaozhan = Tiku()
    # xuexitiaozhan.get_tiku()

    # 获取用户名列表
    user_list = []
    users_list = []
    user_value = True
    for username in usernames.values():
        # logger.info(username)
        if user_value:
            user_list.append(username)
            user_value = False
        else:
            user_list.append(username)
            users_list.append(user_list)
            # print(user_list)
            user_list = []
            user_value = True
    print("本次学习以下账号：")
    print(users_list)
    # users_list = [
    #     ['17600000000', 'Nopass.123'],
    #     ['18600000000', '0000
    #     00'],
    #     ['1770000000', '000000'],
    # ]
    app = App()
    for index_u, user in enumerate(users_list):
        # 定义一个APP的启动时间，超时1小时换下一个
        t = time.time()
        while True:
            try:
                app.initapp(user[0], user[1])
                # test()
                start()
                break
            except Exception as ex:
                logger.info("刷分出现如下错误:")
                logger.info(ex)
                if "An unknown server-side error occurred while processing" in str(ex):
                    try:
                        logger.info("尝试重启APP")
                        app.driver.close_app()
                        app.driver.session.clear()
                        app.driver.quit()
                        app = App()
                    except:
                        app = App()
                else:
                    app.refresh(3)
                if time.time() - t > 3600:
                    logger.info(f'程序存在错误，试了一个小时都不行，换下个号码刷')
                    break
    sys.exit(0)
