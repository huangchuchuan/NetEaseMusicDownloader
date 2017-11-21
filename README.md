# 网易云音乐同步下载

## 文件功能描述
### GeneralMusicDownloader
使用第三方下载api [MkOnlinePlayer](http://lab.mkblog.cn/music/)

支持`网易`, `QQ`, `虾米`, `酷狗`, `百度`搜索和下载

支持歌词自动下载和封面添加到mp3文件的功能

### NetEaseApi
提供网易云音乐登录/获取每日推荐/歌单信息的api

### NetEaseMusicSync
调用`NetEaseApi`和`GeneralMusicDownloader`实现登录/获取歌单/下载歌单到本地文件夹的功能

## Api接口说明
更详细的接口信息请看对应的`.py`文件

### 网易云音乐统一api请求方式
使用同一种加密方式和请求体格式，响应均为`json`格式
#### 请求方式
`POST`
#### 请求加密方式
```python
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
```

### NetEaseApi::cellphone_login
#### 请求url
```
http://music.163.com/weapi/login/cellphone?csrf_token=
```
#### 请求参数
```
{
    'phone': username,
    'password': hashlib.md5(password).hexdigest(),
    'rememberLogin': "true"
}
```
#### 响应示例
```python
{
	u'profile': {
		u'followed': False,
		u'remarkName': None,
		u'expertTags': None,
		u'userId': xxxxxx,
		u'authority': 0,
		u'userType': 0,
		u'experts': {

		},
		u'backgroundImgId': xxxxxx,
		u'city': xxxxxx,
		u'mutual': False,
		u'avatarUrl': xxxxxx,
		u'detailDescription': u'',
		u'avatarImgIdStr': u'xxxxxx',
		u'province': xxxxxx,
		u'description': u'',
		u'signature': u'',
		u'birthday': -xxxxxx,
		u'nickname': u'xxxxxx',
		u'vipType': 0,
		u'avatarImgId': xxxxxx,
		u'gender': 1,
		u'djStatus': 0,
		u'accountStatus': 0,
		u'backgroundImgIdStr': u'xxxxxx',
		u'backgroundUrl': u'xxxxxx',
		u'defaultAvatar': False,
		u'authStatus': 0
	},
	u'account': {
		u'userName': u'xxxxxx',
		u'status': 0,
		u'anonimousUser': False,
		u'whitelistAuthority': 0,
		u'baoyueVersion': 0,
		u'salt': u'[B@xxxxxx',
		u'createTime': 0,
		u'tokenVersion': 0,
		u'vipType': 0,
		u'ban': 0,
		u'viptypeVersion': 0,
		u'type': 1,
		u'id': xxxxxx,
		u'donateVersion': 0
	},
	u'code': 200,
	u'bindings': [{
		u'expiresIn': xxxxxx,
		u'tokenJsonStr': u'{
			"countrycode": "",
			"cellphone": "xxxxxx",
			"hasPassword": true
		}',
		u'url': u'',
		u'expired': False,
		u'userId': xxxxxx,
		u'refreshTime': xxxxxx,
		u'type': 1,
		u'id': xxxxxx
	},]
	......
}
```

### NetEaseApi::get_play_list
根据uid获取列表信息
#### 请求url
```
http://music.163.com/weapi/user/playlist?csrf_token=
```
#### 请求参数
```python
params = {
            'offset': '0',
            'limit': '9999',
            'uid': str(uid)
        }
```
#### 响应示例
```python
{
	u'playlist': [{
		u'updateTime': xxxxxx,
		u'ordered': False,
		u'anonimous': False,
		u'creator': {
			......
		},
		u'trackUpdateTime': xxxxxx,
		u'userId': xxxxxx,
		u'coverImgUrl': xxxxxx,
		u'artists': None,
		u'newImported': False,
		u'commentThreadId': u'xxxxxx',
		u'subscribed': False,
		u'privacy': 0,
		u'id': xxxxxx,
		u'trackCount': 1138,
		u'specialType': 5,
		u'status': 0,
		u'description': None,
		u'subscribedCount': 0,
		u'tags': [],
		u'trackNumberUpdateTime': xxxxxx,
		u'tracks': None,
		u'highQuality': False,
		u'subscribers': [],
		u'playCount': 112,
		u'coverImgId': xxxxxx,
		u'createTime': xxxxxx,
		u'name': u'xxxxxx',
		u'cloudTrackCount': 0,
		u'adType': 0,
		u'totalDuration': 0
	},]
}
```

### NetEaseApi::get_play_list_info
根据列表id来获取歌名列表
#### 请求url
```
url = 'http://music.163.com/weapi/playlist/detail?csrf_token='
```
#### 请求参数
```python
params = {'id': str(music_list_id)}
```
#### 响应示例
```python
{
	u'code': 200,
	u'result': {
		u'updateTime': xxxxx,
		u'ordered': False,
		u'anonimous': False,
		u'creator': {
			u'followed': False,
			u'remarkName': None,
			u'expertTags': None,
			u'userId': xxxx,
			u'authority': 0,
			u'userType': 0,
			u'experts': None,
			u'gender': 1,
			u'backgroundImgId': xxxxx,
			u'city': xxxxx,
			u'mutual': False,
			u'avatarUrl': u'xxxxx',
			u'avatarImgIdStr': u'xxxxx',
			u'detailDescription': u'',
			u'province': xxxx,
			u'description': u'',
			u'birthday': -xxxx,
			u'nickname': u'xxxx',
			u'vipType': 0,
			u'avatarImgId': xxxx,
			u'defaultAvatar': False,
			u'djStatus': 0,
			u'accountStatus': 0,
			u'backgroundImgIdStr': u'xxxxx',
			u'backgroundUrl': u'xxxx',
			u'signature': u'',
			u'authStatus': 0
		},
		u'trackUpdateTime': xxxxx,
		u'userId': xxxxx,
		u'coverImgUrl': u'xxxxx',
		u'commentCount': 0,
		u'artists': None,
		u'newImported': False,
		u'commentThreadId': u'xxxxx',
		u'subscribed': False,
		u'privacy': 0,
		u'id': xxxxxx,
		u'trackCount': 20,
		u'specialType': 0,
		u'status': 0,
		u'description': None,
		u'subscribedCount': 0,
		u'tags': [],
		u'coverImgId': xxxxxx,
		u'tracks': [{
			u'bMusic': {
				u'name': u'\u8fd9\u6837\u7231\u4e86',
				u'extension': u'mp3',
				u'volumeDelta': -1.48,
				u'sr': 44100,
				u'dfsId': 0,
				u'playTime': 263105,
				u'bitrate': 96000,
				u'id': 29417131,
				u'size': 3194123
			},
			u'hearTime': 0,
			u'mvid': 1115,
			u'hMusic': {
				u'name': u'\u8fd9\u6837\u7231\u4e86',
				u'extension': u'mp3',
				u'volumeDelta': -1.84,
				u'sr': 44100,
				u'dfsId': 0,
				u'playTime': 263105,
				u'bitrate': 320000,
				u'id': 29417129,
				u'size': 10562534
			},
			u'disc': u'1',
			u'artists': [{
				u'img1v1Url': u'http: //p1.music.126.net/6y-UleORITEDbvrOLV0Q8A==/5639395138885805.jpg',
				u'name': u'\u5f20\u5a67',
				u'briefDesc': u'',
				u'albumSize': 0,
				u'img1v1Id': 0,
				u'musicSize': 0,
				u'alias': [],
				u'picId': 0,
				u'picUrl': u'http: //p1.music.126.net/6y-UleORITEDbvrOLV0Q8A==/5639395138885805.jpg',
				u'trans': u'',
				u'id': 10753
			}],
			u'duration': 263105,
			u'id': 391564,
			u'album': {
				u'pic': 72567767449563L,
				u'subType': u'\u5f55\u97f3\u5ba4\u7248',
				u'artists': [{
					u'img1v1Url': u'http: //p1.music.126.net/6y-UleORITEDbvrOLV0Q8A==/5639395138885805.jpg',
					u'name': u'\u7fa4\u661f',
					u'briefDesc': u'',
					u'albumSize': 0,
					u'img1v1Id': 0,
					u'musicSize': 0,
					u'alias': [],
					u'picId': 0,
					u'picUrl': u'http: //p1.music.126.net/6y-UleORITEDbvrOLV0Q8A==/5639395138885805.jpg',
					u'trans': u'',
					u'id': 122455
				}],
				u'id': 38789,
				u'size': 10,
				u'commentThreadId': u'R_AL_3_38789',
				u'companyId': 0,
				u'briefDesc': u'',
				u'type': u'\u4e13\u8f91',
				u'status': 1,
				u'description': u'',
				u'tags': u'',
				u'company': u'\u6d77\u8776\u97f3\u4e50',
				u'picId': 72567767449563L,
				u'picUrl': u'http: //p1.music.126.net/Rk334sCFsT_HeO3ZJ-IfeA==/72567767449563.jpg',
				u'blurPicUrl': u'http: //p1.music.126.net/Rk334sCFsT_HeO3ZJ-IfeA==/72567767449563.jpg',
				u'copyrightId': 14026,
				u'name': u'\u8f69\u8f95\u5251\u7535\u89c6\u539f\u58f0\u5927\u789f',
				u'artist': {
					u'img1v1Url': u'http: //p1.music.126.net/6y-UleORITEDbvrOLV0Q8A==/5639395138885805.jpg',
					u'name': u'',
					u'briefDesc': u'',
					u'albumSize': 0,
					u'img1v1Id': 0,
					u'musicSize': 0,
					u'alias': [],
					u'picId': 0,
					u'picUrl': u'http: //p1.music.126.net/6y-UleORITEDbvrOLV0Q8A==/5639395138885805.jpg',
					u'trans': u'',
					u'id': 0
				},
				u'publishTime': 1342368000000L,
				u'alias': [],
				u'songs': []
			},
			u'fee': 0,
			u'copyright': 1,
			u'no': 1,
			u'rtUrl': None,
			u'ringtone': u'600902000009339522',
			u'rtUrls': [],
			u'score': 100,
			u'rurl': None,
			u'status': 0,
			u'ftype': 0,
			u'mp3Url': None,
			u'audition': None,
			u'playedNum': 0,
			u'commentThreadId': u'R_SO_4_391564',
			u'mMusic': {
				u'name': u'\u8fd9\u6837\u7231\u4e86',
				u'extension': u'mp3',
				u'volumeDelta': -1.44,
				u'sr': 44100,
				u'dfsId': 0,
				u'playTime': 263105,
				u'bitrate': 160000,
				u'id': 29417130,
				u'size': 5299384
			},
			u'lMusic': {
				u'name': u'\u8fd9\u6837\u7231\u4e86',
				u'extension': u'mp3',
				u'volumeDelta': -1.48,
				u'sr': 44100,
				u'dfsId': 0,
				u'playTime': 263105,
				u'bitrate': 96000,
				u'id': 29417131,
				u'size': 3194123
			},
			u'copyrightId': 14026,
			u'name': u'\u8fd9\u6837\u7231\u4e86',
			u'rtype': 0,
			u'crbt': u'0a25e5667006a3b49b79ec8e7ffaf8f2',
			u'popularity': 100.0,
			u'dayPlays': 0,
			u'alias': [u'\u7535\u89c6\u5267\u300a\u8f69\u8f95\u5251\u4e4b\u5929\u4e4b\u75d5\u300b\u7247\u5c3e\u66f2'],
			u'copyFrom': u'',
			u'position': 1,
			u'starred': False,
			u'starredNum': 0
		},
		],
		u'highQuality': False,
		u'subscribers': [],
		u'playCount': 0,
		u'trackNumberUpdateTime': xxxxx,
		u'createTime': xxxxx,
		u'name': u'\u4e0b\u8f7d',
		u'cloudTrackCount': 0,
		u'shareCount': 0,
		u'adType': 0,
		u'totalDuration': 0
	}
}
```

### MKOnlinePlayer 音乐接口
使用同一个api接口和请求方式，响应均为`JSONP`格式
#### 请求url
```
api_url = 'http://122.112.253.137/music/api.php'
```
#### 请求方式
`GET`

### GeneralMusicDownloader::get_song_info_from_source
根据关键词获取歌曲信息
#### 请求参数
```python
query_song_data = {
        'callback': 'jQuery111308194906156652133_1511145723854',
        'types': 'search',
        'count': '20',
        'source': 'netease',  # 按需更改
        'pages': '1',
        'name': '幼稚完 林峰',  # 按需更改
        '_': '1511145723857',
    }
```
#### 响应示例
```python
jQuery111307832949596001351_1511159299186([{
	"id": "001ZptHS0QElqW",
	"name": "\u5e7c\u7a1a\u5b8c",
	"artist": ["\u6797\u5cef"],
	"album": "A Time 4 You \u65b0\u66f2+\u7cbe\u9009",
	"pic_id": "003lA98A4Jbn9I",
	"url_id": "001ZptHS0QElqW",
	"lyric_id": "001ZptHS0QElqW",
	"source": "tencent"
}...
])
```

### GeneralMusicDownloader::get_song_download_info_from_source
根据`url_id`获取下载`url`
#### 请求参数
```python
general_query_data = {
        'callback': 'jQuery111308194906156652132_1511145723853',
        'types': 'url',  # 按需修改
        'id': '25638257',  # url_id
        'source': 'netease',  # 按需修改
        '_': '1511145723868',
 }
```
#### 响应示例
```python
{"url":"https:\/\/dl.stream.qqmusic.qq.com\/M800001ZptHS0QElqW.mp3?vkey=483BB7027FD2626BFAE54FFD77A7C31F58F44BAB9F5E2A1DBFA9EAA58C2A39D1627A7D4F2C3E8478D690B085BF43BE47B99BF0DECA512B29&guid=513525444&uid=0&fromtag=30","br":320}
```

