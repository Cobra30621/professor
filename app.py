# -*- coding: utf-8 -*-
"""
Created on Fri Aug 24 18:12:45 2018

@author: linzino
"""
# server-side
from flask import Flask, request, abort

# line-bot
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *

# package
import re
from datetime import datetime 

# customer module
import mongodb
import corwler


app = Flask(__name__)

line_bot_api = LineBotApi('dCdBEwGwdWUxethKTVf5nZX8CMpaY7zU0k44dvBp9V8S6iacj3LZWUSx9DG0WuXxbGBaU6I5QjoOilzZ1WOeiuF4vQY0nzbzSyhoGh/UE3uUD7HBW6b3JUu2mWAp2s/i+dLBcv2e/eGasmUYYOwRAgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('43f859131a0ee481594c57358b4d330e')



@app.route("/callback", methods=['POST'])
def callback():

    
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(FollowEvent)
def handle_follow(event):
    '''
    當使用者加入時觸動
    '''
    # 取得使用者資料
    profile = line_bot_api.get_profile(event.source.user_id)
    name = profile.display_name
    uid = profile.user_id
    
    print(name)
    print(uid)
    # Udbddac07bac1811e17ffbbd9db459079
    if mongodb.find_user(uid,'users')<= 0:
        # 整理資料
        dic = {'userid':uid,
               'username':name,
               'creattime':datetime.now(),
               'Note':'user',
               'ready':0}
        
        mongodb.insert_one(dic,'users')
   
def makeCard(dic, event):
    dic = dic

    columns = []
    for i in range(3):
        carousel = CarouselColumn(
                    thumbnail_image_url = dic[i]['img'],
                    title = dic[i]['title'],
                    text = dic[i]['summary'],
                    actions=[
                        URITemplateAction(
                            label = '點我看新聞',
                            uri = dic[i]['link']
                          )
                        ]
                    )
        columns.append(carousel)
    
    remessage = TemplateSendMessage(
                alt_text='Carousel template',
                template=CarouselTemplate(columns=columns)
                )
    
    
    line_bot_api.reply_message(event.reply_token, remessage)      

def makeCard2(image, title, text, label, link, event):

    columns = []
    for i in range(3):
        carousel = CarouselColumn(
                    thumbnail_image_url = image[i],
                    title = title[i],
                    text = text[i],
                    actions=[
                        URITemplateAction(
                            label = label[i],
                            uri = link[i]
                          )
                        ]
                    )
        columns.append(carousel)
    
    remessage = TemplateSendMessage(
                alt_text='Carousel template',
                template=CarouselTemplate(columns=columns)
                )
    
    
    line_bot_api.reply_message(event.reply_token, remessage)         

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    '''
    當收到使用者訊息的時候
    '''
    profile = line_bot_api.get_profile(event.source.user_id)
    name = profile.display_name
    uid = profile.user_id
    message = event.message.text
    print(name)
    print(uid)
    print(message)
    
    dic = {'userid':uid,
       'username':name,
       'creattime':datetime.now(),
       'mess':message}
    mongodb.insert_one(dic,'message')
    
    if mongodb.get_ready(uid,'users') ==1 :
        mongodb.update_byid(uid,{'ready':0},'users')
        casttext = name+' 對大家說： '+message
        remessage = TextSendMessage(text=casttext)
        userids = mongodb.get_all_userid('users')
        line_bot_api.multicast(userids, remessage)
        return 0 


    if message == '群體廣播':
        # 設定使用者下一句話要群廣播
        mongodb.update_byid(uid,{'ready':1},'users')
        remessage = TextSendMessage(text='請問要廣播什麼呢?')
        line_bot_api.reply_message(
                        event.reply_token,
                        remessage)
        return 0 
    
    if re.search('Hi|hello|你好|ha', message, re.IGNORECASE):
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))
        
        return 0 
#特殊能力

    if re.search('特殊能力', event.message.text, re.IGNORECASE):

        image = ['https://i.imgur.com/uM5Xj2W.jpg','https://i.imgur.com/uM5Xj2W.jpg','https://i.imgur.com/uM5Xj2W.jpg']
        title = ['APCS實作題成績：第三級','扯鈴表演','巴哈姆特寫小說心得文']
        text = ['本人在「大學程式設計先修檢測」APCS實作題中，拿下三級分。為1246個考生中的前15.6%。','國小為扯鈴社社長，畢業後以校友的身份進行扯鈴教學、表演。','閱讀超過2000本小說，並常於巴哈姆特寫小說推薦文。']
        label = ['成績證明','表演影片','我的小屋']
        link = ['https://upload.cc/i1/2018/11/23/lhXGLv.png','https://www.google.com','https://home.gamer.com.tw/creation.php?owner=s10530032']
        
        
        makeCard2(image, title, text, label, link, event)
        return 0 

#推薦課程與展覽

    if re.search('推薦課程與展覽', event.message.text, re.IGNORECASE):

        image = ['https://i.imgur.com/uM5Xj2W.jpg','https://upload.cc/i1/2018/11/23/YCVQqc.png','https://upload.cc/i1/2018/11/23/o0Qs5y.png']
        title = ['科技未來展','第二屆-用Python打造自己的股票小秘書','黑心外匯交易員的告白']
        text = ['以生技、醫材、AI為主題的展覽。我覺得最猛的科技有量子電腦、干擾性RNA藥物用於治療近視等等。','教你製作可以開盤前自動寄送符合條件的股票到手機的股票小秘書。','不用一直看盤，不會因為賠錢而影響心情，以身活為重的投資術。每天只要20分鐘，就能得到穩定收入。']
        label = ['影片介紹','課程連結','課程連結']
        link = ['https://www.youtube.com/watch?v=5_TJWELuS1U','https://tmrgood.kktix.cc/events/stockbot2','https://coahing.mpg668.com/trade-j/?utm_source=FB&utm_medium=post&utm_campaign=20181113']
        
        
        makeCard2(image, title, text, label, link, event)
        return 0 

#介紹自己

    if re.search('介紹自己', event.message.text, re.IGNORECASE):

        image = ['https://i.imgur.com/uM5Xj2W.jpg','https://i.imgur.com/uM5Xj2W.jpg','https://i.imgur.com/uM5Xj2W.jpg']
        title = ['APCS實作題成績：第三級','11','11']
        text = ['本人在「大學程式設計先修檢測」APCS實作題中，拿下三級分。為1246個考生中的前15.6%。','','']
        label = ['點我','點我','點我']
        link = ['https://www.google.com','https://www.google.com','https://www.google.com']
        
        
        makeCard2(image, title, text, label, link, event)
        return 0 

#科技報橘
        
    if re.search('科技報橘', event.message.text, re.IGNORECASE):
     
        columns = []
        img = 'https://asia.money2020.com/sites/asia.money2020.com/files/Tech-orange360.png'

        carousel = CarouselColumn(
                    thumbnail_image_url = img,
                    title = '科技報橘新聞',
                    text = '點擊觀看類型',
                    actions=[
                        MessageTemplateAction(
                            label='創新創業',
                            text='tech創新創業'
                           ),
                        MessageTemplateAction(
                            label='人工智慧',
                            text='tech人工智慧'
                           ),
                        MessageTemplateAction(
                            label='數位行銷',
                            text='tech數位行銷'
                           )

                         ]
                     )
        columns.append(carousel)

        
        remessage = TemplateSendMessage(
                    alt_text='Carousel template',
                    template=CarouselTemplate(columns=columns)
                    )
        
        
        line_bot_api.reply_message(event.reply_token, remessage)
        return 0         
            
    
    if re.search('tech創新創業', event.message.text, re.IGNORECASE):
        dic = corwler.techorange('創新創業/')
        
        makeCard(dic, event)
        return 0 
    
    if re.search('tech人工智慧', event.message.text, re.IGNORECASE):
        dic = corwler.techorange('artificialintelligence/')
        
        makeCard(dic, event)
        return 0 
    
    if re.search('techorange新經濟', event.message.text, re.IGNORECASE):
        dic = corwler.techorange('新經濟/')
        
        makeCard(dic, event)        
        return 0 
    
    if re.search('techorange數位轉型', event.message.text, re.IGNORECASE):
        dic = corwler.techorange('數位轉型/')
        
        makeCard(dic, event)
        return 0 
    
    if re.search('techorange', event.message.text, re.IGNORECASE):
        dic = corwler.techorange('')
        
        makeCard(dic, event)
        return 0 
    
    if re.search('tech數位行銷', event.message.text, re.IGNORECASE):
        dic = corwler.techorange('software_digimarketing/')
        
        makeCard(dic, event)
        return 0 
    

if __name__ == '__main__':
    app.run(debug=True)