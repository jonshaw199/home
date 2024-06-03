#!/usr/bin/env python3

import os
import http.client
import json
from dotenv import load_dotenv

load_dotenv()
HOME_HOST = os.getenv('HOME_HOST')
HOME_PORT = os.getenv('HOME_PORT')
HOME_USERNAME = os.getenv('HOME_USERNAME')
HOME_PASSWORD = os.getenv('HOME_PASSWORD')


class Auth:
    def __init__(self):
        self.token = ''

    def get_token(self):
        conn = http.client.HTTPConnection(f'{HOME_HOST}:{HOME_PORT}')
        body = json.dumps({
            'username': HOME_USERNAME,
            'password': HOME_PASSWORD
        })
        headers = {'Content-type': 'application/json'}
        conn.request("POST", '/api-token-auth/', body, headers)
        response = conn.getresponse()
        if response.status != 200:
            raise Exception('Failed to get auth token')
        response_data = json.loads(response.read())
        self.token = response_data["token"]
        print(f'Token: {self.token}')
        return self.token
