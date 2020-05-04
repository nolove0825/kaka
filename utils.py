import os
import shutil
import time
from dateutil.parser import parse

import smtplib
from email.mime.text import MIMEText
from email.header import Header


file_max_size = 1  # Mb，日志文件多大保存一次
cache_dir = os.path.abspath('.') + "/cache"
log_dir = os.path.abspath('.') + "/log"

# ============ time ========



# ============ log =========

def save_log2(content_, log_file_name, test):
    content = "********************  " + getTime() +"  ********************" + "    \n" + str(content_) +  "\n\n\n"
    if test:
        print(log_file_name + "\n" + content)
    else:
        save_log(content, log_file_name)


def save_log(content, log_file_name):
    make_dir(log_dir)

    log_file = log_dir + "/" + log_file_name

    # 每次获取现在的ip，都把文件中的上次ip更新一下
    with open(log_file, 'a') as file:
        file.write(content)

    file_size(log_file)

# M
def file_size(log_file):
    log_name = os.path.split(log_file)[1].replace(".log", "")
    ip_cache_dir_ = cache_dir + "/" + log_name
    make_dir(ip_cache_dir_)

    fsize = os.path.getsize(log_file) / float(1024 * 1024)

    if fsize > file_max_size:
        shutil.move(log_file, ip_cache_dir_ + "/" + getTime() + ".log")
    return fsize

def getTime():
    return time.strftime('%Y_%m_%d-%H_%M_%S', time.localtime(time.time()))

def make_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def qq_send_mail(subject, content, mail_from_usr, mail_from_usr_pw, mail_to_usr):
    send_mail(subject, content, mail_from_usr, mail_from_usr_pw, mail_to_usr,
              "smtp.qq.com")

def lzu_send_mail(subject, content, mail_from_usr, mail_from_usr_pw,
                  mail_to_usr):
    send_mail(subject, content, mail_from_usr, mail_from_usr_pw, mail_to_usr, "smtp.lzu.edu.cn")


def send_mail(subject,
              content,
              mail_from_usr,
              mail_from_usr_pw,
              mail_to_usr,
              smtp_server="smtp.qq.com",
              smtp_port=465):
    msg_from = mail_from_usr  # 发送方邮箱
    passwd = mail_from_usr_pw  # 填入发送方邮箱的授权码(填入自己的授权码，相当于邮箱密码)
    # msg_to = ['****@qq.com','**@163.com','*****@163.com']  # 收件人邮箱
    msg_to = mail_to_usr  # 收件人邮箱

    # 生成一个MIMEText对象（还有一些其它参数）
    msg = MIMEText(content)
    # 放入邮件主题
    msg['Subject'] = subject
    # 也可以这样传参
    # msg['Subject'] = Header(subject, 'utf-8')
    # 放入发件人
    msg['From'] = msg_from
    # 放入收件人
    # msg['To'] = '616564099@qq.com'
    # msg['To'] = '发给你的邮件啊'
    print("发送中……")
    try:
        # 通过ssl方式发送，服务器地址，端口
        s = smtplib.SMTP_SSL(smtp_server, smtp_port)
        # 登录到邮箱
        s.login(msg_from, passwd)
        # 发送邮件：发送方，收件方，要发送的消息
        s.sendmail(msg_from, msg_to, msg.as_string())
        s.quit()
        print('成功')
        save_log2("成功发送邮件：\n" + subject + "\n" + content, "mail.log", False)
    except Exception as e:
        save_log2("邮件发送失败：\n" + subject + "\n" + content, "mail.log", False)
        print(e)
