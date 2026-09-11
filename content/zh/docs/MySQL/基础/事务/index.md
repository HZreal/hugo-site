+++
title = "事务"
weight = 20
type = "docs"
layout = "page"
+++

## 概念

![](static/OzJGbZjDBo0nJHxqSaWcEGlTnjc.png)

## ACID 特性

原子性 **Atomicity **：要么全部执行，要么全部不执行

一致性 **Consistency **：达到一致的状态。满足现实约束下的一致性状态

隔离性 **Isolation **：并发执行的各个事务之间相互隔离，互不影响

持久性 **Durability **：数据一旦提交，就持久化到数据库中

![](static/Bv7EbKduCo8Lurx1SWecnFL7nke.png)

## 事务的状态

![](static/UNwabxoj8on285xZbSYczP9Vn1f.png)

## 显式事务和隐式事务

### 显式事务

![](static/ZCAZbs72HobzywxHvuucko6lnMh.png)

### 隐式事务

![](static/T9sGbRqKkoGqOvxYBYzc8ttbn6V.png)

#### 隐式提交的情况

![](static/WFlwbrTX9ob5jXx5sMwcrHFWnPd.png)

![](static/WmLLbQfxhohxepxfZ4wczbpenje.png)

![](static/FpD9b17daoPlnVxabl3cButxncs.png)

## 事务分类

![](static/MElebHdOroUddHxalUXcKZganAb.png)

![](static/S2dXbUr8JoJEJLxugE1c5Fg9nCd.png)

![](static/CJCMbvj51o7STOx2uO4ciWKCned.png)

![](static/Gmm2bTzCAoCAZ8xMaBicJ3ginzb.png)

从查询和修改的角度，事务可以分为查询事务（只包含查询语句）和更新事务（至少存在一条修改语句）
