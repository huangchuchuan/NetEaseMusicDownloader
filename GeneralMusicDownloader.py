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


class GeneralMusicDownloader:
    default_headers = {
        'Host': '122.112.253.137',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'http://lab.mkblog.cn/music/',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }

    query_song_data = {
        'callback': 'jQuery111308194906156652133_1511145723854',
        'types': 'search',
        'count': '20',
        'source': 'netease',  # 按需更改
        'pages': '1',
        'name': '幼稚完 林峰',  # 按需更改
        '_': '1511145723857',
    }

    general_query_data = {
        'callback': 'jQuery111308194906156652132_1511145723853',
        'types': 'url',  # 按需修改
        'id': '25638257',
        'source': 'netease',  # 按需修改
        '_': '1511145723868',
    }

    source_list = ['netease', 'tencent', 'xiami', 'kugou', 'baidu']  # 下载源

    api_url = 'http://122.112.253.137/music/api.php'

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
        callback_item = 'jQuery%s_%s' % (random_int_string(21), timestamp_ms_string())
        query_song_data['callback'] = callback_item
        query_song_data['_'] = timestamp_ms_string()
        query_song_data['name'] = search_keyword
        query_song_data['source'] = source

        resp = self.session.get(url=self.api_url, params=query_song_data, headers=self.default_headers)
        songs = []
        try:
            songs = json.loads(resp.content[len(callback_item) + 1: -1])
        except:
            traceback.print_exc()
            print resp.content
        # 响应示例
        #  [
        # 	"id": "001ZptHS0QElqW",
        # 	"name": "\u5e7c\u7a1a\u5b8c",
        # 	"artist": ["\u6797\u5cef"],
        # 	"album": "A Time 4 You \u65b0\u66f2+\u7cbe\u9009",
        # 	"pic_id": "003lA98A4Jbn9I",
        #	"url_id": "001ZptHS0QElqW",
        #	"lyric_id": "001ZptHS0QElqW",
        #	"source": "tencent",
        # }]
        return songs

    def get_song_download_info_from_source(self, song_id, source):
        # 修改必要参数
        general_query_data = self.general_query_data.copy()
        callback_item = 'jQuery%s_%s' % (random_int_string(21), timestamp_ms_string())
        general_query_data['callback'] = callback_item
        general_query_data['_'] = timestamp_ms_string()
        general_query_data['id'] = song_id
        general_query_data['source'] = source
        general_query_data['types'] = 'url'
        # 获取下载信息
        resp = self.session.get(url=self.api_url, params=general_query_data, headers=self.default_headers)
        json_data = json.loads(resp.content[len(callback_item) + 1: -1])
        # 响应示例
        # {"url":"","br":-1}
        # {"url":"https:\/\/dl.stream.qqmusic.qq.com\/M800001ZptHS0QElqW.mp3?vkey=483BB7027FD2626BFAE54FFD77A7C31F58F44BAB9F5E2A1DBFA9EAA58C2A39D1627A7D4F2C3E8478D690B085BF43BE47B99BF0DECA512B29&guid=513525444&uid=0&fromtag=30","br":320}
        return json_data

    def get_song_download_url(self, search_keyword):
        for source in self.source_list:
            songs = self.get_song_info_from_source(search_keyword, source)
            if songs:
                song_id = songs[0]['id']
                song_name = songs[0]['name']
                song_artist = songs[0]['artist'][0]  # 取第一位艺术家
                pic_id = songs[0]['pic_id']
                lyric_id = songs[0]['lyric_id']
                album = songs[0]['album']

                download_url = self.get_song_download_info_from_source(song_id=song_id, source=source)['url']
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
        # 修改必要参数
        general_query_data = self.general_query_data.copy()
        callback_item = 'jQuery%s_%s' % (random_int_string(21), timestamp_ms_string())
        general_query_data['callback'] = callback_item
        general_query_data['_'] = timestamp_ms_string()
        general_query_data['id'] = pic_id
        general_query_data['source'] = source
        general_query_data['types'] = 'pic'
        # 获取下载信息
        resp = self.session.get(url=self.api_url, params=general_query_data, headers=self.default_headers)
        json_data = json.loads(resp.content[len(callback_item) + 1: -1])
        if json_data['url']:
            urllib.urlretrieve(url=json_data['url'], filename=os.path.join(self.default_pic_folder, filename))
            print 'download cover pic %s successfully' % filename
            return True
        else:
            print 'Can not download cover pic %s' % filename
            return False

    def get_and_download_lyric(self, lyric_id, song_name, song_artist, source):
        filename = '%s - %s.lrc' % (song_artist, song_name)
        if os.path.exists(os.path.join(self.default_download_folder, filename)):
            print 'already download the lyric %s successfully' % filename
            return True
        # 修改必要参数
        general_query_data = self.general_query_data.copy()
        callback_item = 'jQuery%s_%s' % (random_int_string(21), timestamp_ms_string())
        general_query_data['callback'] = callback_item
        general_query_data['_'] = timestamp_ms_string()
        general_query_data['id'] = lyric_id
        general_query_data['source'] = source
        general_query_data['types'] = 'lyric'
        # 获取下载信息
        resp = self.session.get(url=self.api_url, params=general_query_data, headers=self.default_headers)
        json_data = json.loads(resp.content[len(callback_item) + 1: -1])
        if json_data['lyric']:
            with codecs.open(os.path.join(self.default_download_folder, filename), 'wb', 'utf-8') as f:
                f.write(json_data['lyric'])
            print 'download the lyric %s successfully' % filename
            return True
        else:
            print 'Can not download the lyric %s' % filename
            return False

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
        download_url, song_name, song_artist, pic_id, lyric_id, source, album = self.get_song_download_url(keyword)
        if self.download_song_from_url(download_url, song_name, song_artist):
            self.get_and_download_lyric(lyric_id=lyric_id, song_name=song_name, song_artist=song_artist, source=source)
            if self.get_and_download_pic(pic_id=pic_id, song_name=song_name, song_artist=song_artist, source=source):
                self.write_pic_to_song(song_name, song_artist, album)


if __name__ == '__main__':
    api = GeneralMusicDownloader()
    download_url, song_name, song_artist, pic_id, lyric_id, source, album = api.get_song_download_url('幼稚完 林峰')
    if api.download_song_from_url(download_url, song_name, song_artist):
        api.get_and_download_lyric(lyric_id=lyric_id, song_name=song_name, song_artist=song_artist, source=source)
        if api.get_and_download_pic(pic_id=pic_id, song_name=song_name, song_artist=song_artist, source=source):
            api.write_pic_to_song(song_name, song_artist, album)
