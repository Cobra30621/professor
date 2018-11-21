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

line_bot_api = LineBotApi('qxQIS8TTitqfZkp4+wuHQCe+pEWKskFrxr/jRB8mRMjaEr5EHgZKKwWC1MX+UUy6sbqD1Gbr299QTpplU3idbEBBTGs/LQZGG6dHCUnvK7Fs8my2hCIwYPlw92p/W+Vs97wZQQASgXsVT6/oADxNNQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('258c64afe44ab5ed8e041a75f88fcf27')



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
#關鍵評論網
            
    if re.search('theNewLens', event.message.text, re.IGNORECASE):
     
        columns = []
        img = 'https://image3.thenewslens.com/assets/web/cover-photo-medium.png'

        carousel = CarouselColumn(
                    thumbnail_image_url = img,
                    title = '關鍵評論網新聞',
                    text = '點擊觀看類型',
                    actions=[
                        MessageTemplateAction(
                            label='科學',
                            text='關鍵評論科學'
                           ),
                        MessageTemplateAction(
                            label='商業',
                            text='關鍵評論商業'
                           ),
                        MessageTemplateAction(
                            label='職場',
                            text='關鍵評論職場'
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
            
    
    
    if re.search('關鍵評論科學', event.message.text, re.IGNORECASE):
        dic = corwler.theNewLens('science')
        
        makeCard(dic, event)
        return 0 
    
    if re.search('關鍵評論商業', event.message.text, re.IGNORECASE):
        dic = corwler.theNewLens('business')
        
        makeCard(dic, event)
        return 0 
    
    if re.search('關鍵評論職場', event.message.text, re.IGNORECASE):
        dic = corwler.theNewLens('career')
        
        makeCard(dic, event)
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