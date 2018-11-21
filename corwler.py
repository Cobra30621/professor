# -*- coding: utf-8 -*-
"""
Created on Sat Aug 25 00:17:32 2018

@author: linzino
"""
import requests #引入函式庫
from bs4 import BeautifulSoup
import re
import json
import feedparser


def udn_news():
    '''
    抓最新前三篇新聞
    
    回傳是一個dict
    '''
    rss_url = 'https://udn.com/rssfeed/news/2/6638?ch=news'
 
    # 抓取資料
    rss = feedparser.parse(rss_url)
    
    cards = []    
    for index in range(0,3):
        # 抓文章標題
        title = rss['entries'][index]['title']
        # 抓文章連結
        link = rss['entries'][index]['link']
        # 處理摘要格式
        summary =  rss['entries'][index]['summary']
        
        if 'img' in summary:
            soup = BeautifulSoup(summary, 'html.parser')
            p_list = soup.find_all('p')
            # 抓文章摘要 限制只有60個字
            text = p_list[1].getText()[:50]
            # 抓文章圖片
            image = p_list[0].img['src']
        else:
            # 沒有圖片
            text = summary[:50]
            image = 'https://i.imgur.com/vkqbLnz.png'
        
        card = {'title':title,
                'link':link,
                'summary': text,
                'img':image
                }
        cards.append(card)
        
    return cards




def techorange(newType):
    '''
    在techorangeAi 上某個關鍵字最新的文章
    '''
    newType = newType
    url = 'https://buzzorange.com/techorange/tag/' + newType
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    atags = soup.select('.entry-title')

    cards = []
    for index in range(3):    
        #文章標題

        title = atags[index].text[:40]
        
        #文章內文
        interUrl = atags[index].a['href']
        interResp = requests.get(interUrl)
        interSoup = BeautifulSoup(interResp.text, 'html.parser')
        interAtags = interSoup.select('.entry-content')
        text = interAtags[0].text.replace('\n', '')[:50]

        
        #文章連結
        link = interUrl
        
        #圖片
        img = interSoup.find_all('img', re.compile('align'))
        image = img[1]['src']   
        
        card = {'title':title,
                    'link':link,
                    'summary': text,
                    'img':image
                    }
        cards.append(card)
 
    
    return cards
    


def theNewLens(newType):
    '''
    搜尋關鍵評論網（theNewLens）的科學文章，做成字卡
    '''
    newType = 'career'
    url = 'https://www.thenewslens.com/category/' + newType
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')

    titles = soup.select('.title')
    texts = soup.select('.description')  
    links = soup.select('.img-box') 
    images = soup.select('.lazy-container') 

    cards = []

    for index in range(3):
        #文章標題
        title = titles[index].text[:40]
        
        #文章連結
        link = links[index].a['href']
        
        #文章內文
        text = texts[index].text[:50] 
        
        #圖片
        image = re.findall(r'(https.*?)\d{3,}w',str(images[index]))[2]
        #b = re.findall('350w,[\S]*400w',str(images[0]))
        
        
        
        card = {'title':title,
                        'link':link,
                        'summary': text,
                        'img':image
                        }
        cards.append(card)

    return cards



def fb():
    '''
    搜尋關鍵評論網（theNewLens）的科學文章，做成字卡
    '''
    url = 'https://www.facebook.com/chasedrea?__tn__=%2CdC-R-R&eid=ARDnjjnJesfZGk4eRSXvv3mzSi9A3t5sZ3KokokeDUJH-COyd6dwjMdjxYTfsMjVQ3GygfVOZrgr54r-&hc_ref=ARRXWEZo5GRi3kCiaSIvgsDW0gdAdO5hexa2T6cM3rpCfCRPAtEiepFoBKhi_kNLLT8&fref=nf'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    atags = soup.find_all('div', re.compile('_26ni hidden_elem img'))

    
    cards = []
    for index in range(3):
        #文章標題
        title = atags2[index].a['title']
        
        #文章連結
        link = atags2[index].a['href']
        
        #文章內文
        textlist = atags[index].find_all('div', re.compile('description'))
        text = str(textlist[0])
        text = text.replace('<div class="description"> ', '')[:50] 
        
        #圖片
        
        imglist = str(atags2[index].a.div.img).split(',')
        imglist = imglist[2].split(' ')
        image = imglist[1]
        
        
        card = {'title':title,
                        'link':link,
                        'summary': text,
                        'img':image
                        }
        cards.append(card)

    return cards


