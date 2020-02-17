# -*- coding: utf-8 -*-
# @Author : Huangcc

import os
import re
import datetime
import traceback
from NetEaseApi import NetEaseApi
from TiantianJingtingMusicDownloader import TiantianJingtiingMusicDownloader


def to_win_safe(s):
    return re.sub('[\/:*?"<>|]', '-', s)


class NetEaseMusicSync:
    def __init__(self, cellphone, password):
        self.cellphone = cellphone
        self.password = password
        self.netease_api = NetEaseApi()
        self.downloader = TiantianJingtiingMusicDownloader()

    def login(self):
        user_data = self.netease_api.cellphone_login(self.cellphone, self.password)
        if user_data["code"] != 200:
            raise ValueError("login fail! phone: %s, password: %s, response: %s" %
                             (self.cellphone, self.password, user_data))
        return user_data['account']['id']

    def sync_song_lists(self, uid):
        play_list = self.netease_api.get_play_list(uid)
        for music_list in play_list['playlist']:
            list_name = music_list['name']
            # 去除特殊字符
            list_name = to_win_safe(list_name)

            music_dir = os.path.join('music', list_name)
            if not os.path.exists(music_dir):
                os.mkdir(music_dir)

            music_list_info = self.netease_api.get_play_list_info(music_list['id'])
            if music_list_info['code'] == 200:
                music_name_artist = []
                exist_filename_list = os.listdir(music_dir)
                # 获取歌单中的音乐名字和演唱者
                for music in music_list_info['result']['tracks']:
                    music_name_artist.append((to_win_safe(music['name']), to_win_safe(music['artists'][0]['name']) if music['artists'] else ""))
                # 过滤已下载的音乐
                music_name_artist = filter(lambda x: ('%s - %s.mp3' % (x[1], x[0])) not in exist_filename_list,
                                           music_name_artist)
                # 搜索下载对应的音乐
                num_of_music = len(music_name_artist)
                curr = 1
                for name, artist in music_name_artist:
                    try:
                        print '-*- %d/%d downloading the song %s from list %s -*-' % (curr, num_of_music, name, list_name)
                        self.downloader.search_and_download_song('%s %s' % (name, artist), music_dir, None)
                    except Exception:
                        traceback.print_exc()
                    curr += 1

    def sync_daily_recommend(self):
        current_date = (datetime.datetime.now() - datetime.timedelta(hours=6)).strftime('%Y%m%d')  # 每天6点更新
        daily_dir = os.path.join('music', current_date)
        if not os.path.exists(daily_dir):
            os.mkdir(daily_dir)

        daily_data = self.netease_api.get_daily_recommend()
        if daily_data['code'] == 200:
            music_list = daily_data['recommend']
            music_name_artist = []
            exist_filename_list = os.listdir(daily_dir)
            # 获取歌单中的音乐名字和演唱者
            for music in music_list:
                music_name_artist.append((music['name'], music['artists'][0]['name'] if music['artists'] else ""))
            # 过滤已下载的音乐
            music_name_artist = filter(lambda x: ('%s - %s.mp3' % (x[1], x[0])) not in exist_filename_list,
                                       music_name_artist)
            # 搜索下载对应的音乐
            num_of_music = len(music_name_artist)
            curr = 1
            for name, artist in music_name_artist:
                print '-*- %d/%d downloading the song %s from list %s -*-' % (curr, num_of_music, name, current_date)
                self.downloader.search_and_download_song('%s %s' % (name, artist), daily_dir, None)
                curr += 1
        else:
            print 'Can not get daily recommend of %s' % current_date


if __name__ == '__main__':
    my_netease = NetEaseMusicSync('your_phone_number', 'your_password')
    uid = my_netease.login()
    my_netease.sync_song_lists(uid)  # 同步歌单
    my_netease.sync_daily_recommend()  # 同步每日推荐
