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
import xlsxwriter
import os
from flask import Flask, render_template, request, redirect, url_for
import os
from flask import Flask, abort, request, jsonify, g, url_for
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from flask import make_response
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
from flask import send_file
from urlparse import urlparse
from threading import Thread
import httplib
import sys
from Queue import Queue
import logging
import requests
from requests.adapters import HTTPAdapter 
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from celery import Celery
from flask import Response
from itertools import chain
from celery import Celery
from celery.task.control import inspect
from celery.result import AsyncResult
from time import sleep
#from models import*
from celery.result import AsyncResult
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO


rearr = []
celery = Celery('tasks', backend='amqp', broker='amqp://')
log = logging.getLogger(__name__)
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


from models import*
from InstagramAPI import InstagramAPI

class RetryHTTPAdapter(HTTPAdapter):

    SECONDS_BETWEEN_RETRIES = 5

    def __init__(self, retry_time=120, *args, **kwargs):
        self.retry_time = retry_time
        super(RetryHTTPAdapter, self).__init__(*args, **kwargs)

    def send(self, *args, **kwargs):
        for _ in range(int(self.retry_time / self.SECONDS_BETWEEN_RETRIES)):
            response = super(RetryHTTPAdapter, self).send(*args, **kwargs)
            if response.status_code == httplib.OK:
                break
            time.sleep(self.SECONDS_BETWEEN_RETRIES)
        return response

s = requests.Session()
s.mount('http://', RetryHTTPAdapter(retry_time=180))
s.mount('https://', RetryHTTPAdapter(retry_time=180))

def igFunction(name):
    try:
        excelArr = []
        dictionary = {}
        #responseID = s.get('https://www.instagram.com/'+str(name)+'/?__a=1')
        response = s.get('https://www.instagram.com/'+str(name)+'/?__a=1').text
        JSON = json.loads(response)
        URL = 'https://www.instagram.com/'+str(name)
        dictionary['url'] = URL
        Username = JSON['user']['username']
        dictionary['username'] = Username
        Name = JSON['user']['full_name']
        dictionary['name'] = Name
        UID = JSON['user']['id']
        dictionary['UID'] = UID
        Followers = JSON['user']['followed_by']['count']
        dictionary['followers'] = Followers
        Following = JSON['user']['follows']['count']
        dictionary['following'] = Following
        Verified = JSON['user']['is_verified']
        dictionary['verified'] = Verified
        Uploads = JSON['user']['media']['count']
        dictionary['uploads'] = Uploads
        Private = JSON['user']['is_private']
        dictionary['private'] = Private
        Bio = JSON['user']['biography']
        dictionary['bio'] = Bio
        URLFIELD = JSON['user']['external_url']
        dictionary['external_url'] = URLFIELD
        dictionary['snapchat'] = "None"
        try:
            justTEXT = Bio.encode('ascii','ignore')
            splitJustTEXT = justTEXT.split('\n')
            #emails = re.findall(r'[\w\.-]+@[\w\.-]+', splitJustTEXT) 
            dictionary['email']=''
            for items in splitJustTEXT:
                if "Snapchat" in items:
                    dictionary['snapchat'] = items
                if "Snap" in items:
                    dictionary['snapchat'] = items

                if "SNAPCHAT" in items:
                    dictionary['snapchat'] = items
                if "snap" in items:
                    dictionary['snapchat'] = items

                if "sc" in items:
                    dictionary['snapchat'] = items
                match = re.search(r'[\w.-]+@[\w.-]+.\w+', items)
                if match:
                    try:
                        dictionary['email']=match.group().split('')[0]
                    except:
                        dictionary['email']=match.group()


        	    # if match:
            	# 	try:
            	#      		 dictionary['email']=match.group().split('')[0]
            	# 	except:
            	# 		 dictionary['email']=match.group()
        except:
            pass
		
       # print dictionary
        excelArr.append(dictionary)
        return excelArr
    except:
        pass


##make a function that calls InstagramResult -> 
## 
@celery.task
def InstagramMain(name):
    #def generate():
        with app.app_context():
            try:
                finalData = igFunction(name)
                outputDict = {}
                response = s.get('https://www.instagram.com/'+str(name)+'/?__a=1').text
                JSON = json.loads(response)
                UID = JSON['user']['id']
                ig = InstagramAPI("benjidahal", "123123123vb")
                ig.login()
                main_list = ig.getTotalFollowersID2(UID)
                finalArr = []
                finalOutput = []
                for items in main_list:
                    try:
                        username = items['username']
                        print username
                        finalArr.append(igFunction(username))
                    except TypeError:
                        pass
                outputDict['self_user_info'] = finalData
                outputDict['each_followers_data'] = finalArr
                finalOutput.append(outputDict)
        	    #print finalOutput


                output = StringIO.StringIO()
               # workbook = xlsxwriter.Workbook(output)
                workbook = xlsxwriter.Workbook(name+'.xlsx')
                worksheet = workbook.add_worksheet()
                worksheet.set_column(1, 1, 15)
                bold = workbook.add_format({'bold': 1})
                worksheet.write('A1', 'username', bold)
                worksheet.write('B1', 'bio', bold)
                worksheet.write('C1', 'snapchat', bold)
                worksheet.write('D1', 'verified', bold)
                worksheet.write('E1', 'name', bold)
                worksheet.write('F1', 'url', bold)
                worksheet.write('G1', 'private', bold)
                worksheet.write('H1', 'followers', bold)
                worksheet.write('I1', 'uploads', bold)
                worksheet.write('J1','following',bold)
                worksheet.write('K1', 'external_url', bold)
                worksheet.write('L1', 'email', bold)
                worksheet.write('M1', 'UID', bold)
                row = 1
                col = 0
                for items in finalOutput:
                    lst1 = items['each_followers_data']
                    lst2 = items['self_user_info']
                    for second_items in lst2:
                        self_user_info = second_items
                        for mini_s_items in self_user_info:
                                worksheet.write_string(row,col,str(self_user_info['username']))
                                worksheet.write_string(row,col+1,str(self_user_info['bio'].encode('ascii','ignore')))
                                worksheet.write_string(row,col+2,str(self_user_info['snapchat']))
                                worksheet.write_string(row,col+3,str(self_user_info['verified']))
                                try:
                                    worksheet.write_string(row+1,col+4, str(self_user_info['name'].encode('ascii','ignore')))
                                except:
                                    pass
                                worksheet.write_string(row,col+5,str(self_user_info['url']))
                                worksheet.write_string(row,col+6,str(self_user_info['private']))
                                worksheet.write_string(row,col+7,str(self_user_info['followers']))
                                worksheet.write_string(row,col+8,str(self_user_info['uploads']))
                                worksheet.write_string(row,col+9,str(self_user_info['following']))
                                worksheet.write_string(row,col+10,str(self_user_info['external_url']))
                                worksheet.write_string(row,col+11,str(self_user_info['email']))
                                worksheet.write_string(row,col+12,str(self_user_info['UID']))
                    for items in lst1:
                        each_items = items
                        for mini_items in each_items:
                                try:
                                    worksheet.write_string(row+1,col,str(mini_items['username']))
                                except:
                                    pass
                                try:
                                    worksheet.write_string(row+1,col+1,str(mini_items['bio'].encode('ascii','ignore')))
                                except:
                                    pass
                                try:
                                    worksheet.write_string(row+1,col+2,str(mini_items['snapchat']))
                                except:
                                    pass
                                try:
                                    worksheet.write_string(row+1,col+3,str(mini_items['verified']))
                                except:
                                    pass
                                try:
                                    worksheet.write_string(row+1,col+4, str(mini_items['name'].encode('ascii','ignore')))
                                except:
                                    pass
                                worksheet.write_string(row+1,col+5,str(mini_items['url']))
                                worksheet.write_string(row+1,col+6,str(mini_items['private']))
                                worksheet.write_string(row+1,col+7,str(mini_items['followers']))
                                worksheet.write_string(row+1,col+8,str(mini_items['uploads']))
                                worksheet.write_string(row+1,col+9,str(mini_items['following']))
                                worksheet.write_string(row+1,col+10,str(mini_items['external_url']))
                                try:
                                    worksheet.write_string(row+1,col+11,str(mini_items['email']))
                                except:
                                    pass
                                worksheet.write_string(row+1,col+12,str(mini_items['UID']))
                                row +=1
                # workbook.close()
                # output.seek(0)
                # response = make_response(output.read())
                # sleep(20)
                # response.headers['Content-Disposition'] = "attachment; filename=output.csv"
                # return response
                return "work is still on progress... Visit /csv/ "+name
            except:
                pass
@app.route('/csv/<path:filename>', methods=['GET', 'POST'])
def download(filename):    
    return send_from_directory(directory='pdf', filename=filename)

@app.route('/instagram/backend/<name>')
def igbackendWorker(name):
    instagram = InstagramMain.delay(name)
    task_id = instagram.task_id
    add_data = InstagramResult(task_id=task_id,ig_name=name)
    db.session.add(add_data)
    db.session.commit()
    return "Added to queue!"

@app.route('/instagram/<name>/result')
def GenerateResult(name):
    queryName = InstagramResult.query.filter_by(ig_name=name).first()
    task_id = queryName.task_id
  #  v = cache.get('celery-task-%s' % session.get('task_id'))
    # if v:
    #     print v
    res = AsyncResult(task_id)
    if "True" in str(res.ready()):
        return res.get()
    else:
        return "Query is still being processed! Please wait! status:" + str(res.ready())

@app.route('/outreach/<query>/results')
def FinalResults(query):
    queryResults = Result.query.filter_by(query=query).first()
    task_id = queryResults.task_id
    res = AsyncResult(task_id)
    if "True" in res.ready():
        return jsonify(results=res.get())
    else:
        return "Query is still being processed! Please wait! status:" + str(res.ready())




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
        try:
            actualItem = LoadAsJson['answers'][0]['webResults']
            appendArr.append(actualItem)
        except:
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
                response = requests.get('http://104.131.43.184/whois/'+str(fixedDomain)).text
                loadAsJson = json.loads(response)
                whoisDictionary = {}
                try:
                    whoisDictionary['domain_name'] = loadAsJson['domain_name']
                except:
                    whoisDictionary['domain_name'] = "None"
                try:
                    whoisDictionary['whois_full_name'] = loadAsJson['registrant']['name']
                except:
                    whoisDictionary['whois_full_name'] = "None"
                try:
                    whoisDictionary['whois_city_name'] = loadAsJson['registrant']['city_name']
                except:
                    whoisDictionary['whois_city_name'] = "None"
                try:
                    whoisDictionary['whois_country_code'] = loadAsJson['registrant']['country_code']
                except:
                    whoisDictionary['whois_country_code'] = "None"
                try:
                    whoisDictionary['whois_email_address'] = loadAsJson['registrant']['email']
                except:
                    whoisDictionary['whois_email_address']="None"
                try:
                    whoisDictionary['whois_phone_number'] = loadAsJson['registrant']['phone_number']
                except:
                    whoisDictionary['whois_phone_number'] = "None"
                print whoisDictionary
                miniArz.append(whoisDictionary)
                bingDictionary['whoisData'] = miniArz
                rearr.append(bingDictionary)
            except KeyError,RuntimeError:
                pass
    return rearr
   
if __name__ == '__main__':
    app.run()





