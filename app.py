import json
import time
import requests
import schedule
import threading
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__) 
baaab, flyingSeed = [], [] 

def howsTheWeather():
    global flyingSeed 
    weatherList = {'Thunderstorm' : '천둥번개가 쳐요.', 'Drizzle' : '비가 와요.', 'Rain' : '비가 와요.', 'Snow' : '눈이 와요', 'Clear' : '맑아요.', 'Clouds' : '흐려요.' } 
    
    req = requests.get('https://api.openweathermap.org/data/2.5/weather?id=1835553&APPID=714bbbb9ad184e11c835635e025e301d') 
    data = json.loads(req.text) 
    
    flyingSeed.append(weatherList[data['weather'][0]['main']])
    flyingSeed.append(data['main']['temp'])
    flyingSeed.append(data['main']['humidity'])
    flyingSeed.append(data['wind']['speed'])
    flyingSeed.append(data['sys']['sunrise'])
    flyingSeed.append(data['sys']['sunset'])
    
def yogiyo():
    global baaab 
    
    headers = {
        'Host':  'mportal.ajou.ac.kr',
        'Connection':  'keep-alive',
        'Content-Length':  '32',
        'Accept':  'application/json, text/plain, */*',
        'Origin':  'http://mportal.ajou.ac.kr',
        'User-Agent':  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3846.0 Safari/537.36',
        'Sec-Fetch-Mode':  'cors',
        'Content-Type':  'application/json;charset=UTF-8',
        'Sec-Fetch-Site':  'same-origin',
        'Referer' : 'http://mportal.ajou.ac.kr/main.do',
        'Accept-Encoding':  'gzip, deflate, br',
        'Accept-Language':  'en-US,en;q=0.9,ko;q=0.8,de;q=0.7'
    }
    
    for i in range(0, 3):
        payload = '{"tabIndex":' + str(i) + ',"date":"' + datetime.today().strftime('%Y%m%d') + '"}'
        
        s = requests.Session()
        content = s.post('http://mportal.ajou.ac.kr/portlet/p018/p018Text.ajax', data=payload, headers=headers)
        content = json.loads(content.text) 
        
        hungry = {'morningText' : '아침', 'launchText' : '점심', 'dinnerText' : '저녁'} 
        baaab.append([]) 
        
        if not content['p018Text'] is None: 
            for txt in hungry.keys(): 
                menu = content['p018Text'][txt] 
                if menu is None : menu = "" 
                menu = menu.replace('\r', '\n').replace('</br>', '') 
                if menu : baaab[i].append({hungry[txt] : menu}) 
        
        else : baaab[i].append({'메뉴' : '없음'}) 

@app.route('/message', methods=['POST']) 
def Message():
    
    content = request.get_json()
    content = content['userRequest']['utterance']
    
    if content == u'밥':
        payload = {
            'version' : '2.0',
            'template' : {
                'outputs' : [{
                  'simpleText' : { 'text' : '어느 식당으로 가실래요?' }  
                }],
                'quickReplies' : [{
                        'messageText' : '학생식당',
                        'action' : 'message',
                        'label' : '학생식당'
                    }, {
                        'messageText' : '기숙사식당',
                        'action' : 'message',
                        'label' : '기숙사식당'
                    }, {
                        'messageText' : '교직원식당',
                        'action' : 'message',
                        'label' : '교직원식당'
                    }
                ]
            }
        }
        
    elif content == u'학생식당':
        
        string = ''
        for content in baaab[0]:
            for item in content.keys():
                string += item + '\n' + content[item] + '\n\n'
                
        payload = {
            'version' : '2.0',
            'template' : {
                'outputs' : [{
                  'simpleText' : { 'text' : string.rstrip() }
                }]
            }
        }
        
    elif content == u'기숙사식당':
        string = ''
        for content in baaab[1]:
            for item in content.keys():
                string += item + '\n' + content[item] + '\n\n'
                
        payload = {
            'version' : '2.0',
            'template' : {
                'outputs' : [{
                  'simpleText' : { 'text' : string.rstrip() }
                }]
            }
        }
        
    elif content == u'교직원식당':
        string = ''
        for content in baaab[2]:
            for item in content.keys():
                string += item + '\n' + content[item] + '\n\n'
                
        payload = {
            'version' : '2.0',
            'template' : {
                'outputs' : [{
                  'simpleText' : { 'text' : string.rstrip() }
                }]
            }
        }
    
    elif content == u'날씨':
        string = '지금 아주대학교는 ' + flyingSeed[0] + '\n'
        string += '기온은 ' + str(round(flyingSeed[1] - 273.15, 1)) + '°C로 ' + ('따뜻합니다.' if (float(flyingSeed[1]) > 20) else '쌀쌀합니다') + '\n'
        string += '습도는 ' + str(flyingSeed[2]) + '%이고, ' + str(flyingSeed[3]) + 'm/s로 바람이 불고 있어요.\n'
        string += '오늘 아주대학교에선 해가 ' + datetime.fromtimestamp(int(flyingSeed[4])).strftime('%H시 %M분') + '에 떠서 '
        string += datetime.fromtimestamp(int(flyingSeed[5])).strftime('%H시 %M분') + '에 질 거에요.'
            
        payload = {
            'version' : '2.0',
            'template' : {
                'outputs' : [{
                  'simpleText' : { 'text' : string }  
                }]
            }
        }
        
    elif content == u'길찾기':
        payload = {
            'version' : '2.0',
            'template' : {
                'outputs' : [{
                  'simpleText' : { 'text' : 'test rcv OK' }  
                }]
            }
        }
    
    else :
        payload = {
            'version' : '2.0',
            'template' : {
                'outputs' : [{
                  'simpleText' : { 'text' : '이해하지 못했습니다.\n무엇을 물어보실래요?' }  
                }],
                'quickReplies' : [{
                        'messageText' : '밥',
                        'action' : 'message',
                        'label' : '오늘 밥 뭐지'
                    }, {
                        'messageText' : '날씨',
                        'action' : 'message',
                        'label' : '날씨 어때?'
                    }, {
                        'messageText' : '길찾기',
                        'action' : 'message',
                        'label' : '집 갈래'
                    }
                ]
            }
        }
    return jsonify(payload) 
    
def scheduler(): 
    schedule.run_pending()
    threading.Timer(1, scheduler).start() 
    
if __name__ == '__main__':
    scheduler() 
    
    yogiyo()
    howsTheWeather()
    
    schedule.every().hour.do(howsTheWeather)
    schedule.every().day.at('00:01').do(yogiyo)
    
    app.run(host='0.0.0.0', port='1220') 
    
