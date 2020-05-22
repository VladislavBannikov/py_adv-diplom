from urllib.parse import urlencode
import requests
from time import sleep
import os
from helpers.singleton import singleton


@singleton
class VK:
    __ACCESS_TOKEN = ''  # token for access VK AP (load from token.key)
    __IS_DEBUG = False  # If True print dot when VK API is called

    @classmethod
    def read_token(cls):
        """
        Read from token.key
        :return: no return
        """
        if cls.__ACCESS_TOKEN == '':
            with open('token.key') as f:
                cls.__ACCESS_TOKEN = f.read()
        #  TODO: check if file exists, maybe run create token automatically

    def __init__(self):
        self.read_token()

    @classmethod
    def get_is_debug(cls):
        return cls.__IS_DEBUG

    @classmethod
    def set_is_debug(cls, dp: bool):
        cls.__IS_DEBUG = dp

    @classmethod
    def generate_new_token(cls):
        """
        Create URL to get token
        :return: URL to get token
        """
        APP_ID = '7465530'
        OAUTH_URL = 'https://oauth.vk.com/authorize'
        OAUTH_PARAMS = {
            'client_id': APP_ID,
            'display': 'page',
            'scope': 'status,groups',
            'response_type': 'token',
            'v': '5.89',
        }
        url = '?'.join((OAUTH_URL, urlencode(OAUTH_PARAMS)))
        # print(url)
        # response = requests.get(url)
        return url #response.text

    @classmethod
    def get_token(cls):
        return cls.__ACCESS_TOKEN

    @classmethod
    def vk_request(cls, method, params={}):
        """
        Helper to query VK API with error handling
        :param method: VK API method
        :param params:  Parameter for query (dict)
        :return: response of VK API
        """
        common_params = {
            'access_token': cls.get_token(),
            'v': '5.89',
        }
        common_params.update(params)
        response = ''
        for i in range(10):
            if cls.get_is_debug():  # debug message
                print('.', end='')  # callback function would be better

            # response = requests.get(url, params)
            response= requests.get(
                f'https://api.vk.com/method/{method}',
                params=common_params
            )
            if response.status_code != 200:
                sleep(1)
            elif 'error' in response.json():
                err_code = response.json().get('error').get('error_code')
                err_msg = response.json().get('error').get('error_msg')
                key = response.json().get('error').get('request_params')[0].get('key')
                value = response.json().get('error').get('request_params')[0].get('value')
                if err_code == 6:  # 'Too many requests per second'
                    sleep(1)
                else:
                    raise Exception(f'Error: {err_msg}, {key}: {value}, {err_code}')
            else:
                break
        # print(response)
        list = response.json().get('response')
        return list

    @classmethod
    def vk_request_batch(cls, method, ids):
        """
        Helper to send 25 VK API queries as batch. VK method Execute is used.
        :param method: method to query
        :param ids: ids as parameter to query method (list)
        :return: list in format [[user_id,[<response ids>]],...]
        """
        if cls.get_is_debug(): # debug message
            print(os.linesep, f'[Debug] VK batch request {method} has started')

        def make_vk_script(method, ids: str, ):
            code = 'var users = [%s]; \
            var out = [] ; \
            var i=0; \
            while (i < users.length){{ \
                out.push([users[i], API.%s({"user_id": users[i]}).items]); \
                i= i+1; \
            }} \
            return out;' % (ids, method)
            return code

        ids_copy = ids[:]
        out_ids = []
        while ids_copy:
            ids_s = ','.join([str(i) for i in ids_copy[:25]])
            del ids_copy[:25]
            vk_script = make_vk_script(method, ids_s)
            t = cls.vk_request('execute', {"code": vk_script})
            out_ids += t
        return out_ids

