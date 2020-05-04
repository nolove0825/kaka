import requests
import re
import time
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from apscheduler.schedulers.blocking import BlockingScheduler
import os
import shutil
import json
import random
import utils
from multiprocessing import Process  #导入multiprocessing模块，然后导入Process这个类
from dateutil.parser import parse
from datetime import datetime
import config

test_ = config.test

headers = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"
}


def getMD5(cardId):
    datas = {"cardId": cardId}

    s = requests.post("http://202.201.13.180:9037/encryption/getMD5",
                      headers=headers,
                      data=datas).text.strip()

    jsons = json.loads(s)
    if jsons["code"] == 1:
        md5 = jsons["data"]
        return md5
    else:
        raise Exception("获取md5错误\n" + s)


def getInfo(cardId, md5):
    param = {"cardId": cardId, "md5": md5}

    url = "http://202.201.13.180:9037/grtbMrsb/getInfo"

    s = requests.post(url, headers=headers, data=param).text.strip()

    jsons = json.loads(s)
    if jsons["code"] == 1:
        data = jsons["data"]
        return data

    else:
        raise Exception("获取信息错误\n" + s)


def get_temp(n):

    if n == 0:
        temp = random.randint(config.temp_zc_, config.temp_zc) / 10.0
    elif n == 1:
        temp = random.randint(config.temp_zw_, config.temp_zw) / 10.0
    elif n == 2:
        temp = random.randint(config.temp_ws_, config.temp_ws) / 10.0
    else:
        raise Exception("获取温度有误\n" + str(n))

    return temp


def get_name(data):
    return str(data["list"][0]["xm"])


def get_id(data):
    return str(get_id_num(data))


def get_id_num(data):
    return data["list"][0]["xykh"]


def get_usr_msg(data):

    cardId = get_id(data)

    return get_name(
        data) + cardId + "  邮箱" + config.usrs[cardId] + "qq.com\nsjd: " + str(
            data["sjd"]) + "\n\n" + get_da_ka(data) + "\n\n" + str(data)


def get_log_file_name(data):
    return get_id(data) + ".log"


def get_da_ka(data):

    msg = ""
    dailys = data["list"]
    for daily in dailys:
        msg = "早晨：" + str(daily["zcsbsj"]) + "：" + str(daily["zcwd"]) + "\n中午：" + \
            str(daily["zwsbsj"]) + "：" + str(daily["zwwd"]) + "\n晚上：" +\
                str(daily["wssbsj"]) + "：" + str(daily["wswd"]) + msg
    return msg


def sublime(data):

    sjd_ = data["sjd"]  # 0早上，1中午，2下午，“”此时不能打卡
    daily = data["list"][0]

    if len(sjd_) == 0:
        msg = "此时不能打卡：   " + get_usr_msg(data)
        # 正常不应该发生这个问题！

        if test_:
            print("此时不能打卡：   " + get_usr_msg(data))
        else:
            raise Exception(msg)

    else:
        n = int(sjd_)
        wds = [daily["zcwd"], daily["zwwd"], daily["wswd"]]
        if wds[n] == None:
            wds[n] = get_temp(n)

            param = {
                "bh": daily["bh"],
                "xykh": daily["xykh"],
                "twfw": daily["twfw"],
                "sfzx": daily["sfzx"],
                "sfgl": daily["sfgl"],
                "szsf": daily["szsf"],
                "szds": daily["szds"],
                "szxq": daily["szxq"],
                "sfcg": daily["sfcg"],
                "cgdd": daily["cgdd"],
                "gldd": daily["gldd"],
                "jzyy": daily["jzyy"],
                "bllb": daily["bllb"],
                "sfjctr": daily["sfjctr"],
                "jcrysm": daily["jcrysm"],
                "xgjcjlsj": daily["xgjcjlsj"],
                "xgjcjldd": daily["xgjcjldd"],
                "xgjcjlsm": daily["xgjcjlsm"],
                "zcwd": wds[0],
                "zwwd": wds[1],
                "wswd": wds[2],
                "sbr": daily["sbr"],
                "sjd": sjd_
            }

            url = "http://202.201.13.180:9037/grtbMrsb/submit"

            s = requests.post(url, headers=headers, data=param).text.strip()

            jsons = json.loads(s)
            if jsons["code"] == 1:
                message = jsons["message"]
                cardId = get_id_num(data)
                msg = "打卡成功：   " + get_usr_msg(getInfo(cardId, getMD5(cardId)))
                print(msg)
                save_log(msg, get_log_file_name(data))

                if not test_:
                    qq_mail = config.usrs[cardId] + "@qq.com"
                    send_mail_to_usr("打卡成功", msg, qq_mail)

                return param
            else:
                raise Exception("提交错误\n" + get_usr_msg(data) + "\n\n" + param +
                                "\n\n" + s)

        else:
            msg = "已经打过卡了：   " + get_usr_msg(data)
            save_log(msg, get_log_file_name(data))


def daka(cardId):

    try:
        if not test_:
            sleep_min = random.randint(0, config.dealy)
            # sleep_min = 0
            sleep_sec = random.randint(0, 60)
            sleep_time = sleep_min * 60 + sleep_sec

            time.sleep(sleep_time)

        md5 = getMD5(cardId)
        data = getInfo(cardId, md5)
        sublime(data)

    except Exception as err:

        msg = "\n\n" + str(err)
        save_log(msg, str(cardId) + ".log")

        if not test_:
            send_mail_to_admin("打卡错误  ", msg)


def send_mail_to_admin(subject, content):
    # 你也可以用qq邮箱的配置
    # utils.qq_send_mail
    utils.lzu_send_mail(subject, content, config.mail_from_usr,
                 config.mail_from_usr_pw, config.mail_to_usr)


def send_mail_to_usr(subject, content, mail_to_usr):
    # 你也可以用qq邮箱的配置
    # utils.qq_send_mail
    utils.lzu_send_mail(subject, content, config.mail_from_usr,
                        config.mail_from_usr_pw, mail_to_usr)


def save_log(content, log_file_name):
    utils.save_log2(content, log_file_name, test_)


def start_auto():
    for cardId in cardIds:
        p = Process(target=daka, args=(cardId, ))
        p.start()


cardIds = config.usrs.keys()

# daka(320160936051)

save_log("开始" + str(cardIds), "daka.log")

if test_:
    start_auto()
else:
    scheduler = BlockingScheduler()
    # 正式
    scheduler.add_job(start_auto,
                      'cron',
                      hour=config.time_hour,
                      minute=config.time_min)
    scheduler.start()

# zc_0 = parse("6:00")
# zc_1 = parse("10:00")

# zw_0 = parse("10:30")
# zw_1 = parse("14:30")

# ws_0 = parse("18:30")
# ws_1 = parse("22:30")
