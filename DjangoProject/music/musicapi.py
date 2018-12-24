#!/usr/bin/env python
# encoding: utf-8

import requests
import random, math
from Crypto.Cipher import AES
import base64
import codecs
import os
from django.conf import settings
from django.shortcuts import HttpResponse

"""
获取歌曲地址：https://music.163.com/weapi/song/enhance/player/url?csrf_token=429d8812f4449bb9acb60e7647113999
"""


class Spider(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
            'Cookie': 'vjuids=-10d568a29.15ce8403fa5.0.4df3ca9c09c25; _ntes_nuid=b2828e3f6ee88d36d522e6f8ba8b2fb9; vjlast=1498545144.1500548341.13; _ga=GA1.2.2086505493.1502191838; usertrack=ezq0pFtW5nxVGTpYBv1TAg==; _ntes_nnid=b2828e3f6ee88d36d522e6f8ba8b2fb9,1532421743728; _iuqxldmzr_=32; WM_TID=GYPUVWfZh9dX166chRdLCLPrt8GJeUcp; __remember_me=true; __utmz=94650624.1539159615.21.5.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmc=94650624; __utma=94650624.2086505493.1502191838.1539318372.1539324670.23; WM_NI=feGZ0JMD5rDlVFomUmwxy9%2F1bVATLeFmeFHmPy6jfUrLf2e%2BWNZLjl9jsoZ0LoR%2F9umMSGBx%2BAINYju652SRK7t70yI5X1xz83yYUaTUB%2F%2FMOV9nIgii9ihxslXe%2FPuEYTQ%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee92ea4d8c8bfad2d239fb8e8aa6c54b928b8aaabc6f88f0f8ccd2399c9b9fccb62af0fea7c3b92aa6bb89bbb3428f9cfb93c768969aa18ed867b5a8b7daae3ba28a8fb5cf6f86b3aba7cb6794a7fa8be55fb294aad3e821959296ade968fbb6bd90d93c90b19ed0bc7faf939da8c174e99f87afdc62b7eafbd3d25a89e9bcd8b3738beb98d2fb72fcedb7bad86b988b8ed0ae478d8af78fcc6dabb7f78aeb74b1b49886ae5cb79b97b5d437e2a3; MUSIC_U=f4f6655b93b6234d31c9ea50482e49e0af222276a9320b1cc285b3452db917355a95e930ab32c229376ed803f19fb4737e88693155b77f7b9f87406c925553ba33bb3b2e18397611bf122d59fa1ed6a2; __csrf=4ca1051a2ab1178d540a68f3de08a922; __utmb=94650624.9.10.1539324670; JSESSIONID-WYYY=burIXpZYuBKnDC43nTjxAlmMgdQ4fOoP%5COriCxG9rQJjCoMG6yJ6k3DWvRPy2xIEBmGbK70YlFkXqW%2F8yA6Yn%2FhKFKlGqrinCyyD%2BfMacdVJSn8mhgTrEQgrkz7%2BvefkQGrsnRoP88%5CglH1DAgrb3G9M%5Cnx6EDyty0UUNwHQscFNNVOa%3A1539328209169'

        }

    def __get_mp3(self, id):
        d = '{"ids":"[%s]","br":320000,"csrf_token":""}' % id
        wyy = WangYiYun(d)
        data = wyy.get_data()
        print(id)
        url = 'https://music.163.com/weapi/song/enhance/player/url?csrf_token='
        response = requests.post(url, data=data, headers=self.headers).json()
        return response['data']

    # 搜索歌曲type 搜索单曲(1)，歌手(100)，专辑(10)，歌单(1000)，用户(1002)

    def __getsong(self, name, type):
        d = '{"s":"[%s]","type":%d,"offset":0,"total":"true","limit":100}' % (name, type)
        wyy = WangYiYun(d)
        data = wyy.get_data()
        url = 'http://music.163.com/weapi/search/get/'
        response = requests.post(url, data=data, headers=self.headers).json()
        return response

    def __getdetailsong(self, ids):
        url = 'http://music.163.com/api/song/detail/?id=%d&ids=[%d]' % (ids, ids)
        response = requests.get(url, headers=self.headers).json()
        return response

    def __getlyric(self, ids):
        d = '{"os":"osx","id":%d,"lv":-1,"kv":-1,"tv":-1}' % ids
        wyy = WangYiYun(d)
        data = wyy.get_data()
        url = 'http://music.163.com/weapi/song/lyric'
        response = requests.post(url, data=data, headers=self.headers).json()
        return response

    def __album(self, album_id):
        url = 'http://music.163.com/api/album/%s' % album_id
        response = requests.post(url, headers=self.headers).json()
        return response

    def __download_mp3(self, url, filename):
        """下载mp3"""
        
        path = os.path.join(settings.MEDIA_ROOT, 'musicdownload')
        if not os.path.exists(path):  # 如果目录不存在创建目录
            os.makedirs(path)

        path_file = os.path.join(path, filename)
        print(path_file)
        response = requests.get(url, headers=self.headers).content
        with open(path_file + '.mp3', 'wb') as f:
            f.write(response)
        return "下载完毕"

    def __hotrecommend(self):
        url = 'http://music.163.com/api/personalized/playlist'
        response = requests.post(url, headers=self.headers).json()
        return response

    def __newrecommend(self):
        d = '{"offset":0,"limit":20,"total":"true","csrf_token":""}'
        wyy = WangYiYun(d)
        data = wyy.get_data()
        url = 'http://music.163.com/weapi/v1/discovery/recommend/resource'
        response = requests.post(url, data=data, headers=self.headers).json()
        return response

    def __gedandetail(self, id):
        url = 'http://music.163.com/api/playlist/detail?id=%d&updateTime=-1' % id
        response = requests.post(url, headers=self.headers).json()
        return response

    def __otheralbum(self, id):
        d = '{"id":%s,"offset":0,"limit":1,"csrf_token":""}' % id
        wyy = WangYiYun(d)
        data = wyy.get_data()
        url = 'http://music.163.com/weapi/artist/mvs'
        response = requests.post(url, data=data, headers=self.headers).json()
        return response

    def __artistintroduce(self, id):
        d = '{"id":%s,"csrf_token":""}' % id
        wyy = WangYiYun(d)
        data = wyy.get_data()
        url = 'http://music.163.com/weapi/artist/introduction'
        response = requests.post(url, data=data, headers=self.headers).json()
        return response

    def __artistmvs(self, id):
        d = '{"artistId":%s,"total": true,"offset":0,"limit":100,"csrf_token":""}' % id
        wyy = WangYiYun(d)
        data = wyy.get_data()
        url = 'http://music.163.com/weapi/artist/mvs'
        response = requests.post(url, data=data, headers=self.headers).json()
        return response

    def __playmv(self, id):
        url = 'http://music.163.com/api/mv/detail?id=%d&type=mp4' % id
        response = requests.post(url, headers=self.headers).json()
        return response

    def search(self, name, type):
        song = self.__getsong(name, type)
        return song

    def getlyric(self, ids):
        song = self.__getlyric(ids)
        return song

    def getmp3(self, id):
        mp3 = self.__get_mp3(id)
        return mp3

    def getdetailsong(self, ids):
        song = self.__getdetailsong(ids)
        return song

    def getalbumdetail(self, album_id):
        albumdetail = self.__album(album_id)
        return albumdetail

    def download_mp3(self, url, music_name):
        message = self.__download_mp3(url, music_name)
        return message

    def hotrecommend(self):
        recommend = self.__hotrecommend()
        return recommend

    def newrecommend(self):
        recommend = self.__newrecommend()
        return recommend

    def gedandetail(self, id):
        gedandetail = self.__gedandetail(id)
        return gedandetail

    def otheralbum(self, id):
        other = self.__otheralbum(id)
        return other

    def artistmvs(self, id):
        mvs = self.__artistmvs(id)
        return mvs

    def artistintroduce(self, id):
        intr = self.__artistintroduce(id)
        return intr

    def playmv(self, id):
        playmv = self.__playmv(id)
        return playmv


class WangYiYun(object):
    def __init__(self, d):
        self.d = d
        self.e = '010001'
        self.f = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5a" \
                 "a76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46be" \
                 "e255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
        self.g = "0CoJUm6Qyw8W8jud"
        self.random_text = self.get_random_str()

    def get_random_str(self):
        """js中的a函数"""
        str = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        res = ''
        for x in range(16):
            index = math.floor(random.random() * len(str))
            res += str[index]
        return res

    def aes_encrypt(self, text, key):
        iv = '0102030405060708'  # 偏移量
        pad = 16 - len(text.encode()) % 16  # 使加密信息的长度为16的倍数，要不会报下面的错
        # 长度是16的倍数还会报错，不能包含中文，要对他进行unicode编码
        text = text + pad * chr(pad)  # Input strings must be a multiple of 16 in length
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        msg = base64.b64encode(encryptor.encrypt(text))  # 最后还需要使用base64进行加密
        return msg

    def rsa_encrypt(self, value, text, modulus):
        '''进行rsa加密'''
        text = text[::-1]
        rs = int(codecs.encode(text.encode('utf-8'), 'hex_codec'), 16) ** int(value, 16) % int(modulus, 16)
        return format(rs, 'x').zfill(256)

    def get_data(self):
        # 这个参数加密两次
        params = self.aes_encrypt(self.d, self.g)
        params = self.aes_encrypt(params.decode('utf-8'), self.random_text)
        enc_sec_key = self.rsa_encrypt(self.e, self.random_text, self.f)
        return {
            'params': params,
            'encSecKey': enc_sec_key
        }


def getmp3con(id):
    spider = Spider()
    data = spider.getmp3(id)
    return data


def search(name, type):
    spider = Spider()
    data = spider.search(name, type)
    return data


def getdetailsong(ids):
    spider = Spider()
    data = spider.getdetailsong(ids)
    return data


def getlyric(ids):
    spider = Spider()
    data = spider.getlyric(ids)
    return data


def getalbumdetail(album_id):
    spider = Spider()
    data = spider.getalbumdetail(album_id)
    return data


def load_mp3(url, music_name):
    spider = Spider()
    message = spider.download_mp3(url, music_name)
    return message


def hotrecommend():
    spider = Spider()
    data = spider.hotrecommend()
    return data


def newrecommend():
    spider = Spider()
    data = spider.newrecommend()
    return data


def rankinggedandetail(id):
    spider = Spider()
    data = spider.gedandetail(id)
    return data


def otheralbum(id):
    spider = Spider()
    data = spider.otheralbum(id)
    return data


def artistmvs(id):
    spider = Spider()
    data = spider.artistmvs(id)
    return data


def artistintroduce(id):
    spider = Spider()
    data = spider.artistintroduce(id)
    return data


def playmv(id):
    spider = Spider()
    data = spider.playmv(id)
    return data
