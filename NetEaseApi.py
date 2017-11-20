# -*- coding: utf-8 -*-
# @Author : Huangcc

import json
import base64
from Crypto.Cipher import AES
import requests
import hashlib
import os


class NetEaseApi:
    # 基于 gaoyuan427 的github项目进行修改 https://github.com/gaoyuan427/NetEaseMusicSync
    # 感谢 gaoyuan427 提供的网易云音乐api

    def __init__(self):
        self.session = requests.session()
        self.cookies = None

    def _aes_encrypt(self, text, sec_key):
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(sec_key, 2, '0102030405060708')
        cipher_text = encryptor.encrypt(text)
        cipher_text = base64.b64encode(cipher_text)
        return cipher_text

    def _rsa_encrypt(self, text, pub_key, modulus):
        text = text[::-1]
        rs = int(text.encode('hex'), 16) ** int(pub_key, 16) % int(modulus, 16)
        return format(rs, 'x').zfill(256)

    def _create_secret_key(self, size):
        return (''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(size))))[0:16]

    def get_info_from_nem(self, url, params):
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'music.163.com',
            'Referer': 'http://music.163.com/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36'
        }
        modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
        nonce = '0CoJUm6Qyw8W8jud'
        pub_key = '010001'
        params = json.dumps(params)
        sec_key = self._create_secret_key(16)
        enc_text = self._aes_encrypt(self._aes_encrypt(params, nonce), sec_key)
        enc_sec_key = self._rsa_encrypt(sec_key, pub_key, modulus)
        data = {
            'params': enc_text,
            'encSecKey': enc_sec_key
        }
        req = self.session.post(url, headers=headers, data=data)
        return req.json()

    def get_play_list(self, uid):
        url = 'http://music.163.com/weapi/user/playlist?csrf_token='
        params = {
            'offset': '0',
            'limit': '9999',
            'uid': str(uid)
        }
        return self.get_info_from_nem(url, params)

    def get_play_list_info(self, music_list_id):
        url = 'http://music.163.com/weapi/playlist/detail?csrf_token='
        params = {'id': str(music_list_id)}
        return self.get_info_from_nem(url, params)

    def get_music_url(self, music_id):
        url = 'http://music.163.com/weapi/song/enhance/player/url?csrf_token='
        if type([]) != type(music_id):
            music_id = [music_id]
        params = {
            "ids": str(music_id),
            "br": '320000'
        }
        return self.get_info_from_nem(url, params)

    def cellphone_login(self, username, password):
        url = 'http://music.163.com/weapi/login/cellphone?csrf_token='
        data = {'phone': username, 'password': hashlib.md5(password).hexdigest(),
                'rememberLogin': "true"}
        return self.get_info_from_nem(url, data)

    def get_daily_recommend(self):
        url = 'http://music.163.com/weapi/v2/discovery/recommend/songs?csrf_token='
        data = {
            'csrf_token': '',
            'limit': '999',
            'offset': '0',
            'total': 'true'
        }
        return self.get_info_from_nem(url, data)
