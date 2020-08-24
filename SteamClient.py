#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import time
import decimal
import requests
from tqdm import tqdm
import steam.webauth as wa
from bs4 import BeautifulSoup
from urllib.parse import quote
from base64 import b64decode, b64encode
from steam.guard import SteamAuthenticator

class ApiException(Exception):
    def __init__(self, error):
        print(error)
        
def toNearest(num, tickSize):
    tickDec = decimal.Decimal(str(tickSize))
    return float((decimal.Decimal(round(num / tickSize, 0)) * tickDec))

class SteamClient:
    def __init__(self, username, password, secrets=None, deviceId=None):
        self.user = wa.WebAuth(username, password)
        if secrets is not None:
            self.mobile = wa.MobileWebAuth(username, password)
            self.sa = SteamAuthenticator(secrets)
        else:
            self.mobile = None
            self.sa = None
        self.deviceId = deviceId
        self.login()
        self.baseURL = 'https://steamcommunity.com'
        self.urlToId = {}
        self.SIDDB = requests.Session()
        print(f'Steam User: {self.user.steam_id.as_64} Logged.')

    def login(self):
        notDone = True
        while notDone:
            try:
                self.user.login()
            except wa.CaptchaRequired:
                print(self.user.captcha_url)
                self.user.login(captcha=input('Captcha: '))
                notDone = False
            except wa.EmailCodeRequired:
                self.user.login(email_code=input('Email Code: '))
                notDone = False
            except wa.TwoFactorCodeRequired:
                if self.sa is None:
                    self.user.login(twofactor_code=input('Two-Factor Code: '))
                else:
                    self.user.login(twofactor_code=self.sa.get_code())
                notDone = False
        self.steamId = self.user.steam_id
        if self.mobile is None:
            return
        timeToSleep = 30 - int(time.time() % 30) + 1
        for i in tqdm(range(timeToSleep), desc='Waiting for next code'):
            time.sleep(1)
        notDone = True
        while notDone:
            try:
                self.mobile.login()
            except wa.CaptchaRequired:
                print(self.mobile.captcha_url)
                self.mobile.login(captcha=input('Captcha: '))
                notDone = False
            except wa.EmailCodeRequired:
                self.mobile.login(email_code=input('Email Code: '))
                notDone = False
            except wa.TwoFactorCodeRequired:
                self.mobile.login(twofactor_code=self.sa.get_code())
                notDone = False
        return
        
    def validateWalletCode(self, code):
        payload = {
            'sessionid': self.user.session.cookies.get_dict()['sessionid'],
            'wallet_code': code
        }
        return self.user.session.post('https://store.steampowered.com/account/validatewalletcode/', data=payload).json()
    
    def redeemWalletCode(self, code):
        payload = {
            'sessionid': self.user.session.cookies.get_dict()['sessionid'],
            'wallet_code': code
        }
        return self.user.session.post('https://store.steampowered.com/account/confirmredeemwalletcode/', data=payload).json()