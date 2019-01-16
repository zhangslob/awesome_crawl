#!/usr/bin/env python  
# -*- coding: utf-8 -*-
"""
@author: zhangslob
@file: douyu_websocket_client.py 
@time: 2018/12/26
@desc: 抓取斗鱼指定直播间弹幕消息
        可以多线程抓取，将房间ID添加到`room_list`即可
"""

import os
import re
import pytz
import time
import json
import socket
import hashlib
import pymongo
import requests
import threading
import logging

from tenacity import *
from datetime import datetime

mongodb_uri = 'mongodb://127.0.0.1:27017/douyu'
mongodb_client = pymongo.MongoClient(os.environ.get('MONGODB_URL', mongodb_uri))
logging.basicConfig(level=logging.INFO, stream=sys.stdout)


def get_today():
    today = datetime.fromtimestamp(int(time.time()), pytz.timezone('Asia/Shanghai')).strftime('%Y_%m_%d')
    return today


class BaseWebsocket(object):
    def __init__(self, room_id):
        self.room_id = room_id
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostbyname("openbarrage.douyutv.com")
        port = 8601
        self.client.connect((host, port))
        self.chat_msg = re.compile(
            b'type@=chatmsg/.+?/uid@=(.+?)/nn@=(.+?)/txt@=(.+?)/.+?/level@=(.+?)/.+?/bnn@=(.*?)/bl@=(.+?)/.+?')  # 弹幕
        self.gift_msg = re.compile(b'type@=dgb/.+?/gfid@=(.+?)/.+?/nn@=(.+?)/.+?')  # 礼物
        self.gift_list = dict()
        self.database = mongodb_client.get_database()
        self.db = self.database['{}_{}'.format(self.room_id, get_today())]
        self.db.create_index('unique_key', unique=True)
        self._running = True

    def send_msg(self, msg_str):
        msg = msg_str.encode('utf-8')
        data_length = len(msg) + 8
        code = 689
        msg_head = int.to_bytes(data_length, 4, 'little') + \
                   int.to_bytes(data_length, 4, 'little') + int.to_bytes(code, 4, 'little')
        self.client.send(msg_head)
        sent = 0
        while sent < len(msg):
            tn = self.client.send(msg[sent:])
            sent = sent + tn

    def get_gift_list(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        url = 'http://open.douyucdn.cn/api/RoomApi/room/' + str(self.room_id)
        room_info = requests.get(url, headers=headers).json()['data']
        for each in room_info['gift']:
            self.gift_list[each['id']] = each['name']
            logging.info('{}, {}'.format(each['id'], each['name']))

    def open(self):
        msg = 'type@=loginreq/roomid@={}/\x00'.format(self.room_id)
        self.send_msg(msg)
        join_room_msg = 'type@=joingroup/rid@={}/gid@=-9999/\x00'.format(self.room_id)  # 加入房间分组消息
        self.send_msg(join_room_msg)
        logging.info("Succeed logging in")

        while True:
            try:
                data = self.client.recv(2048)  # bytes-like-objects
                # print(str(data[12:], 'utf-8', 'ignore'))
                if not data:
                    pass
                for gid, nn in self.gift_msg.findall(data):
                    if gid.decode() in list(self.gift_list.keys())[:4]:
                        gift_id = str(gid.decode())
                        logging.info("---[{}]送出----{}---".format(nn.decode(), self.gift_list[gift_id]))  # 礼物部分
                        gift = dict()
                        gift['nn'] = nn.decode()
                        gift['gift_id'] = self.gift_list[gift_id]
                        self.save_mongodb(gift)

            except Exception as e:
                logging.info(e)
                logging.info('-------礼物 Decode error---------')
                pass
            # for uid,nn,txt,level,bnn,bl in chatmsg.findall(data):
            # print(data)
            try:
                for uid, nn, txt, level, bnn, bl in self.chat_msg.findall(data):
                    if bl.decode() == '0':
                        bnn = b'NONE'

                        logging.info("[{}({})][lv.{}][{}]: {} ".format(
                        bnn.decode(), bl.decode(), level.decode(),
                        nn.decode(errors='ignore'), txt.decode(errors='ignore').strip()))
                    danmu = dict()
                    danmu['bnn'] = bnn.decode()
                    danmu['bl'] = bl.decode()
                    danmu['level'] = level.decode()
                    danmu['nn'] = nn.decode(errors='ignore')
                    danmu['txt'] = txt.decode(errors='ignore').strip()
                    self.save_mongodb(danmu)

                time.sleep(0.05)  # continue
            except Exception as e:
                logging.info(e)
                logging.info('-------弹幕 Decode error---------')

    def keep_live(self):
        while True:
            # msg = 'type@=keeplive/tick@=' + str(int(time.time())) + '/\0'
            msg = 'type@=mrkl/'
            self.send_msg(msg)
            time.sleep(40)

    def create_mongo_index(self):
        names = self.database.collection_names()
        today_db = '{}_{}'.format(self.room_id, get_today())
        if today_db not in names:
            self.db = self.database[today_db]
            self.db.create_index('unique_key', unique=True)

    def save_mongodb(self, data):
        hash_str = json.dumps(data)
        hl = hashlib.md5()
        hl.update(hash_str.encode('utf-8'))
        data['unique_key'] = hl.hexdigest()
        data['created_time'] = datetime.fromtimestamp(int(time.time()), pytz.timezone('Asia/Shanghai'))
        data['created_time_ts'] = int(time.time() * 1000)
        try:
            self.create_mongo_index()
            self.db.insert_one(data)
        except pymongo.errors.DuplicateKeyError:
            pass

    def main(self):
        self.get_gift_list()
        t1 = threading.Thread(target=self.keep_live)
        t1.setDaemon(True)
        t1.start()

        while True:
            self._running = True
            t = threading.Thread(target=self.open)
            t.start()
            t.join()


if __name__ == '__main__':
    # '208114',
    room_list = ['4537144']
    for i in room_list:
        w = BaseWebsocket(i)
        t = threading.Thread(target=w.main)
        t.start()
