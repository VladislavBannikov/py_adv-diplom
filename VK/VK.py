from urllib.parse import urlencode
import requests
from time import sleep
import os
from helpers.singleton import singleton
import json
from urllib.parse import urljoin, urlparse, parse_qs
import settings
import system_settings
import sys

BASE_API_URL = 'https://api.vk.com/method/'

class ExceptionVK(Exception):
    def __init__(self, err_msg, err_code):
        self.err_msg = err_msg
        self.err_code = err_code

    def __str__(self):
        return self.message


@singleton
class VK:
    def __init__(self):
        self.test_vk_connection()
        # pass

    @classmethod
    def update_token_in_setting(cls, token: str):
        """
        update token in setting.py file and quit the program
        :param token:
        :return:
        """
        settings_path = settings.__file__
        with(open(settings_path, 'r')) as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if line.find('VK_TOKEN') > -1:
                lines[i] = f'VK_TOKEN = "{token}"\n'
                break
            if len(lines) == i+1:  # if 'VK_TOKEN' not found in settings.py file - append it. But if VK_TOKEN doesn't present app will raise exception anyway.
                lines.append(f'VK_TOKEN = "{token}"\n')

        with(open(settings_path, 'w')) as f:
            f.writelines(lines)
        print('Token updated. Please run the program again.')
        exit(0)

    @classmethod
    def test_vk_connection(cls):
        """
        Check that token is valid
        :return:
        """
        params = {'screen_name': 'durov'}
        try:
            cls.vk_request(method='utils.resolveScreenName', params=params).get('object_id')
        except ExceptionVK as e:
            message = """
            Your access token is not valid. Follow procedure below to get access:
            1) Copy link to browser
            {url}
            2) Type your credentials and click OK if asked
            3) Copy entire string from address bar of your browser         
            """
            if e.err_code == 5:
                print(message.format(url=cls.generate_new_token()))
                vk_url_response = input("Paste the sting from the browser here:")
                params = urlparse(vk_url_response)[5]

                token = parse_qs(params).get('access_token').pop()
                if token:
                    cls.update_token_in_setting(token)
        return


    @classmethod
    def generate_new_token(cls):
        """
        Create URL to get token
        :return: URL to get token
        """
        APP_ID = system_settings.VK_APP_ID
        OAUTH_URL = 'https://oauth.vk.com/authorize'
        OAUTH_PARAMS = {
            'client_id': APP_ID,
            'display': 'page',
            'scope': 'status,groups',
            'response_type': 'token',
            'v': system_settings.VK_API_VERSION,
        }
        url = '?'.join((OAUTH_URL, urlencode(OAUTH_PARAMS)))
        # print(url)
        # response = requests.get(url)
        return url

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
            'access_token': settings.VK_TOKEN, #cls.get_token(),
            'v': system_settings.VK_API_VERSION,
        }
        common_params.update(params)
        response = ''
        for i in range(10):
            if system_settings.DEBUG:  # debug message
                print('.', end='')  # callback function would be better

            # response = requests.get(url, params)
            url_q = urljoin(BASE_API_URL, method)
            response= requests.get(
                url_q,
                # f'https://api.vk.com/method/{method}',
                params=common_params
            )
            # print(json.dumps(response))
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
                    raise ExceptionVK(err_msg=err_msg, err_code=err_code)
            else:
                break
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
        if system_settings.DEBUG: # debug message
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

