import requests
from datetime import datetime
from bs4 import BeautifulSoup
import itchat
from apscheduler.schedulers.blocking import BlockingScheduler
import time
import city_dict
import yaml
from itchat.content import *


# 收到好友消息
@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
def friend_text_reply(msg):
    # msg.user.send('%s: %s' % (msg.type, msg.text))
    print("====>get friend msg:  "+msg.user+" ："+msg.text)

# 收到群消息
@itchat.msg_register(TEXT, isGroupChat=True)
def group_text_reply(msg):
    # if msg.isAt:
    #     msg.user.send(u'@%s\u2005I received: %s' % (
    #         msg.actualNickName, msg.text))
    print("====>get group msg:   "+msg.actualNickName+" : "+msg.text)


def online():
    try:
        if itchat.search_friends():
            return True
    except:
        return False
    return True

def login():
    if online():
        return True
    # 登陆，尝试 5 次
    for _ in range(5):
        # 命令行显示登录二维码
        itchat.auto_login(enableCmdQR=2, hotReload=True)
        # itchat.auto_login()
        if online():
            print('login sucess')
            return True
    return False


global viplist
global vipWechatIDlis
global chatGroupName
global chatGroupNickName

RemindHour = 10
RemindMin = 50
# 今天要点餐人的ID
VipIDToday = 0


class VIP:
    NickName = ""
    UserName = ""

    def ToString(self):
        return "nickName:"+self.NickName+",UserName:"+self.UserName


class Job:
    def start_today_info(self):
        # 定时任务
        if isToadyNeedTakeout():
            names = GetToadyVipName()
            print("今天要点餐的人：%s，明天要点餐的人:%s"%(names[0],names[1]))
        else:
            print("今天不需要点餐")

#获取今天和明天要点餐人的昵称,返回一个list
def GetToadyVipName():
    if isToadyNeedTakeout() == True:
        #今天要点餐
        global VipIDToday
        vipname = viplist[VipIDToday].NickName
        VipIDToday = (VipIDToday+1) % len(viplist)
        tomorrowName = viplist[VipIDToday].NickName
        return [vipname,tomorrowName]

# 判断今天是否需要点餐
def isToadyNeedTakeout():
    sec = datetime.now().second
    print("today is :",sec)
    if sec%5 == 0:
        # print("今天不需要点餐---Yes")
        return False
    else:
        # print("今天点餐---No")
        return True

    day = datetime.now()
    today = day.weekday()
    print("today is " + str(today))
    if today <= 4:
        return True
    else:
        return False

# 往群里发消息
def SendMsgToChat(msgText):
    itchat.send_msg(msgText, toUserName=chatGroupUserName)

# 主函数
if __name__ == '__main__':
    print("===takeout programe start===")

    idlist = [2, 4, 3, 0, 1, 13]

    VipIDToday = 0

    # 登录微信
    if not login():
        print("login failed")
    viplist = []
    chatGroupName = "外卖值日生"
    # chatGroupName = "团结友爱"
    # 在群里获取值日生的微信号
    # print(itchat.get_chatrooms(contactOnly=True))

    ChatGroupRoom = itchat.search_chatrooms(name=chatGroupName)
    ChatGroupRoom = itchat.update_chatroom(ChatGroupRoom[0]['UserName'])
    # 获取群id
    chatGroupUserName = ChatGroupRoom['UserName']

    # 获取到六大常任理事国,放入viplist中
    for id in idlist:
        count = 0
        for man in ChatGroupRoom['MemberList']:
            if count == id:
                vip = VIP()
                vip.NickName = man['NickName']
                vip.UserName = man['UserName']
                viplist.append(vip)
            count = count+1

    # for man in roomlist['MemberList']:
    #     # print(man['NickName'])
    #     # print(man['UserName'])
    #     # print("***")
    #     vip = VIP()
    #     vip.NickName = man['NickName']
    #     vip.UserName = man['UserName']
    #     viplist.append(vip)

    # 打印viplist
    for man in viplist:
        print(man.ToString())

    # 定时任务
    scheduler = BlockingScheduler()
    job = Job()
    scheduler.add_job(job.start_today_info, 'interval',seconds = 2)
    # scheduler.add_job(job.start_today_info, 'cron', hour = RemindHour,minute = RemindMin)
    scheduler.start()

    itchat.run()
