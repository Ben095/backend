import requests
from bs4 import BeautifulSoup
import json
# from py_bing_search import PyBingWebSearch
from urlparse import urlparse
import sys
import urllib2
import re
from multiprocessing import Pool
from tornado import ioloop, httpclient
from flask.ext.sqlalchemy import SQLAlchemy

import os
from flask import Flask, render_template, request, redirect, url_for
import os
from flask import Flask, abort, request, jsonify, g, url_for
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from flask_restful import reqparse, abort, Api, Resource, fields, marshal_with
import requests
import stripe
from firebase import firebase
# from pyfcm import FCMNotification
import json
import time
# from youtubescraper import*
import grequests
from grequests import*
from functools import partial

from urlparse import urlparse
from threading import Thread
import httplib
import sys
from Queue import Queue
import logging
import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from celery import Celery
from flask import Response
from itertools import chain
from celery import Celery
from celery.task.control import inspect
from celery.result import AsyncResult

#from models import*
from celery.result import AsyncResult

rearr = []
celery = Celery('tasks', backend='amqp', broker='amqp://')
log = logging.getLogger(__name__)
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


from models import*



@celery.task(ignore_result=True)
def print_hello():
    print 'hello there'


@celery.task
def gen_prime(x):
    multiples = []
    results = []
    for i in xrange(2, x + 1):
        if i not in multiples:
            results.append(i)
            for j in xrange(i * i, x + 1, i):
                multiples.append(j)
    return results


@app.route('/outreach/<query>/results/')
def FinalResults(query,username):
    queryResults = Result.query.filter_by(query=query).first()
    task_id = queryResults.task_id
    res = AsyncResult(task_id)
    if "True" in res.ready():
        return jsonify(results=res.get())
    else:
        return "Query is still being processed! Please wait!"




@app.route('/outreach/backend/<query>')
def backendWorker(query):
    outreach = OutReacherDesk.delay(query)
    task_id = outreach.task_id
    user = Result(task_id=task_id, username='Jack', query=query)
    db.session.add(user)
    db.session.commit()
    return "Added to queue!"

@celery.task
def OutReacherDesk(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_1 like Mac OS X)AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0'

    }
    arr = ['0', '23', '37', '51', '65', '79']
    appendArr = []  
    biggerArr = []
    for i in arr:
        response = requests.get('https://c.bingapis.com/api/custom/opal/otherpage/search?q=' + str(
            query) + '&first=' + str(i) + '&rnoreward=1', headers=headers).text
        LoadAsJson = json.loads(response)
        actualItem = LoadAsJson['answers'][0]['webResults']
        appendArr.append(actualItem)

    biggerArr.append(appendArr[
                     0] + appendArr[1] + appendArr[2] + appendArr[3] + appendArr[4] + appendArr[5])
    rearr = []
    for items in biggerArr:
        eachQuery = items
        domainArray = []
        eachPageWhoisResult = []
        async_list = []
        for eachQueryString in eachQuery:
            try:
                bingDictionary = {}
                bingDictionary['prospect_url'] = eachQueryString[
                    'displayUrl']
                bingDictionary['meta_title'] = eachQueryString[
                    'shortTitle'].encode('ascii', 'ignore')
                url = urlparse(eachQueryString['url'])
                domain = '{uri.scheme}://{uri.netloc}/'.format(uri=url)
                bingDictionary['root_domain'] = domain
                formatDomain = str(domain).replace(
                    'http://', '').replace('https://', '')
                fixedDomain = formatDomain.split('/')[0]
                whoisAPI = 'http://api.whoxy.com/?key=f5bd9ed47568013u5c00d35155ec3884&whois=' + \
                    str(fixedDomain)
                domainArray.append(whoisAPI)
                bingDictionary['whoisData'] = "None"
                bingDictionary['social_shares'] = "None"
                miniArz = []
                resp = requests.get(whoisAPI)
                loadAsJson = json.loads(resp.text)
                whoisDictionary = {}
                try:
                    whoisDictionary['domain_name'] = loadAsJson['domain_name']
                except:
                    whoisDictionary['domain_name'] = "None"
                try:
                    whoisDictionary['whois_full_name'] = loadAsJson[
                        'registrant_contact']['full_name']
                except:
                    whoisDictionary['whois_full_name'] = "None"
                try:
                    whoisDictionary['whois_company_name'] = loadAsJson[
                        'registrant_contact']['company_name']
                except:
                    whoisDictionary['whois_company_name'] = "None"
                try:
                    whoisDictionary['whois_city_name'] = loadAsJson[
                        'registrant_contact']['city_name']
                except:
                    whoisDictionary['whois_city_name'] = "None"
                try:
                    whoisDictionary['whois_country_name'] = loadAsJson[
                        'registrant_contact']['country_name']
                except:
                    whoisDictionary['whois_country_name'] = "None"
                try:
                    whoisDictionary['whois_email_address'] = loadAsJson[
                        'registrant_contact']['email_address']
                except:
                    whoisDictionary['whois_email_address'] = "None"
                try:
                    whoisDictionary['whois_phone_number'] = loadAsJson[
                        'registrant_contact']['phone_number']
                except:
                    whoisDictionary['whois_phone_number'] = "None"
                miniArz.append(whoisDictionary)
                bingDictionary['whoisData'] = miniArz
                rearr.append(bingDictionary)
            except KeyError,RuntimeError:
                pass
    return rearr
   
if __name__ == '__main__':
    app.run()