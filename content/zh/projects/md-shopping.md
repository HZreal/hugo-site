+++
title = 'MD-shopping'
description = '电商购物平台'
date = 2025-01-08T09:32:11+08:00
tags = ['Python', 'Vue', 'Django', 'SDK']
categories = ['project']
+++

Github 地址： {{< button href="https://github.com/HZreal/MD-shopping" target="_blank" >}}查看 GitHub{{< /button >}}

传统的 B2C 购物网站，基于 Django 集成 Jinja2 模板 + Vue 的前后端不分离开发

功能：

1. 登录注册
2. 第三方 QQ 登录
3. 图形验证码/短信验证/邮箱验证
4. 用户中心
5. 收货地址管理
6. 首页轮播、面包屑导航
7. 商品列表、商品检索、商品详情
8. 购物车、结账
9. 订单支付、支付宝沙箱支付
10. 后台商品管理、统计分析等

技术栈点：

1. 图形验证captcha，短信验证(容联云 SDK )，采用异步 Celery 、单例模式发短信/邮件

2. Cookie/Session登录状态保持，支持多账号登录，第三方 QQ 登录(Oauth2.0认证)

3. 用户中心，用户邮件验证，收货地址管理，地址信息 Redis 缓存

4. 图片对象存储 FastDFS 文件存储/七牛云，商品列表全文检索 Elasticsearch 服务

5. 用户购物车信息根据用户登录状态，存储于 Redis 或者 Cookie 中，并做登入时的数据合并

6. 订单事务多表一致性，乐观锁实现并发下单，对接支付宝沙箱平台支付

7. 首页、详情页等重要页面静态化提高响应速度，分别采用 Crontab 定时，脚本批量生成

8. Redis 消息 broker、session 缓存、验证码缓存、浏览记录、购物车存储

9. MySQL 主从搭建实现读写分离，同时使用 Haystack 备份到 ES

10. Django restframework 后台管理高效开发、JWT认证

11. 生产部署采用 uWSGI/Gunicorn + Supervisor + Nginx + SSL

12. 上线采用云服务器
