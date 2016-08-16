#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
api:
stock detail: http://api.money.126.net/data/feed/0600749,money.api
search stock: http://quotes.money.163.com/stocksearch/json.do?type=&count=10&callback=Baidu.Finance.Suggest.GetResult&word=zpgf
"""

import sys
import os
import time
import urllib2
import json
import gzip
import cStringIO

default_list = ['000001', '600749', '002325', '603883']
referer = 'http://www.hao123.com/stocknew'

def create_request(url, referer = None):
    req = urllib2.Request(
        urllib2.quote(url.split('#')[0].encode('utf8'), safe = "%/:=&?~#+!$,;'@()*[]"), 
        headers = {"Accept": "application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5",
                   "Accept-Charset": "GBK,utf-8;q=0.7,*;q=0.3",
                   "Accept-Encoding": "gzip",
                   "Accept-Language": "zh-CN,zh;q=0.8",
                   "Cache-Control": "max-age=0",
                   "Connection": "keep-alive",
                   "User-Agent": "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.106 Safari/535.2",
        })
    
    if referer is not None: 
        req.add_header('Referer', referer)
    return req

def show_help():
    print "Usage:"
    print "python ./stock.py -h[--help] show this help"
    print "python ./stock.py            show default stock's quotation"
    print "python ./stock.py -c 000001  show specify stock's quotation"
    print "python ./stock.py -s gyyh    search the no of stock by short name"
    sys.exit()

def get_stock(stock_list):
    request_time = time.ctime()
    stock_str = ','.join(stock_list)
    api_url = "http://api.money.126.net/data/feed/%s,money.api" % stock_str
    f = urllib2.urlopen(create_request(api_url, referer), timeout=15)
    data = f.read()
    if data[:6] == '\x1f\x8b\x08\x00\x00\x00':
        data = gzip.GzipFile(fileobj = cStringIO.StringIO(data)).read()
    f.close()

    if data is not None:
        json_data = data[(data.index('(') + 1): -2]
        json_list = json.loads(json_data)

        print request_time
        for i in json_list:
            stock = json_list[i]
            symbol = stock['symbol'].encode('utf-8')
            name = stock['name'].encode('utf-8')
            price = stock['price']
            updown = stock['updown']
            percent = stock['percent']
            arrow = stock['arrow']
            percent = str(round((100 * percent), 2)) + "%"
            print symbol, "\t", price, "\t", updown, "\t", percent, "\t", arrow

def search_stock(short_name):
    api_url = "http://quotes.money.163.com/stocksearch/json.do?type=&count=10&callback=Baidu.Finance.Suggest.GetResult&word=%s" % short_name
    f = urllib2.urlopen(create_request(api_url, referer), timeout=15)
    data = f.read()
    if data[:6] == '\x1f\x8b\x08\x00\x00\x00':
        data = gzip.GzipFile(fileobj = cStringIO.StringIO(data)).read()
    f.close()

    if data is not None:
        json_data = data[(data.index('(') + 1): -1]
        json_list = json.loads(json_data)

        for stock in json_list:
            symbol = stock['symbol'].encode('utf-8')
            name = stock['name'].encode('utf-8')
            print symbol, "\t", name

if __name__ == '__main__':
    if (len(sys.argv) > 1 and (sys.argv[1] == '-h' or sys.argv[1] == '--help')):
        show_help()

    if len(sys.argv) > 1:
        # search stock by short name
        if sys.argv[1] == '-s' and sys.argv[2].isalpha():
            search_stock(sys.argv[2])
            sys.exit()
        # get current quotation of specify stock
        if sys.argv[1] == '-c' and sys.argv[2].isdigit():
            daemon = False
            stocks = []
            stocks.append(sys.argv[2])
        else:
            show_help()
    else:
        daemon = True
        stocks = default_list
        stocks.reverse()

    stock_list = []
    for stock in stocks:
        if stock[:6] == '000001':
            stock_list.append('0' + stock)
        elif stock[0] == '6':
            stock_list.append('0' + stock)
        else:
            stock_list.append('1' + stock)

    if daemon is True:
        while True:
            get_stock(stock_list)
            print os.linesep*20
            time.sleep(2)
    else:
        get_stock(stock_list)
