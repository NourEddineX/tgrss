import re
import logging
import requests
import lxml.html
from flask import Flask, render_template, jsonify, Response

def check_tgid(tgid):
    try:
        tgid = tgid.lower()
        for char in tgid:
            if char not in 'abcdefghijklmnopqrstuvwxyz0123456789_':
                return False
        return True
    except Exception as e:
        logging.error(e) 
        return False

def tglink2weblink(text):
    text = lxml.html.fromstring(text)
    for elem in text.xpath('.//*[contains(@href,"https://t.me/")]'):
            elem.attrib['href'] = elem.attrib['href'].replace('https://t.me/','https://t.me/s/')
    return lxml.html.tostring(text).decode('utf-8')

def image_url(img):
    if img is str:
        elem = lxml.html.fromstring(img)
    else:
        elem = img
    x = elem.xpath('.//a[contains(@style,"background-image:url")]/@style')[0]
    rgxp = re.compile('http[s]?://cdn[0-9.][.]telesco\.pe/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    rgxp = re.compile('http[s]?://cdn[0-9.][.]telesco\.pe/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    span = tuple(rgxp.finditer(x))[0].span()
    url = x[span[0]:span[1]]
    if url.endswith("')"):
        url = url[:-2]
    return '<img src="%s"></img>' % url

def scrape_msg(msg):
    try:
        text = msg.xpath('.//div[@class="tgme_widget_message_text js-message_text"]')[0]
        text = lxml.html.tostring(text).decode('utf-8')
    except IndexError:
        text = '<br>'
    try:
        new = msg.xpath('.//a[contains(@class,"tgme_widget_message_reply")]')[0]
        new = lxml.html.tostring(new).decode('utf-8')
        text = new + '<br>' + text
    except IndexError:
        pass
    try:
        new = msg.xpath('.//div[contains(@class,"tgme_widget_message_forwarded_from")]')[0]
        new = lxml.html.tostring(new).decode('utf-8')
        text = text + '<br>' + new
    except IndexError:
        pass
    try:
        new = msg.xpath('.//div[contains(@class,"tgme_widget_message_poll")]')[0]
        new = lxml.html.tostring(new).decode('utf-8')
        text = text + '<br>' + new
    except IndexError:
        pass
    try:
        new = msg.xpath('.//a[contains(@class,"tgme_widget_message_video_player")]')[0]
        new = lxml.html.tostring(new).decode('utf-8')
        text = text + '<br>' + new
    except IndexError:
        pass
    try:
        new = msg.xpath('.//a[contains(@class,"tgme_widget_message_document_wrap")]')[0]
        filename = new.xpath('.//div[contains(@class,"tgme_widget_message_document_title")]/text()')[0]
        extra = new.xpath('.//div[contains(@class,"tgme_widget_message_document_extra")]/text()')[0]
        text = text + '<br>' + 'File: %s , Size: %s' % (filename, extra)  
    except IndexError:
        pass
    try:
        img = msg.xpath('.//a[contains(@class,"tgme_widget_message_photo_wrap")]')[0]
        text = text + image_url(msg)
    except IndexError:
        img = None
    text = tglink2weblink(text)
    try:
        views = msg.xpath('.//span[contains(@class,"tgme_widget_message_views")]/text()')[0]
    except IndexError:
        views = None
    date_time = msg.xpath('.//a[@class="tgme_widget_message_date"]/time/@datetime')[0]
    hr_time = ' '.join(date_time.split('+')[0].split('T'))
    url = msg.xpath('.//a[@class="tgme_widget_message_date"]/@href')[0]
    url = url.replace('https://t.me/','https://t.me/s/')
    return (text,views,url,date_time,hr_time)

def scrape_channel(tgid):
    tgid = tgid.lower()
    channel_url = 'https://t.me/s/'+tgid
    try:
        r = requests.get(channel_url, allow_redirects=False)
    except Exception as e:
        logging.error(e)
    if r.status_code != 200:
        return False
    doc = lxml.html.fromstring(r.content)
    msgs = doc.xpath('//*/div[@class="tgme_widget_message_bubble"]')
    channel_name = doc.xpath('//*/div[@class="tgme_header_title"]/text()')[0]
    channel_members = doc.xpath('//*/div[@class="tgme_header_counter"]/text()')[0]
    try:
        channel_bio = doc.xpath('//*/div[@class="tgme_channel_info_description"]/text()')[0]
    except IndexError:
        channel_bio = None
    return ( channel_name, channel_members, channel_url, tuple([scrape_msg(msg) for msg in msgs]) )

app = Flask(__name__)

@app.route('/')
def index():
    return 'Usage: GET /durov -> https://t.me/durov as RSS feed'

@app.route('/<tgid>')
def tgfeed(tgid):
    if not check_tgid(tgid):
        return jsonify('Bad @name'), 404
    data = scrape_channel(tgid)
    if not data:
        return jsonify('Not a channel'), 404
    feed = render_template('rss.xml',channel_name=data[0],channel_members=data[1],channel_url=data[2],msgs=data[3])
    return Response(feed,mimetype='text/xml')

if __name__ == '__main__':
    app.run(port=1234,host='0.0.0.0')
