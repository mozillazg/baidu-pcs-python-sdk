#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

api_template = 'https://pcs.baidu.com/rest/2.0/pcs/{0}'

class PCS(object):
    def __init__(self, access_token, api_template=api_template):
        self.access_token = access_token
        self.api_template = api_template

    def quota(self):
        api = self.api_template.format('quota')
        params = {
            'method': 'info',
            'access_token': self.access_token
        }
        response = requests.get(api, params=params)
        return response.json()
        # if response.ok:
        #     pass


def main():
    api_key = '6Uc87wOtAB2VdaSXUpe5z8IW'
    secret_key = 'RmwGHXadU27kb0jzHr8sXpDXZ8iE70dW'
    access_token = '3.3f56524f9e796191ce5baa84239feb15.2592000.1380728222.'
    access_token += '570579779-1274287'
    pcs = PCS(access_token)
    print pcs.quota()

if __name__ == '__main__':
    main()
