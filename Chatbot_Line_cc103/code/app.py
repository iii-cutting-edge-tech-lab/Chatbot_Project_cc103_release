
# coding: utf-8

# In[1]:


"""
    1.建立跟redis的連線
    2.抓secret_key裡面的資料
    3.啟用API伺服器基本樣板，啟用伺服器基本
    4.撰寫用戶關注事件發生時的動作(follow event)
    5.收到按鈕（postback）的封包後(postback event)
    6.針對message event的設定
    7.啟動server

"""


# In[2]:




# In[3]:


"""

    1.針對跟redis的連線
    

"""

import redis

#製作redis連線
redis = redis.Redis(
    #redis container的host name
		host='redis',
		port=6379,
    #預設沒密碼
    password=None,
    #給格式
    charset="utf-8",
    #要解碼不然回傳的資料前面會多一個b
    decode_responses=True)


import os 

#擷取EC2裡面的ip位置，主要用於test.py
#ip_location=os.environ.get('IPA_ENV')
#我的ip，請在改成自己的
ip_location='chatbot_api'


# In[4]:


"""

    2.抓secret_key裡面的資料（由於是本機執行，所以secret_key可放在本機，之後要上AWS，要放在S3，不能放在github，有安全顧慮）
    

"""
# 載入json處理套件
import json

# 載入基礎設定檔，本機執行所以路徑可以相對位置，在test.py要改成絕對路徑，因為是使用kernel開啟
secretFile=json.load(open("/home/jovyan/work/secret_key",'r'))

# 從linebot 套件包裡引用 LineBotApi 與 WebhookHandler 類別
from linebot import (
    LineBotApi, WebhookHandler
)

# channel_access_token是用於傳送封包去給line的認證使用類似這個是私鑰，而公鑰已經丟到line那邊，拿著這個就可以有VIP特權
line_bot_api = LineBotApi(secretFile.get("channel_access_token"))

# secret_key是用於當line傳送封包過來時確定line是否為本尊，沒有被仿冒
handler = WebhookHandler(secretFile.get("secret_key"))

# rich_menu_id用於將所指定的rich menu綁定到加好友的用戶上
menu_id = secretFile.get("rich_menu_id")
server_url = secretFile.get("server_url")


# In[5]:


"""

  3.啟用伺服器基本樣板，啟用伺服器基本 

"""

# 引用Web Server套件
from flask import Flask, request, abort

# 從linebot 套件包裡引用 LineBotApi 與 WebhookHandler 類別
from linebot import (
    LineBotApi, WebhookHandler
)

# 引用無效簽章錯誤
from linebot.exceptions import (
    InvalidSignatureError
)

# 載入json處理套件
import json


# 設定Server啟用細節，這邊使用相對位置，test.py中使用絕對位置，因為是使用kernel開啟
app = Flask(__name__,static_url_path = "/images" , static_folder = "./images/")


# 啟動server對外接口，使Line能丟消息進來
@app.route("/", methods=['POST'])
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

#製作一個測試用接口
@app.route('/hello',methods=['GET'])
def hello():
    return 'Hello World!!'


# In[6]:


'''

    4.撰寫用戶關注事件發生時的動作
        1. 取得用戶個資，並存回伺服器
        2. 把先前製作好的自定義菜單，與用戶做綁定
        3. 回應用戶，歡迎用的文字消息與圖片消息
        4. 製作用戶的redis資料

'''

# 將消息模型，文字收取消息與文字寄發消息，Follow事件引入
from linebot.models import (
    MessageEvent, FollowEvent, JoinEvent,
    TextSendMessage, TemplateSendMessage,
    TextMessage, ButtonsTemplate,
    PostbackTemplateAction, MessageTemplateAction,
    URITemplateAction,ImageSendMessage
)

# 載入requests套件
import requests


#宣告並設定推播的 button_template_message (全域變數)
button_template_message = ButtonsTemplate(
                                        thumbnail_image_url='https://%s/images/aws_icon.png' %server_url,
                                        title='Menu',
                                        text='歡迎使用cc103_考古題聊天機器人\n請使用下方功能選單\n或是按下方按鈕',
                                        image_size="cover",
                                        actions=[
                                          {
                                            "type": "uri",
                                            "label": "Web 網址",
                                            "uri": "https://www.google.com",
                                            "data": "Data"
                                          },
                                          {
                                            "type": "message",
                                            "label": "AWS",
                                            "text": "AWS",
                                            "data": "Data"
                                          },
                                          {
                                            "type": "message",
                                            "label": "輕鬆一下",
                                            "text": "輕鬆一下",
                                            "data": "Data"
                                          },   
                                          {
                                            "type": "message",
                                            "label": "答題情形",
                                            "text": "detail",
                                            "data": "Data"
                                          }
                                        ],
                                    )


# 告知handler，如果收到FollowEvent，則做下面的方法處理
@handler.add(FollowEvent)
def reply_text_and_get_user_profile(event):
    
    # 取出消息內User的資料
    user_profile = line_bot_api.get_profile(event.source.user_id)
        
    # 將用戶資訊做成合適Json
    user_info = {  
        "user_open_id":user_profile.user_id,
        "user_nick_name":user_profile.display_name,
        #status留給學弟做應用
        "user_status" : "",
        "user_img" : user_profile.picture_url,
        "user_register_menu" : menu_id
    }
    
    # 將json傳回API Server
    Endpoint='http://%s:5000/user' % (ip_location)
    
    # header要特別註明是json格式
    Header={'Content-Type':'application/json'}
    
    # 傳送post對API server新增資料 
    Response=requests.post(Endpoint,headers=Header,data=json.dumps(user_info))
    print(Response)
    print(Response.text)
    
    # 將菜單綁定在用戶身上
    # 要到Line官方server進行這像工作，這是官方的指定接口
    linkMenuEndpoint='https://api.line.me/v2/bot/user/%s/richmenu/%s' % (user_profile.user_id, menu_id)
    
    # 官方指定的header
    linkMenuRequestHeader={'Content-Type':'image/jpeg','Authorization':'Bearer %s' % secretFile["channel_access_token"]}
    
    # 傳送post method封包進行綁定菜單到用戶上
    lineLinkMenuResponse=requests.post(linkMenuEndpoint,headers=linkMenuRequestHeader)

    #再跟老師討論存在redis的值有沒有需要進去mysql
    #給剛加入的用戶初始化Redis資料
    redis.hmset(user_profile.user_id, {'result': 0,"total" : 0,"sa_qid" : 0,"dev_qid" : 0,"sys_qid" : 0})
    
    
    print(Response)
    print(Response.text)
                         
    #針對剛加入的用戶回覆文字消息與圖片消息
    reply_message_list = [
                    TextSendMessage(text="歡迎%s\n感謝您加入cc103_AWS考古題機器人\n使用我來幫助您通過AWS的認證考試吧!\n\n萬一您覺得提醒的次數有點多，您可以在本畫面的聊天室設定選單中，將「提醒」的功能關掉喔！?\n" % (user_profile.display_name) ),    
                    ImageSendMessage(original_content_url='https://%s/images/certificate.jpg' %server_url,
                    preview_image_url='https://%s/images/certificate.jpg' %server_url), 
                    TemplateSendMessage(alt_text="CC103功能選單，為您服務",template=button_template_message),
                ] 
    
    #推送訊息
    line_bot_api.reply_message(
        event.reply_token,
        reply_message_list    
    )
    


# In[7]:


"""
    
    5.收到按鈕（postback）的封包後
        1. 先看是哪種按鈕（question(考試),answer(答覆)）
        2. 看是哪種類別（sa,sysops,develop）
        3. 執行所需動作（執行之後的哪一些函式）
        4. 回覆訊息

"""
from linebot.models import PostbackEvent

#parse_qs用於解析query string
from urllib.parse import urlparse,parse_qs

#用戶點擊button後，觸發postback event，對其回傳做相對應處理
@handler.add(PostbackEvent)
def handle_post_message(event):
    #抓取user資料
    user_profile = event.source.user_id
    
    #抓取postback action的data
    data = event.postback.data
    
    #用query string 解析data
    data=parse_qs(data)
    
    #出考題
    if (data['type']==['question']):
        #每要求出題後，redis 的total增加一
        redis.hincrby(user_profile,"total")
        if (data['question_type']==['sysops']):
            #每次出一題sysops增加一個sys_qid
            redis.hincrby(user_profile,"sys_qid")
            #從redis擷取出來
            questionid = redis.hget(user_profile,"sys_qid")
            #回覆一組回覆串
            line_bot_api.reply_message(
            event.reply_token,
            test('sysops',user_profile,questionid))
        elif (data['question_type']==['develop']):
            redis.hincrby(user_profile,"dev_qid")
            questionid = redis.hget(user_profile,"dev_qid")
            line_bot_api.reply_message(
            event.reply_token,
            test('devlop',user_profile,questionid))
        elif (data['question_type']==['sa']):
            redis.hincrby(user_profile,"sa_qid")
            questionid = redis.hget(user_profile,"sa_qid")
            line_bot_api.reply_message(
            event.reply_token,
            test('sa',user_profile,questionid))
            
    #給按了答案的回覆
    elif (data['type']==['answer']):
        if (data['question_type']==['sysops']):
            #進行回覆
            line_bot_api.reply_message(
                event.reply_token,
                answer_reply_list('sysops',data,user_profile)
            )
        elif (data['question_type']==['devlop']):
            #進行回覆
            line_bot_api.reply_message(
                event.reply_token,
                answer_reply_list('devlop',data,user_profile)
            )
        elif (data['question_type']==['sa']):
            line_bot_api.reply_message(
                event.reply_token,
                answer_reply_list('sa',data,user_profile)
            )
      
    else:
        pass


# In[8]:


"""

    製作許多postback event要用到的函式

"""

    
"""

    取出指定的考題資料，輔助進行後續運用

"""
#url =  "http://%s:5000/question/%s" % (ip_location,qtype)
def answer(qtype,qid):
    url =  "http://%s:5000/question/%s" % (ip_location,qtype)
    #裝query string的部份
    payload = {'question_id' : qid}
    #傳送封包
    a = requests.get(url,params=payload)
    #將回傳結果取出
    a=a.json()
    #將考題資料回傳
    return a
    
 
"""

    針對按了考試按鈕所要回傳的考題資訊
    1.先判斷question_id是否超過100，因為題庫只到100題
    2.question_id沒問題後取得指定的考題資訊
    3.利用取得的考題資料，包裝成一個回覆list，這邊使用了quick_reply

""" 
    
#做一個回傳考題的函式，擷取變數（考題類別,使用者id,考題id）
def test(questiontype,user_id,questionid):
    #由於只有100題，所以超過之後回傳一個訊息
    if (questionid==101):
        #並將它歸零
        redis.hset(user_id,questionid,0)
        #回覆訊息
        reply_message_list = [
        TextSendMessage(text="Congratulation!!!!\nYou already finish 100 question about %s" % (questiontype)),
        ]
        return reply_message_list
    # question_id沒問題後取得指定的考題資訊
    a = answer(questiontype,questionid)
    #這邊使用quick reply的方式，QuickReply算是一種TextSendMessage
    quickreply = TextSendMessage(
                text='Choose your answer:',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            #使用postback action類似按鈕的概念
                            action=PostbackAction(label="A",
                                                  #使用了data裝query string的方式，一次裝多個變數
                                                  #這邊使用true_answer()來幫助取得result的值（判斷對或錯）
                                                  data="type=answer&question_type=%s&question_id=%s&result=%s" % (questiontype,questionid,true_answer(a,'A')),
                                                  #按了按鈕之後的會有的回覆
                                                  text='choose:A'
                                                 )
                        ),
                        QuickReplyButton(
                            action=PostbackAction(label="B",
                                                  data="type=answer&question_type=%s&question_id=%s&result=%s" % (questiontype,a['question_id'],true_answer(a,'B')),
                                                  text='choose:B'
    
                                                 )
                        ),
                        QuickReplyButton(
                            action=PostbackAction(label="C",
                                                  data="type=answer&question_type=%s&question_id=%s&result=%s" % (questiontype,a['question_id'],true_answer(a,'C')),
                                                  text='choose:C'
                                                 )
                        ),
                        QuickReplyButton(
                            action=PostbackAction(label="D",
                                                  data="type=answer&question_type=%s&question_id=%s&result=%s" % (questiontype,a['question_id'],true_answer(a,'D')),
                                                  text='choose:D'
                                                 )
                        )
                    ]))
    #包裝一個回傳的list
    reply_message_list = [
        # 考題的題目
        TextSendMessage(text=a["question_content"]),
        # 考題的選項
        TextSendMessage(text=a["answer1_content"]+"\n\n"+a["answer2_content"]+"\n\n"+a["answer3_content"]+"\n\n"+a["answer4_content"]),
        #回傳quick reply選單
        quickreply    
    ]
    return reply_message_list

"""

    幫助製作一個選了答案所須的回覆訊息
    1.先取得指定考題資訊
    2.判斷用戶是否答對
    3.包裝一個針對答案所回覆的list

"""

def answer_reply_list(questiontype,data,user_profile):
    # 去API取得考題資訊
    a = answer(questiontype,data['question_id'][0])
    # 預設為錯誤的reply
    reply = "Error\nAns:%s" %a["true_answer"]
    # 假如正確的話回一個正確的reply
    if (data['result']==['True']):
        # 每答對一題，redis的result增加一
        redis.hincrby(user_profile,"result")
        # 將錯誤的回覆改成正確
        reply = 'Correct!!'
    # 包裝一個回覆list
    reply_message_list = [
        # 看是答對或答錯
        TextSendMessage(text=reply),
        # 考題詳解
        TextSendMessage(text=a["true_answer_decribe_content"]+"\n\n"),
        # 詳解的連結
        TextSendMessage(text=a["external_link"])
        ]
    #進行回覆
    return reply_message_list

"""

    專門用來判斷是否為正確答案

"""
from linebot.models import QuickReply,QuickReplyButton,PostbackAction

#寫一個函式是看正解給result使用，專門用來判斷是否為正確答案
def true_answer(a,answer):
    if a['true_answer']==answer:
        return 'True'
    else:
        return 'False'


# In[9]:


'''
    6.針對message event的設定
    當用戶發出文字消息時，判斷文字內容是否包含一些關鍵，
    若有，則回傳客製化訊息
    若無，則回傳預設訊息。

'''

# 用戶發出文字消息時， 按條件內容, 回傳文字消息
@handler.add(MessageEvent, message=TextMessage)
#將這次event的參數抓進來
def handle_message(event):
    user_profile = event.source.user_id
    # 由於在quick_reply的地方，在按鈕給了text針對按鈕的text不予回應
    if (event.message.text.find('choose:')!= -1):
        pass
    # 當用戶輸入detail時判斷成立
    elif (event.message.text.find('detail')!= -1):
        # sa回答到哪題
        sa_qid = redis.hget(user_profile,"sa_qid")
        # sysops回答到哪題
        sys_qid = redis.hget(user_profile,"sys_qid")
        # develop回答到哪題
        dev_qid = redis.hget(user_profile,"dev_qid")
        # 總答對題數
        correct = redis.hget(user_profile,"result")
        # 總回答題數
        total = redis.hget(user_profile,"total")
        # 將上面的變數包裝起來                          
        reply_list = [
            TextSendMessage(text="各類回答紀錄\nsa:%s/100\ndeveloper:%s/100\nsysops:%s/100" % (sa_qid,sys_qid,dev_qid) ),
            TextSendMessage(text="總共答對 (%s)題\n總共回答 (%s)題\n" % (correct,total))
        ]
        # 回覆訊息
        line_bot_api.reply_message(
            event.reply_token,
            reply_list
            )
    # 當用戶輸入AWS時判斷成立
    elif (event.message.text.find('AWS')!= -1):
        # 提供AWS白皮書網址及AWS培訓語認證網址
        url1='https://aws.amazon.com/tw/whitepapers/'
        url2='https://aws.amazon.com/tw/training/'
        # 將上面的變數包裝起來
        reply_list = [
            TextSendMessage(text="AWS 白皮書連結:\n%s" % (url1)),
            TextSendMessage(text="AWS 培訓與認證:\n%s" % (url2))
        ]
        # 回覆訊息
        line_bot_api.reply_message(
            event.reply_token,
            reply_list
            )
        
        
    elif (event.message.text.find('more')!= -1):        
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text="CC103功能選單，為您服務",
                template=button_template_message
            )
        )
        
    # 收到不認識的訊息時，所給予的回覆    
    else:         
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text="CC103功能選單，為您服務",
                template=button_template_message
            )
        )          


# In[ ]:


'''
    7.啟動server
    執行此句，啟動Server，觀察後，按左上方塊，停用Server

'''

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)

