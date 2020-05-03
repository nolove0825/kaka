<!--
 * @Description: 
 * @Version: 1.0
 * @Date: 2020-05-02 22:17:02
 * @LastEditTime: 2020-05-03 15:11:36
 -->

# python学习

学习python网络请求，定时任务，邮件发送,json解析等

## 配置学号等信息

配置文件在[config.py](config.py)配置

## python依赖

注意安装python的依赖:

```bash
pip3 install requirements.txt
```

## 运行以及测试

运行下面文件即可
> 如果要测试，先配置好[config.py](config.py)的文件，然后将其中的test修改为True

```bash
python3 daily.py
```

## 后台服务与开机自启

怎么在服务器后台运行，自己百度，如果是linux可以用systemctl管理后台运行以及开机自启
