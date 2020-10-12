#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@project: AutoXue-multiuser
@file: __main__.py
@time: 2020年9月29日10:55:28
@Copyright © 2020. All rights reserved.
"""

import json
import requests
from .unit import cfg, logger


class Structure:
    _fields = []

    def __init__(self, *args, **kwargs):
        if len(args) > len(self._fields):
            raise TypeError('Expected {} arguments'.format(len(self._fields)))

        # Set all of the positional arguments
        for name, value in zip(self._fields, args):
            setattr(self, name, value)

        # Set the remaining keyword arguments
        for name in self._fields[len(args):]:
            setattr(self, name, kwargs.pop(name))

        # Check for any remaining unknown arguments
        if kwargs:
            raise TypeError('Invalid argument(s): {}'.format(','.join(kwargs)))


class Bank(Structure):
    _fields = ['id', 'category', 'content', 'options', 'answer', 'excludes', 'description']

    def __repr__(self):
        return f'{self.content}'

    def to_json(self):
        pass

    @classmethod
    def from_json(self, data):
        pass


class BankQuery:
    def __init__(self):
        self.url = cfg.get('api', 'url')
        self.headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
        }

    def post(self, item, url=None):
        if not url:
            url = self.url
        if "" == item["content"]:
            logger.debug(f'content is empty')
            return False
        # logger.debug(f'POST {item["content"]} {item["options"]} {item["answer"]} {item["excludes"]}...')
        # python 复制列表为不同的引用指向同一个地址，所以这里拓展options影响了函数外的变量，不可取，应采用深拷贝实现
        options = item["options"][:]
        options.extend([""] * (6 - len(item["options"])))
        try:
            res = requests.post(url=url, headers=self.headers, json={
                "category": item["category"],
                "content": item["content"],
                "itemA": options[0],
                "itemB": options[1],
                "itemC": options[2],
                "itemD": options[3],
                "itemE": options[4],
                "itemF": options[5],
                "answer": item.get("answer", ""),
                "excludes": item.get("excludes", ""),
                "notes": item.get("notes", "")
            })
            if 200 == res.status_code:
                res = json.loads(res.text)
                return res["data"]
        except:
            return None

    def put(self, item, url=None):
        if not url:
            url = self.url
        if "" == item["content"]:
            logger.debug(f'content is empty')
            return False
        logger.debug(f'PUT {item["content"]} {item["options"]} {item["answer"]} {item["excludes"]}...')
        try:
            res = requests.put(url=url, headers=self.headers, json=item)
            if 201 == res.status_code:
                logger.info('添加新记录')
                return True
            elif 200 == res.status_code:
                logger.info('更新记录')
                return True
            else:
                logger.debug("PUT do nothing")
                return False
        except:
            return False

    def get(self, item, url=None):
        if not url:
            url = self.url
        if "" == item["content"]:
            logger.debug(f'content is empty')
            return None
        logger.debug(f'GET {item["content"]}...')
        try:
            res = requests.post(url=url, headers=self.headers, json=item)
            if 200 == res.status_code:
                logger.debug(f'GET item success')
                # logger.debug(res.text)
                # logger.debug(json.loads(res.text))
                return json.loads(res.text)
            else:
                logger.debug(f'GET item failure')
                return None
        except:
            logger.debug('request faild')
            return None
