from urllib.parse import urlencode
import requests
from time import sleep
import os
from urllib.parse import urljoin, urlparse, parse_qs
from settings import VK_TOKEN
import settings
from system_settings import BASE_API_URL, VK_APP_ID, VK_API_VERSION, DEBUG
import system_settings
import json

base_url = BASE_API_URL
app_id = VK_APP_ID
api_ver = VK_API_VERSION
vk_token = VK_TOKEN
is_debug = DEBUG
raw_file = system_settings.RAW_OUTPUT_FILE if getattr(system_settings, 'RAW_OUTPUT_FILE') else 'raw.out'
is_save_raw_response = system_settings.SAVE_RAW_RESPONSE if getattr(system_settings, 'SAVE_RAW_RESPONSE') else False


class ExceptionVK(Exception):
    def __init__(self, err_msg, err_code):
        self.err_msg = err_msg
        self.err_code = err_code

    def __str__(self):
        return self.err_msg


class VKBase:
    @classmethod
    def update_token_in_setting(cls, token: str):
        """
        update token in setting.py file and quit the program
        :param token:
        :return:
        """
        try:
            settings_path = settings.__file__
            with(open(settings_path, 'r')) as f:
                lines = f.readlines()

            for i, line in enumerate(lines):
                if line.find('VK_TOKEN') > -1:
                    lines[i] = f'VK_TOKEN = "{token}"\n'
                    break
                if len(
                        lines) == i + 1:  # if 'VK_TOKEN' not found in settings.py file - append it. But if VK_TOKEN doesn't present app will raise exception anyway.
                    lines.append(f'VK_TOKEN = "{token}"\n')

            with(open(settings_path, 'w')) as f:
                f.writelines(lines)
        except Exception as e:
            print('Something wrong here [update_token_in_setting]', e)
            exit(1)
        return True

    @classmethod
    def test_vk_connection(cls) -> int:
        """
            Check that token is valid
            :return: 0 - ok, 5- token not valid
        """
        params = {'screen_name': 'durov'}
        try:
            cls.vk_request(method='utils.resolveScreenName', params=params).get('object_id')
        except ExceptionVK as e:
            if e.err_code == 5:
                return 5
            else:
                return 1
        return 0

    @classmethod
    def test_vk_connection_with_prompt(cls):
        """
        Check that token is valid and prompt for new token
        :return: True if success, False if unhandled error occurs
        """

        message = """
        Your access token is not valid. Follow procedure below to get access:
        1) Copy link to browser
        {url}
        2) Type your credentials and click OK if asked
        3) Copy entire string from address bar of your browser         
        """
        if cls.test_vk_connection() == 5:
            print(message.format(url=cls.generate_new_token()))
            vk_url_response = input("Paste the sting from the browser here:")
            params = urlparse(vk_url_response)[5]

            token = parse_qs(params).get('access_token').pop()
            if token:
                cls.update_token_in_setting(token)
                global vk_token
                vk_token = token
                cls.test_vk_connection_with_prompt()  # run test again, I hope here is no infinite recursion
        elif cls.test_vk_connection() > 0:
            # Unhandled error during connection to VK."
            return False
        return True

    @classmethod
    def generate_new_token(cls):
        """
        Create URL to get token
        :return: URL to get token
        """
        APP_ID = app_id
        OAUTH_URL = 'https://oauth.vk.com/authorize'
        OAUTH_PARAMS = {
            'client_id': APP_ID,
            'display': 'page',
            'scope': 'status,groups',
            'response_type': 'token',
            'v': api_ver,
        }
        url = '?'.join((OAUTH_URL, urlencode(OAUTH_PARAMS)))
        # print(url)
        # response = requests.get(url)
        return url

    @classmethod
    def vk_request(cls, method, params={}):
        """
        Helper to query VK API with error handling
        :param method: VK API method
        :param params:  Parameter for query (dict)
        :return: response of VK API
        """
        common_params = {
            'access_token': vk_token,  # cls.get_token(),
            'v': api_ver,
        }
        common_params.update(params)
        response = ''
        for i in range(10):
            if is_debug:  # debug message
                print('*', end='')  # callback function would be better

            # response = requests.get(url, params)
            url_q = urljoin(base_url, method)
            response = requests.get(
                url_q,
                # f'https://api.vk.com/method/{method}',
                params=common_params
            )

            if is_save_raw_response:
                with open(raw_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n=====method: {method} params: {params}\n")
                    json.dump(response.json(), f, ensure_ascii=False)

            if response.status_code != 200:
                sleep(1)
            elif 'error' in response.json():
                err_code = response.json().get('error').get('error_code')
                err_msg = response.json().get('error').get('error_msg')
                if err_code == 6:  # 'Too many requests per second'
                    sleep(1)
                else:
                    raise ExceptionVK(err_msg=err_msg, err_code=err_code)
            else:
                break
        vk_response = response.json().get('response')
        return vk_response

    @classmethod
    def vk_request_batch(cls, method, ids):
        """
        Helper to send 25 VK API queries as batch. VK method Execute is used.
        :param method: method to query
        :param ids: ids as parameter to query method (list)
        :return: list in format [[user_id,[<response ids>]],...]
        """
        if is_debug:  # debug message
            print(os.linesep, f'[Debug] VK batch request {method} has started')

        def make_vk_script(method, ids: str, ):
            vk_script_text = f''' var users = [{ids}]; 
                        var out = [] ; 
                        var i=0; 
                        while (i < users.length){{{{ 
                            out.push([users[i], API.{method}({{"user_id": users[i]}}).items]); 
                            i= i+1; 
                        }}}}
                        return out;'''
            return vk_script_text

        ids_copy = ids[:]
        out_ids = []
        while ids_copy:
            ids_s = ','.join(tuple(str(i) for i in ids_copy[:25]))
            del ids_copy[:25]
            vk_script = make_vk_script(method, ids_s)
            t = cls.vk_request('execute', {"code": vk_script})
            out_ids += t
        return out_ids
