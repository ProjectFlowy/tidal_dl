#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   tidal.py
@Time    :   2019/02/27
@Author  :   Yaronzz
@VERSION :   2.0
@Contact :   yaronhuang@foxmail.com
@Desc    :   tidal api
'''
import base64
import hashlib
import json
import logging
import re
import secrets
from subprocess import PIPE, Popen
import time
from urllib.parse import parse_qs, urlparse
from uuid import uuid4
import xml.etree.ElementTree as ET

import aigpy.stringHelper as stringHelper
import requests
from aigpy.modelHelper import dictToModel
from aigpy.stringHelper import isNull
from requests.packages import urllib3
from tidal_dl.enums import Type, AudioQuality, VideoQuality
from tidal_dl.model import Album, Track, Video, Artist, Playlist, StreamUrl, VideoStreamUrl, SearchResult, Lyrics, Mix, SegmentStreamUrl
import tidal_dl.apiKey as apiKey
from tidal_dl.printf import Printf

__VERSION__ = '1.9.1'
__URL_PRE__ = 'https://api.tidalhifi.com/v1/'
__AUTH_URL__ = 'https://auth.tidal.com/v1/oauth2'
__API_KEY__ = {'clientId': '7m7Ap0JC9j1cOM3n',
               'clientSecret': 'vRAdA108tlvkJpTsGZS8rGZ7xTlbJ0qaZ2K9saEzsgY='}

# SSL Warnings
urllib3.disable_warnings()
# add retry number
requests.adapters.DEFAULT_RETRIES = 5


class ReCaptcha(object):
    def __init__(self):
        self.captcha_path = 'captcha/'

        self.response_v3 = None
        self.response_v2 = None

        self.get_response()

    @staticmethod
    def check_npm():
        pipe = Popen('npm -version', shell=True, stdout=PIPE).stdout
        output = pipe.read().decode('UTF-8')
        found = re.search(r'[0-9].[0-9]+.', output)
        if not found:
            print("NPM could not be found.")
            return False
        return True

    def get_response(self):
        if self.check_npm():
            print("Opening reCAPTCHA check...")
            command = 'npm start --prefix '
            pipe = Popen(command + self.captcha_path, shell=True, stdout=PIPE)
            pipe.wait()
            output = pipe.stdout.read().decode('UTF-8')
            pattern = re.compile(r"(?<='response': ')[0-9A-Za-z-_]+")
            response = pattern.findall(output)
            if len(response) > 2:
                print('You only need to complete the captcha once.')
                return False
            elif len(response) == 1:
                self.response_v3 = response[0]
                return True
            elif len(response) == 2:
                self.response_v3 = response[0]
                self.response_v2 = response[1]
                return True

            print('Please complete the reCAPTCHA check.')
            return False


class LoginKey(object):
    def __init__(self):
        self.deviceCode = None
        self.userCode = None
        self.verificationUrl = None
        self.authCheckTimeout = None
        self.authCheckInterval = None
        self.userId = None
        self.countryCode = None
        self.accessToken = None
        self.refreshToken = None
        self.expiresIn = None


class __StreamRespond__(object):
    trackid = None
    videoid = None
    licenseSecurityToken = None
    streamType = None
    assetPresentation = None
    audioMode = None
    audioQuality = None
    videoQuality = None
    manifestMimeType = None
    manifest = None


class TidalAPI(object):
    def __init__(self):
        self.apiKey = __API_KEY__
        self.key = LoginKey()
        self.__debugVar = 0

    def __toJson__(self, string: str):
        try:
            json_object = json.loads(string)
        except:
            return None
        return json_object

    def __get__(self, path, params={}, retry=3, urlpre=__URL_PRE__):
        # deprecate the sessionId
        # header = {'X-Tidal-SessionId': self.key.sessionId}T
        header = {}
        if not isNull(self.key.accessToken):
            header = {'authorization': 'Bearer {}'.format(self.key.accessToken)}
        params['countryCode'] = self.key.countryCode

        result = None
        respond = None
        for index in range(0, retry):
            try:
                respond = requests.get(urlpre + path, headers=header, params=params, verify=False)
                result = self.__toJson__(respond.text)
                break
            except:
                continue

        if result is None:
            return "Get operation err!" + respond.text, None
        if 'status' in result:
            if 'userMessage' in result and result['userMessage'] is not None:
                return result['userMessage'], None
            else:
                logging.error("[Get operation err] path=" + path + ". respon=" + respond.text)
                return "Get operation err!", None
        return None, result

    def __getItems__(self, path, params={}, retry=3):
        params['limit'] = 50
        params['offset'] = 0
        total = 0
        ret = []
        while True:
            msg, data = self.__get__(path, params, retry)
            if msg is not None:
                return msg, None
            
            if 'totalNumberOfItems'in data:
                total = data['totalNumberOfItems']
            if total > 0 and total <= len(ret):
                return None, ret
            
            num = 0
            for item in data["items"]:
                num += 1
                ret.append(item)
            if num < 50:
                break
            params['offset'] += num
        return None, ret

    def __getQualityString__(self, quality: AudioQuality):
        if quality == AudioQuality.Normal:
            return "LOW"
        if quality == AudioQuality.High:
            return "HIGH"
        if quality == AudioQuality.HiFi:
            return "LOSSLESS"
        if quality == AudioQuality.HiRes:
            return "HI_RES_LOSSLESS"
        return "HI_RES"

    def __getResolutionList__(self, url):
        ret = []
        txt = requests.get(url).text
        # array = txt.split("#EXT-X-STREAM-INF")
        array = txt.split("#")
        for item in array:
            if "RESOLUTION=" not in item:
                continue
            if "EXT-X-STREAM-INF:" not in item:
                continue
            stream = VideoStreamUrl()
            stream.codec = stringHelper.getSub(item, "CODECS=\"", "\"")
            stream.m3u8Url = "http" + stringHelper.getSubOnlyStart(item, "http").strip()
            stream.resolution = stringHelper.getSub(item, "RESOLUTION=", "http").strip()
            stream.resolution = stream.resolution.split(',')[0]
            stream.resolutions = stream.resolution.split("x")
            ret.append(stream)
        return ret

    def __post__(self, url, data, auth=None):
        retry = 3
        while retry > 0:
            try:
                result = requests.post(url, data=data, auth=auth, verify=False).json()
            except (
                    requests.ConnectionError,
                    requests.exceptions.ReadTimeout,
                    requests.exceptions.Timeout,
                    requests.exceptions.ConnectTimeout,
            ) as e:
                retry -= 1
                if retry <= 0:
                    return e, None
                continue
            return None, result

    def getDeviceCode(self):
        data = {
            'client_id': self.apiKey['clientId'],
            'scope': 'r_usr+w_usr+w_sub'
        }
        e, result = self.__post__(__AUTH_URL__ + '/device_authorization', data)
        if e is not None:
            return str(e), False

        if 'status' in result and result['status'] != 200:
            return "Device authorization failed. Please try again.", False

        self.key.deviceCode = result['deviceCode']
        self.key.userCode = result['userCode']
        self.key.verificationUrl = result['verificationUri']
        self.key.authCheckTimeout = result['expiresIn']
        self.key.authCheckInterval = result['interval']
        return None, True

    def checkAuthStatus(self):
        data = {
            'client_id': self.apiKey['clientId'],
            'device_code': self.key.deviceCode,
            'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
            'scope': 'r_usr+w_usr+w_sub'
        }
        e, result = self.__post__(__AUTH_URL__ + '/token', data, (self.apiKey['clientId'], self.apiKey['clientSecret']))
        if e is not None:
            return str(e), False

        if 'status' in result and result['status'] != 200:
            if result['status'] == 400 and result['sub_status'] == 1002:
                return "pending", False
            else:
                return "Error while checking for authorization. Trying again...", False

        # if auth is successful:
        self.key.userId = result['user']['userId']
        self.key.countryCode = result['user']['countryCode']
        self.key.accessToken = result['access_token']
        self.key.refreshToken = result['refresh_token']
        self.key.expiresIn = result['expires_in']
        return None, True

    def verifyAccessToken(self, accessToken):
        header = {'authorization': 'Bearer {}'.format(accessToken)}
        result = requests.get('https://api.tidal.com/v1/sessions', headers=header, verify=False).json()
        if 'status' in result and result['status'] != 200:
            return "Login failed!", False
        return None, True

    def refreshAccessToken(self, refreshToken):
        if self.apiKey["platform"] in ["macOS", "iOS", "Android"]:
            data = {
                'client_id': self.apiKey['clientId'],
                'refresh_token': refreshToken,
                'grant_type': 'refresh_token',
                'scope': 'r_usr+w_usr'
            }
        else:
            data = {
                'client_id': self.apiKey['clientId'],
                'refresh_token': refreshToken,
                'grant_type': 'refresh_token',
                'scope': 'r_usr+w_usr+w_sub'
            }

        e, result = self.__post__(__AUTH_URL__ + '/token', data, (self.apiKey['clientId'], self.apiKey['clientSecret']))
        print(result)
        if e is not None:
            return str(e), False

        # result = requests.post(__AUTH_URL__ + '/token', data=data, auth=(self.apiKey['clientId'], self.apiKey['clientSecret'])).json()
        if 'status' in result and result['status'] != 200:
            return "Refresh failed. Please log in again.", False

        # if auth is successful:
        self.key.userId = result['user']['userId']
        self.key.countryCode = result['user']['countryCode']
        self.key.accessToken = result['access_token']
        self.key.expiresIn = result['expires_in']
        return None, True

    def loginByAccessToken(self, accessToken, userid=None):
        header = {'authorization': 'Bearer {}'.format(accessToken)}
        result = requests.get('https://api.tidal.com/v1/sessions', headers=header, verify=False).json()
        if 'status' in result and result['status'] != 200:
            return "Login failed!", False

        if not isNull(userid):
            if str(result['userId']) != str(userid):
                return "User mismatch! Please use your own accesstoken.", False

        self.key.userId = result['userId']
        self.key.countryCode = result['countryCode']
        self.key.accessToken = accessToken
        return None, True

    def loginByLoginPassword(self, login: str, password: str, app_mode: str = "DESKTOP"):
        session = requests.Session()
        # session.proxies = dict(http='socks5h://gateway-evn.neonteam.cc:30000', https='socks5h://gateway-evn.neonteam.cc:30000')
        redirect_uri = "tidal://login/auth" if app_mode != "android" else "https://tidal.com/android/login/auth"
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b'=')
        code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier).digest()).rstrip(b'=')
        client_unique_key = secrets.token_hex(16)
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) TIDAL/2.34.5 Chrome/106.0.5249.168 Electron/21.2.3 Safari/537.36" if app_mode != "android" else "Mozilla/5.0 (Linux; Android 10; Pixel 4 Build/QQ3A.200805.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/117.0.0.0 Mobile Safari/537.36"
        params = {
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'lang': 'en_US',
            'appMode': app_mode,
            'trackingUuid': client_unique_key,
            'client_id': self.apiKey["clientId"],
            'client_unique_key': client_unique_key,
            'consentStatus': "C0004:0",
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256',
            'restrictSignup': 'true',
            'state': "TIDAL_1696679079370_NSwxODgsMTMyLDI0NiwyMDMsMTQ5LDIyOSwxOTEsMTM2LDIzOCw0MCwyMTIsMjI0LDIzNSw5Niw1OSwyMTYsOTQsNzcsMTgsNTQsNzksMTA3LDUwLDEwNSwyMzcsMjE4LDE0NSwxMTYsMTExLDE5Niw0Mw"
        }
        
        print(params)

        # retrieve csrf token for subsequent request
        r = session.get('https://login.tidal.com/authorize', params=params, headers={
            'user-agent': user_agent,
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            'accept-language': 'en-US'
        }, verify=False)

        if r.status_code == 400:
            return f"Authorization failed! Is the clientid/token up to date?", False
        elif r.status_code == 403:
            return "Tidal BOT Protection on 1st stage, try again later!", False

        # try Tidal DataDome cookie request
        r = session.post('https://dd.tidal.com/js/', data={
            'ddk': '1F633CDD8EF22541BD6D9B1B8EF13A',  # API Key (required)
            'Referer': r.url,  # Referer authorize link (required)
            'responsePage': 'origin',  # useless?
            'ddv': '4.14.0'  # useless?
        }, headers={
            'user-agent': user_agent,
            'content-type': 'application/x-www-form-urlencoded'
        }, verify=False)

        if r.status_code != 200 or not r.json().get('cookie'):
            return "TIDAL BOT protection, could not get DataDome cookie!", False

        # get the cookie from the json request and save it in the session
        dd_cookie = r.json().get('cookie').split(';')[0]
        session.cookies[dd_cookie.split('=')[0]] = dd_cookie.split('=')[1]

        # enter email, verify email is valid
        r = session.post("https://login.tidal.com/api/email", params=params, json={
            'email': login
        }, headers={
            'user-agent': user_agent,
            'x-csrf-token': session.cookies['_csrf-token'],
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json',
            'accept-language': 'en-US'
        }, verify=False)

        if r.status_code != 200:
            try:
                _response = r.json()
                if _response.get("url"):
                    datadome = input(f"Please solve captcha at url {_response.get('url')} and enter cookie from response: ").split(';')[0]
                    session.cookies[datadome.split('=')[0]] = datadome.split('=')[1]
                    # enter email, verify email is valid
                    r = session.post("https://login.tidal.com/api/email", params=params, json={
                        'email': login
                    }, headers={
                        'user-agent': user_agent,
                        'x-csrf-token': session.cookies['_csrf-token'],
                        'accept': 'application/json, text/plain, */*',
                        'content-type': 'application/json',
                        'accept-language': 'en-US'
                    }, verify=False)
                    if r.status_code != 200:
                        return r.text, False
            except Exception:
                pass
            return r.text, False

        if not r.json()['isValidEmail']:
            return 'Invalid email', False
        if r.json()['newUser']:
            return 'User does not exist', False

        # login with user credentials
        r = session.post('https://login.tidal.com/api/email/user/existing', params=params, json={
            'email': login,
            'password': password
        }, headers={
            'User-Agent': user_agent,
            'x-csrf-token': session.cookies['_csrf-token'],
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json',
            'accept-language': 'en-US'
        }, verify=False)

        if r.status_code != 200:
            try:
                _response = r.json()
                if _response.get("url"):
                    datadome = input(f"Please solve captcha at url {_response.get('url')} and enter cookie from response: ").split(';')[0]
                    session.cookies[datadome.split('=')[0]] = datadome.split('=')[1]
                    # login with user credentials
                    r = session.post('https://login.tidal.com/api/email/user/existing', params=params, json={
                        'email': login,
                        'password': password
                    }, headers={
                        'User-Agent': user_agent,
                        'x-csrf-token': session.cookies['_csrf-token'],
                        'accept': 'application/json, text/plain, */*',
                        'content-type': 'application/json',
                        'accept-language': 'en-US'
                    }, verify=False)
                    if r.status_code != 200:
                        return r.text, False
            except Exception:
                pass
            return r.text, False

        # retrieve access code
        r = session.get('https://login.tidal.com/success?lang=en', allow_redirects=False, headers={
            'user-agent': user_agent,
            'accept-language': 'en-US'
        }, verify=False)

        if r.status_code == 401:
            return 'Incorrect password', False
        print(r.status_code, r.text)
        assert (r.status_code == 302 or r.status_code == 200)
        if r.status_code == 200:
            groups = re.findall(r'successRedirectUrl:"([^"]*)"', r.text)
            if not groups:
                return "Can't get access code", False
            url = urlparse(groups[0])
        else:
            url = urlparse(r.headers['location'])
        oauth_code = parse_qs(url.query)['code'][0]

        # exchange access code for oauth token
        r = requests.post(__AUTH_URL__ + '/token', data={
            'code': oauth_code,
            'client_id': self.apiKey["clientId"],
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
            'scope': 'r_usr w_usr w_sub',
            'code_verifier': code_verifier,
            'client_unique_key': client_unique_key
        }, headers={
            'User-Agent': user_agent
        }, verify=False)

        if r.status_code != 200:
            return r.text, False

        print(f"Authenticated with {r.json()['clientName']}!")

        # if auth is successful:
        self.key.userId = r.json()['user']['userId']
        self.key.countryCode = r.json()['user']['countryCode']
        self.key.accessToken = r.json()['access_token']
        self.key.expiresIn = r.json()['expires_in']
        self.key.refreshToken = r.json()['refresh_token']
        # print(f"SUCCESSFUL HACK: {self.key.accessToken} | {self.key.refreshToken} | {self.key.userId} | {self.key.expiresIn}")
        return None, True

    def getAlbum(self, id):
        msg, data = self.__get__('albums/' + str(id))
        return msg, dictToModel(data, Album())

    def getPlaylist(self, id):
        msg, data = self.__get__('playlists/' + str(id))
        return msg, dictToModel(data, Playlist())

    def getArtist(self, id):
        msg, data = self.__get__('artists/' + str(id))
        return msg, dictToModel(data, Artist())

    def getTrack(self, id):
        msg, data = self.__get__('tracks/' + str(id))
        return msg, dictToModel(data, Track())

    def getVideo(self, id):
        msg, data = self.__get__('videos/' + str(id))
        return msg, dictToModel(data, Video())
    
    def getMix(self, id):
        msg, tracks, videos = self.getItems(id, Type.Mix)
        if msg is not None:
            return msg, None
        mix = Mix()
        mix.id = id
        mix.tracks = tracks
        mix.videos = videos
        return None, mix
        
    def search(self, text: str, type: Type, offset: int, limit: int):
        typeStr = "ARTISTS,ALBUMS,TRACKS,VIDEOS,PLAYLISTS"
        if type == Type.Album:
            typeStr = "ALBUMS"
        if type == Type.Artist:
            typeStr = "ARTISTS"
        if type == Type.Track:
            typeStr = "TRACKS"
        if type == Type.Video:
            typeStr = "VIDEOS"
        if type == Type.Playlist:
            typeStr = "PLAYLISTS"

        params = {"query": text,
                  "offset": offset,
                  "limit": limit,
                  "types": typeStr}

        msg, data = self.__get__('search', params=params)
        return msg, dictToModel(data, SearchResult())

    def getLyrics(self, id):
        msg, data = self.__get__('tracks/' + str(id) + "/lyrics", urlpre='https://listen.tidal.com/v1/')
        return msg, dictToModel(data, Lyrics())

    def getItems(self, id, type: Type):
        if type == Type.Playlist:
            msg, data = self.__getItems__('playlists/' + str(id) + "/items")
        elif type == Type.Album:
            msg, data = self.__getItems__('albums/' + str(id) + "/items")
        elif type == Type.Mix:
            msg, data = self.__getItems__('mixes/' + str(id) + '/items')
        else:
            return "invalid Type!", None, None
        if msg is not None:
            return msg, None, None
        tracks = []
        videos = []
        for item in data:
            if item['type'] == 'track':
                tracks.append(dictToModel(item['item'], Track()))
            else:
                videos.append(dictToModel(item['item'], Video()))
        return msg, tracks, videos

    def getArtistAlbums(self, id, includeEP=False):
        albums = []
        msg, data = self.__getItems__('artists/' + str(id) + "/albums")
        if msg is not None:
            return msg, None
        for item in data:
            albums.append(dictToModel(item, Album()))
        if includeEP == False:
            return None, albums
        msg, data = self.__getItems__('artists/' + str(id) + "/albums", {"filter": "EPSANDSINGLES"})
        if msg is not None:
            return msg, None
        for item in data:
            albums.append(dictToModel(item, Album()))
        return None, albums

    def getStreamUrl(self, id, quality: AudioQuality, support_segmented_streaming: bool = False):
        squality = self.__getQualityString__(quality)
        paras = {"audioquality": squality, "playbackmode": "STREAM", "assetpresentation": "FULL"}
        msg, data = self.__get__('tracks/' + str(id) + "/playbackinfopostpaywall", paras, urlpre="https://desktop.tidal.com/v1/")
        if msg is not None:
            return msg, None
        resp = dictToModel(data, __StreamRespond__())
        print(resp.__dict__)
        print(f"{resp.trackid} - {resp.audioQuality}")

        if "vnd.tidal.bt" in resp.manifestMimeType:
            manifest = json.loads(base64.b64decode(resp.manifest).decode('utf-8'))
            ret = StreamUrl()
            ret.trackid = resp.trackid
            ret.soundQuality = resp.audioQuality
            ret.codec = manifest['codecs']
            ret.encryptionKey = manifest['keyId'] if 'keyId' in manifest else ""
            ret.url = manifest['urls'][0]
            ret.audioMode = resp.audioMode
            ret.streamType = "default"
            return "", ret
        elif "application/dash+xml" in resp.manifestMimeType and support_segmented_streaming:
            try:
                manifest_xml = base64.b64decode(resp.manifest).decode('utf-8')
                root = ET.fromstring(manifest_xml)
                namespaces = {"ns": 'urn:mpeg:dash:schema:mpd:2011'}
                initialization_url = root.find(".//ns:SegmentTemplate", namespaces).get("initialization")
                media_template = root.find(".//ns:SegmentTemplate", namespaces).get("media")
                segment_timeline = root.find(".//ns:SegmentTimeline", namespaces)
                codec = root.find(".//ns:Representation", namespaces).get("codecs")
                total_segments = sum([int(s.get("r", 0)) + 1 for s in segment_timeline.findall("ns:S", namespaces)])
                segments = []
                for i in range(0, total_segments + 1):
                    if i == 0:
                        segment_url = initialization_url
                    else:
                        segment_url = media_template.replace("$Number$", str(i))
                    segments.append(segment_url)
                print(segments)
                ret = SegmentStreamUrl()
                ret.trackid = resp.trackid
                ret.soundQuality = resp.audioQuality
                ret.codec = codec
                ret.url = f"https://google.com/file.{codec}"  # BACKWARD COMPABILITY HACK
                ret.total_segments = total_segments
                ret.segments = segments
                ret.audioMode = resp.audioMode
                ret.streamType = "stream"
                return "", ret
            except Exception as e:
                logging.exception("exception!", exc_info=e)
            
        return "Can't get the streamUrl, type is " + resp.manifestMimeType, None

    def getVideoStreamUrl(self, id, quality: VideoQuality):
        paras = {"videoquality": "HIGH", "playbackmode": "STREAM", "assetpresentation": "FULL"}
        msg, data = self.__get__('videos/' + str(id) + "/playbackinfopostpaywall", paras)
        if msg is not None:
            return msg, None
        resp = dictToModel(data, __StreamRespond__())

        if "vnd.tidal.emu" in resp.manifestMimeType:
            manifest = json.loads(base64.b64decode(resp.manifest).decode('utf-8'))
            array = self.__getResolutionList__(manifest['urls'][0])
            icmp = int(quality.value)
            index = 0
            for item in array:
                if icmp <= int(item.resolutions[1]):
                    break
                index += 1
            if index >= len(array):
                index = len(array) - 1
            return "", array[index]
        return "Can't get the streamUrl, type is " + resp.manifestMimeType, None

    def getTrackContributors(self, id):
        msg, data = self.__get__('tracks/' + str(id) + "/contributors")
        return msg, data

    def getCoverUrl(self, sid, width="320", height="320"):
        if sid is None or sid == "":
            return None
        return "https://resources.tidal.com/images/" + sid.replace("-", "/") + "/" + width + "x" + height + ".jpg"
    
    def getCoverData(self, sid, width="320", height="320"):
        url = self.getCoverUrl(sid, width, height)
        try:
            respond = requests.get(url, verify=False)
            return respond.content
        except:
            return ''

    def getArtistsName(self, artists=[]):
        array = []
        for item in artists:
            array.append(item.name)
        return " / ".join(array)

    def getFlag(self, data, type: Type, short=True, separator=" / "):
        master = False
        hi_res = False
        atmos = False
        explicit = False
        if type == Type.Album or type == Type.Track:
            if data.audioQuality == "HI_RES":
                master = True
            if data.audioQuality == "HI_RES_LOSSLESS":
                hi_res = True
            if type == Type.Album and "DOLBY_ATMOS" in data.audioModes:
                atmos = True
            if data.explicit is True:
                explicit = True
        if type == Type.Video:
            if data.explicit is True:
                explicit = True
        if not master and not atmos and not explicit and not hi_res:
            return ""
        array = []
        if master:
            array.append("M" if short else "Master")
        if hi_res:
            array.append("M" if short else "Max")
        if atmos:
            array.append("A" if short else "Dolby Atmos")
        if explicit:
            array.append("E" if short else "Explicit")
        return separator.join(array)

    def parseUrl(self, url):
        etype = Type.Null
        sid = ""
        if "tidal.com" not in url:
            return etype, sid

        url = url.lower()
        if 'artist' in url:
            etype = Type.Artist
        if 'album' in url:
            etype = Type.Album
        if 'track' in url:
            etype = Type.Track
        if 'video' in url:
            etype = Type.Video
        if 'playlist' in url:
            etype = Type.Playlist
        if 'mix' in url:
            etype = Type.Mix

        if etype == Type.Null:
            return etype, sid

        sid = stringHelper.getSub(url, etype.name.lower() + '/', '/')
        return etype, sid

    def getByString(self, string):
        etype = Type.Null
        obj = None

        if isNull(string):
            return "Please enter something.", etype, obj
        etype, sid = self.parseUrl(string)
        if isNull(sid):
            sid = string

        if obj is None and (etype == Type.Null or etype == Type.Album):
            msg, obj = self.getAlbum(sid)
        if obj is None and (etype == Type.Null or etype == Type.Artist):
            msg, obj = self.getArtist(sid)
        if obj is None and (etype == Type.Null or etype == Type.Track):
            msg, obj = self.getTrack(sid)
        if obj is None and (etype == Type.Null or etype == Type.Video):
            msg, obj = self.getVideo(sid)
        if obj is None and (etype == Type.Null or etype == Type.Playlist):
            msg, obj = self.getPlaylist(sid)
        if obj is None and (etype == Type.Null or etype == Type.Mix):
            msg, obj = self.getMix(sid)

        if obj is None or etype != Type.Null:
            return msg, etype, obj
        if obj.__class__ == Album:
            etype = Type.Album
        if obj.__class__ == Artist:
            etype = Type.Artist
        if obj.__class__ == Track:
            etype = Type.Track
        if obj.__class__ == Video:
            etype = Type.Video
        if obj.__class__ == Playlist:
            etype = Type.Playlist
        if obj.__class__ == Mix:
            etype = Type.Mix
        return msg, etype, obj

    """
    def getToken(self):
        token1 = "MbjR4DLXz1ghC4rV"    
        token2 = "pl4Vc0hemlAXD0mN"    # only lossless
        try:
            msg = requests.get( "https://cdn.jsdelivr.net/gh/yaronzz/CDN@latest/app/tidal/tokens.json", timeout=(20.05, 27.05))
            tokens = json.loads(msg.text)
            token1 = tokens['token']
            token2 = tokens['token2']
        except Exception as e:
            pass
        return token1,token2
    """
