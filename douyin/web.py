from flask import Flask
import requests
import json
from urllib.parse import urlencode
from spider_config import *

search_url = 'https://aweme.snssdk.com/aweme/v1/discover/search/?'


app = Flask(__name__)


def _read_gorgon(user_id):
    res = requests.get(f'http://106.14.140.61:9091/get?keyword={user_id}').json()
    timestamp = res.get('timestamp', '')
    time = res.get('time', '')
    gorgon = res.get('gorgon', '')
    return gorgon, time, timestamp


def get_sec_result(user_id):
    search_body['keyword'] = user_id
    gorgon, time, timestamp = _read_gorgon(user_id)
    search_param['ts'] = str(time)
    search_param['_rticket'] = str(timestamp)
    head['X-Gorgon'] = gorgon
    head['X-Khronos'] = str(time)
    sug_url = search_url + urlencode(search_param, safe='%').replace('%2A', "*")
    dict_ret = requests.post(sug_url, headers=head, data=search_body)
    return dict_ret.json()


def _get_signature():
    res = requests.get('http://106.14.140.61:7878/')
    return res.text


def get_user_video_info(sec_user_id, max_cursor):
    video_url = 'https://www.iesdouyin.com/web/api/v2/aweme/post/?'
    videos = []
    has_more = False
    if sec_user_id is None:
        return max_cursor, has_more, videos
    video_param['sec_uid'] = sec_user_id
    video_param['_signature'] = _get_signature()
    video_param['max_cursor'] = max_cursor
    room_url = video_url + urlencode(video_param)
    print(room_url)
    res = requests.get(room_url, headers={
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
    })
    return res.json()

@app.route('/user/<string:key>/')
def get_user(key):
    return get_sec_result(key)

@app.route('/video/<string:sec_uid>')
def get_video(sec_uid):
    return get_user_video_info(sec_uid, 0)

if __name__ == '__main__':
    app.run(port=5051)