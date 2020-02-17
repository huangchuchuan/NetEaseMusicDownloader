# -*- coding: utf-8 -*-
# @Author : Huangcc

import requests
import time
import random
import json
import os
import urllib
import traceback
import codecs
import eyed3


def timestamp_ms_string():
    return '%d' % (time.time() * 1000)


def random_int_string(length):
    start = int('1' + '0' * (length - 1))
    end = int('9' * length)
    return '%d' % random.randint(start, end)


class TiantianJingtiingMusicDownloader:
    default_headers = {
        'Host': '47.112.23.238',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
        'Accept': 'application/json,*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'http://47.112.23.238/',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Origin': 'http://47.112.23.238',
    }

    query_song_data = {
        'number': '20',
        'type': 'netease',  # 按需更改
        'musicName': '幼稚完 林峰',  # 按需更改
    }
    get_lrc_params = {
        'lrc': '513360721',  # 按需更改
        'type': 'netease',  # 按需更改
    }

    source_list = ['netease', 'qq', 'kugou',]  # 下载源

    api_url = 'http://47.112.23.238/Music/getMusicList'
    lrc_api_url = 'http://47.112.23.238/MusicAPI/getLrc/'

    default_download_folder = 'music'
    default_pic_folder = 'pic'

    def __init__(self):
        self.session = requests.Session()
        if not os.path.exists(self.default_download_folder):
            os.mkdir(self.default_download_folder)
        if not os.path.exists(self.default_pic_folder):
            os.mkdir(self.default_pic_folder)

    def get_song_info_from_source(self, search_keyword, source='netease'):
        if source not in self.source_list:
            print 'Unsupported source expected the one of that: %s' % self.source_list
            return False
        query_song_data = self.query_song_data.copy()
        query_song_data['musicName'] = search_keyword
        query_song_data['type'] = source

        resp = self.session.post(url=self.api_url, data=query_song_data, headers=self.default_headers)
        songs = []
        try:
            data = resp.json()
            status, songs = data['status'], data['data']
            if status != 1:
                print "query music error:", resp.content
                return songs
            return songs
        except:
            traceback.print_exc()
            print resp.content
        # 响应示例
        #  {
        #   "status": 1,
        #   "message": "\u83b7\u53d6\u6210\u529f",
        #   "data": [
        #     {
        #       "lrc": "513360721",
        #       "author": "\u623f\u4e1c\u7684\u732b",
        #       "url": "https:\/\/music.163.com\/song\/media\/outer\/url?id=513360721.mp3",
        #       "pic": "http:\/\/p2.music.126.net\/DSTg1dR7yKsyGq4IK3NL8A==\/109951163046050093.jpg?param=320y320",
        #       "title": "\u4e91\u70df\u6210\u96e8",
        #       "type": "netease",
        #       "id": "513360721"
        #     }
        #   ]
        # }
        return songs

    def get_song_download_url(self, search_keyword):
        for source in self.source_list:
            songs = self.get_song_info_from_source(search_keyword, source)
            #  song example:
            #  {
            #     "lrc": "513360721",
            #     "author": "\u623f\u4e1c\u7684\u732b",
            #     "url": "https:\/\/music.163.com\/song\/media\/outer\/url?id=513360721.mp3",
            #     "pic": "http:\/\/p2.music.126.net\/DSTg1dR7yKsyGq4IK3NL8A==\/109951163046050093.jpg?param=320y320",
            #     "title": "\u4e91\u70df\u6210\u96e8",
            #     "type": "netease",
            #     "id": "513360721"
            #   }
            if songs:
                song_id = songs[0]['id']
                song_name = songs[0]['title']
                song_artist = songs[0]['author']
                pic_id = songs[0]['pic']
                lyric_id = songs[0]['lrc']
                album = song_name  # 天天静听没有提供专辑信息，使用歌曲名代替

                download_url = songs[0]['url']
                if download_url:
                    print 'find the download url from source %s' % source
                    return download_url, song_name, song_artist, pic_id, lyric_id, source, album
                else:
                    print 'Can not download from source %s' % source
                    continue  # 无法下载则切换源
            else:
                print 'Can not find any songs from source %s' % source
                continue  # 找不到歌则切换源
        return None

    def download_song_from_url(self, song_url, song_name, song_artist):
        filename = '%s - %s.mp3' % (song_artist, song_name)
        if os.path.exists(os.path.join(self.default_download_folder, filename)):
            print 'already download the song %s of %s successfully' % (song_name, song_artist)
            return True
        try:
            urllib.urlretrieve(url=song_url, filename=os.path.join(self.default_download_folder, filename))
            print 'download the song %s of %s successfully' % (song_name, song_artist)
            return True
        except:
            traceback.print_exc()
            print 'Can not download the song %s of %s from %s' % (song_name, song_artist, song_url)
            return False

    def get_and_download_pic(self, pic_id, song_name, song_artist, source):
        filename = '%s - %s.jpg' % (song_artist, song_name)
        if os.path.exists(os.path.join(self.default_pic_folder, filename)):
            print 'already download cover pic %s successfully' % filename
            return True
        try:
            urllib.urlretrieve(url=pic_id, filename=os.path.join(self.default_pic_folder, filename))
            print 'download cover pic %s successfully' % filename
            return True
        except:
            traceback.print_exc()
            print 'Can not download cover pic %s' % filename
            return False

    def get_and_download_lyric(self, lyric_id, song_name, song_artist, source):
        filename = '%s - %s.lrc' % (song_artist, song_name)
        if os.path.exists(os.path.join(self.default_download_folder, filename)):
            print 'already download the lyric %s successfully' % filename
            return True
        # 修改必要参数
        lrc_params = self.get_lrc_params.copy()
        lrc_params["lrc"] = lyric_id
        lrc_params["type"] = source
        # 获取下载信息
        resp = self.session.get(url=self.lrc_api_url, params=lrc_params, headers=self.default_headers)
        with codecs.open(os.path.join(self.default_download_folder, filename), 'wb', 'utf-8') as f:
            f.write(resp.text)
            print 'download the lyric %s successfully' % filename
            return True

    def write_pic_to_song(self, song_name, song_artist, album):
        song_filename = os.path.join(self.default_download_folder, '%s - %s.mp3' % (song_artist, song_name))
        pic_filename = os.path.join(self.default_pic_folder, '%s - %s.jpg' % (song_artist, song_name))

        try:
            audiofile = eyed3.load(song_filename)
            if not audiofile:
                return
            if not audiofile.tag:
                audiofile.initTag()
            audiofile.tag.images.set(3, open(pic_filename, 'rb').read(), 'image/jpeg')
            audiofile.tag.artist = song_artist if not audiofile.tag.artist else audiofile.tag.artist
            audiofile.tag.title = song_name if not audiofile.tag.title else audiofile.tag.title
            audiofile.tag.album = album if not audiofile.tag.album else audiofile.tag.album
            audiofile.tag.save()
        except:
            traceback.print_exc()
            print song_name, song_artist, album, repr(song_name), repr(song_artist), repr(album)

    def set_default_download_folder(self, path):
        self.default_download_folder = path

    def set_default_pic_folder(self, path):
        self.default_pic_folder = path

    def search_and_download_song(self, keyword, download_dir=None, pic_dir=None):
        if download_dir:
            self.set_default_download_folder(download_dir)
        if pic_dir:
            self.set_default_pic_folder(pic_dir)

        try:
            download_url, song_name, song_artist, pic_id, lyric_id, source, album = self.get_song_download_url(keyword)
            if self.download_song_from_url(download_url, song_name, song_artist):
                self.get_and_download_lyric(lyric_id=lyric_id, song_name=song_name, song_artist=song_artist, source=source)
                if self.get_and_download_pic(pic_id=pic_id, song_name=song_name, song_artist=song_artist, source=source):
                    self.write_pic_to_song(song_name, song_artist, album)
        except Exception:
            traceback.print_exc()
            print "download fail", keyword


if __name__ == '__main__':
    api = TiantianJingtiingMusicDownloader()
    download_url, song_name, song_artist, pic_id, lyric_id, source, album = api.get_song_download_url('沙漠骆驼 展展与罗罗')
    if api.download_song_from_url(download_url, song_name, song_artist):
        api.get_and_download_lyric(lyric_id=lyric_id, song_name=song_name, song_artist=song_artist, source=source)
        if api.get_and_download_pic(pic_id=pic_id, song_name=song_name, song_artist=song_artist, source=source):
            api.write_pic_to_song(song_name, song_artist, album)
