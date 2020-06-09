from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import socket
from threading import Thread
import requests
from urllib.parse import urljoin, urlparse, parse_qs
from tests.load_fixtures import get_id_screen_name


class MockServerRequestHandler(BaseHTTPRequestHandler):

    # def __init__(self):
    #     print("mock server")
    #     super(MockServerRequestHandler, self).__init__() TODO: При определении метода init, как вызвать инициализацию родительского класса?

    # SCREEN_NAME_PATTERN = re.compile(r'/utils.resolveScreenName')

    fixtures_name_id = get_id_screen_name()

    def do_GET(self):
        url_parsed = urlparse(self.path)
        if str.lower(url_parsed[2]) == '/utils.resolveScreenName'.lower():
        # if re.search(self.SCREEN_NAME_PATTERN, self.path):
            params = parse_qs(url_parsed[4])
            screen_name = params.get('screen_name')[0]
            user_id = self.fixtures_name_id.get(screen_name, None)
            if user_id:
                resp_content = {"response": {"object_id": user_id, "type": "user"}}
            else:
                resp_content = {"response": []}

            # Add response status code.
            self.send_response(requests.codes.ok)

            # Add response headers.
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()

            # Add response content.
            response_content = json.dumps(resp_content)
            self.wfile.write(response_content.encode('utf-8'))
            return


def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    address, port = s.getsockname()
    s.close()
    return port


def start_mock_server(port):
    mock_server = HTTPServer(('localhost', port), MockServerRequestHandler)
    mock_server_thread = Thread(target=mock_server.serve_forever)
    mock_server_thread.setDaemon(True)
    mock_server_thread.start()