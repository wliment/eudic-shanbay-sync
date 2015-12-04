#! /usr/bin/env python
#coding:utf-8


import sys
import re
import urllib2
import urllib
import requests
import cookielib
import json
from shanbay import API

## 这段代码是用于解决中文报错的问题  
reload(sys)  
sys.setdefaultencoding("utf8")  
#####################################################
loginurl = 'http://dict.eudic.net/Account/Login?returnUrl='
logindomain = 'eudic.net'

class dict_app(object):

    def __init__(self):
        self.name = ''
        self.passwprd = ''
        self.domain = ''

        self.cj = cookielib.LWPCookieJar()            
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj)) 
        urllib2.install_opener(self.opener)    

    def setLoginInfo(self,username,password):
        '''设置用户登录信息'''
        self.name = username
        self.pwd = password
        self.domain = domain

    def login(self):
        '''登录网站'''
        #loginparams = {'domain':self.domain,'UserName':self.name, 'Password':self.pwd}
        try:
            loginparams = {'domain':self.domain,'UserName':self.name, 'Password':self.pwd,'returnUrl':'',"RememberMe":"true"}
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'}
            req = urllib2.Request(loginurl, urllib.urlencode(loginparams),headers=headers)  
            response = urllib2.urlopen(req)
            self.operate = self.opener.open(req)
            thePage = response.read()        
        except urllib2.HTTPError: 
            print "eudit login error pleare check your's account username and password"
            sys.exit()
        #print thePage
    
    #删除单词
    # 请求头部需要设置内容长度
    #wordid   examplx aa,bb,cc,ee
    def delete_word(self,word_id):
        url="http://dict.eudic.net/StudyList/Edit"
        par = 'oper=del&id='+reduce(lambda x,y:x+','+y,word_id)
        print par
        headers = {'Content-Length':len(par),'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8','User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'}
        req = urllib2.Request(url,par, headers=headers)  
        response = urllib2.urlopen(req)
        self.operate = self.opener.open(req)
        thePage = response.read()        
        print "delete finish"

    #get all new words from service
    def get_word_by_num(self,num):
        en_words={}
        page,rows=1,num
        #eudic 这个连接是不限制单页取词数的
        data=urllib2.urlopen("http://dict.eudic.net/StudyList/GridData?catid=&_search=false&nd=1426850560615&rows=%s&page=%s&sidx=&sord=asc"%(str(rows),str(page)))
        json_data= json.loads(data.read())
        #print json_data
        words= json_data["rows"]
        for word in words:
            w_id  = word["id"]
            d=word["cell"][1].decode("unicode-escape")
            d = re.sub('<[^<]+?>', '', d)
            en_words[w_id]=d
        return en_words

#shanbay class
class shanbay_study():
    def __init__(self,client_id):
        self.client_id = client_id
        f=open("token.json","r")
        self.token=json.loads(f.read())
        f.close()
        self.api=None
        self.search_words=[]
        
    
    def connect(self): 
        self.api = API(self.client_id,self.token)

    def batch_add_search_words(self,words):
        not_found_word=[]
        added_word=[]
        if   self.api and len(words) != 0:
            for word in words:
                word_search = self.api.word(word)
                # there is no need add word  had been added
                if word_search["msg"] == 'SUCCESS' and  ('learning_id' not in word_search['data']):
                    result=self.api.add_word(word_search["data"]["id"])
                    print result
                    if result['msg'] == 'SUCCESS':
                        print "%s add word success " % word
                    else:
                        print "%s add word faile " % word

                elif word_search["msg"] != 'SUCCESS' :
                    print " %s add word faile  add to no_result_word" % word 
                    not_found_word.append(word)
                elif word_search["msg"] == 'SUCCESS' and  ('learning_id'  in word_search['data']):
                    print " %s  had been added befor ,overleap it" % word 
                    added_word.append(word)

        else:
            print "api has not init\n"
            sys.exit()
        return (not_found_word,added_word) 



    
if __name__ == '__main__': 	 
    if len(sys.argv) != 4:
        print 'need eudic account info for sync(http://dict.eudic.net/)'
        print 'Usage: python word.py username passwd  wordnum'
        print 'the wordnum is the number you want sync to shanbay'
        print 'warring the word will be delete when the word sync succesful'
        exit(1)
    eudict_app = dict_app()
    username = sys.argv[1]  #wrong account username will make a error
    password = sys.argv[2]
    sync_num = int(sys.argv[3])
    domain = logindomain
    eudict_app.setLoginInfo(username,password)
    eudict_app.login()
    shanbay_app = shanbay_study("42e61b1dfa3df66c783e") # init must set shanbay clinet_Id
    shanbay_app.connect()

    #eudict_app.delete_word("1111")
    en_words = eudict_app.get_word_by_num(2)
    for i in en_words:
        print i +" " +en_words[i]
    word_not_found,word_added=shanbay_app.batch_add_search_words(en_words.values())
    print word_not_found
    delete_word = [ x for  x ,y in en_words.items() if y not in word_not_found and y in word_added]
    print delete_word
    eudict_app.delete_word(delete_word)
