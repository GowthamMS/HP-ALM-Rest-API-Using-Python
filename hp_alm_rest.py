#!/usr/bin/env python
"""
Hp ALM Rest provides handle to perform CRUD operations on HP ALM via REST Api

Copyrights (c) HP-ALM-Rest-API-Automation-Using-Python 2018

Author: gowtham10ms@gmail.com
"""

import json
import logging
import requests

__author__ = "Gowtham MS"
__copyright__ = "Copyright 2018, HP-ALM-Rest-API-Automation-Using-Python"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Gowtham MS"
__email__ = "gowtham10ms@gmail.com"
__status__ = "Production"

# pylint: disable=

logging.basicConfig(level=logging.INFO, format='%(message)s')
LOG = logging.getLogger(__name__)
LOG.addHandler(logging.FileHandler('%s.log' % __name__, 'w'))

USERNAME = 'xxxxx'
PASSWORD = 'xxxxx'
DOMAIN = 'xxxxx'
PROJECT = 'xxxxx'


class HpALMRest(object):
    """
    HP ALM Rest class
    :param username:
    :param password:
    """

    def __init__(self, username, password):
        """
        Init class of HpALMRest
        :param username:
        :param password:
        """
        self.username = username
        self.password = password
        self.header = {'Accept': 'application/xml', 'Content-Type': 'application/xml'}
        self.cookies = {}

    def login(self):
        """
        Logs into HP ALM and saves the session handler in self.cookies
        :return:
        """
        credentials = (self.username, self.password)
        auth_url = 'http://<Enter Your URL>.com:<Enter Your Port>/qcbin/' \
                   'authentication-point/authenticate'
        response = requests.request("POST", url=auth_url, auth=credentials)
        LOG.info('URL: %s\nResponse Code: %s', auth_url, response.status_code)

        if response.status_code != 200:
            raise Exception(response.reason)

        LOG.info('Authentication Successful')
        cookie = (response.headers['Set-Cookie'].split(';')[0].replace('LWSSO_COOKIE_KEY=', ''))
        self.cookies['LWSSO_COOKIE_KEY'] = cookie

        session_url = "http://<Enter Your URL>.com:<Enter Your Port>/qcbin/rest/site-session"
        session_response = requests.request("POST", url=session_url, cookies=self.cookies)
        LOG.info('URL: %s\nResponse Code: %s', session_url, session_response.status_code)

        if session_response.status_code != 201:
            raise Exception(session_response.reason)

        j_session_id = session_response.headers["Set-Cookie"].split(',')[0].split(';')[0]. \
            replace('JSESSIONID=', '').strip()
        qc_session = session_response.headers["Set-Cookie"].split(',')[1].split(';')[0]. \
            replace('QCSession=', '').strip()
        alm_user = session_response.headers["Set-Cookie"].split(',')[2].split(';')[0]. \
            replace('ALM_USER=', '').strip()
        xsrf_token = session_response.headers["Set-Cookie"].split(',')[-1].split(';')[0]. \
            replace('XSRF-TOKEN=', '').strip()
        self.cookies["QCSession"] = qc_session
        self.cookies["XSRF-TOKEN"] = xsrf_token
        self.cookies["JSESSIONID"] = j_session_id
        self.cookies["ALM_USER"] = alm_user
        self.header["Accept"] = 'application/json'
        LOG.info('Login Successful')

    def get_domains(self):
        """
        Gets and lists all the available domains
        :return: domains(dict): domains details
        """
        domains_url = 'http://<Enter Your URL>.com:<Enter Your Port>/qcbin/rest/domains'
        response = requests.request("GET", url=domains_url,
                                    headers=self.header, cookies=self.cookies)
        LOG.info('URL: %s\nResponse Code: %s', domains_url, response.status_code)

        if response.status_code != 200:
            raise Exception(response.reason)

        content = response.content.decode("utf-8")
        domains = json.loads(str(content))
        LOG.info(domains)
        return domains

    def get_projects(self, domain_name):
        """
        Gets and lists all the available projects in the domain
        :param domain_name:
        :return projects:
        """
        projects_url = 'http://<Enter Your URL>.com:<Enter Your Port>/qcbin/rest/domains/%s/' \
                       'projects/' % domain_name
        response = requests.request("GET", url=projects_url,
                                    headers=self.header, cookies=self.cookies)
        LOG.info('URL: %s\nResponse Code: %s', projects_url, response.status_code)

        if response.status_code != 200:
            raise Exception(response.reason)

        content = response.content.decode("utf-8")
        projects = json.loads(str(content))
        LOG.info(projects)
        return projects

    def get_total_tests_count(self, domain_name, project_name):
        """
        Gets and returns the total tests count in the project
        :param domain_name:
        :param project_name:
        :return total_tests_count:
        """
        tests_url = 'http://<Enter Your URL>.com:<Enter Your Port>/qcbin/rest/domains/%s/' \
                    'projects/%s/tests?page-size=1' % (domain_name, project_name)
        response = requests.request("GET", url=tests_url, headers=self.header, cookies=self.cookies)
        LOG.info('URL: %s\nResponse Code: %s', tests_url, response.status_code)

        if response.status_code != 200:
            raise Exception(response.reason)

        content = response.content.decode("utf-8")
        tests = json.loads(str(content))
        LOG.info(tests)
        total_tests_count = tests["TotalResults"]
        LOG.info(total_tests_count)
        return total_tests_count

    def get_all_tests(self, domain_name, project_name):
        """
        Gets and lists all the available tests in the project
        :param domain_name:
        :param project_name:
        :return:
        """
        total_tests_count = self.get_total_tests_count(domain_name=domain_name,
                                                       project_name=project_name)
        tests_url = 'http://<Enter Your URL>.com:<Enter Your Port>/qcbin/rest/domains/%s/' \
                    'projects/%s/tests?page-size=%s' % (domain_name, project_name,
                                                        total_tests_count)
        LOG.info('Fetching All Tests.Time Consuming!.Please wait.')
        response = requests.request("GET", url=tests_url, headers=self.header, cookies=self.cookies)
        LOG.info('URL: %s\nResponse Code: %s', tests_url, response.status_code)

        if response.status_code != 200:
            raise Exception(response.reason)

        content = response.content.decode("utf-8")
        tests = json.loads(str(content))
        LOG.info(tests)


if __name__ == '__main__':
    REST_HANDLER = HpALMRest(username=USERNAME, password=PASSWORD)
    REST_HANDLER.login()
    REST_HANDLER.get_domains()
    REST_HANDLER.get_projects(DOMAIN)
    REST_HANDLER.get_all_tests(DOMAIN, PROJECT)
