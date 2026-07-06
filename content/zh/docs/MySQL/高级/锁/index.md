+++
title = "锁"
weight = 100
type = "docs"
layout = "page"
+++

# 概述

# 并发事务访问

## 并发事务访问的情况

### 读 - 读

并发读，不需要锁

### 写 - 写

并发写，会出现脏写问题，而脏写问题不能容忍

解决：先到的事务需加锁，后到的事务需等待，直到锁释放再去加锁执行

加锁时，创建锁结构，会关联事务 id 等

### 读 - 写 或 写 - 读

一个读，一个写，可能发生脏读、不可重复度、幻读问题

## 并发问题的解决方案

### 方案一：读操作利用多版本并发控制（MVCC），写操作加锁

![](static/GBT9bbwqSolzYoxOj9ZceKF3nVe.png)

### 方案二：读写操作都采用加锁的方式

![](static/NMRzb3lLxozg07xvBSAchYepnLc.png)

### 方案一、二简单对比

![](static/WOR6bokjHobESexfc3BctkxLnod.png)

# 锁不同角度分类

## 从数据操作的类型划分

**共享锁**和**排他锁**

![](static/VCpobXyjPolFXgxK5FbcI4VanKd.png)

**获取了 S 锁后，其他事务可以继续获得 S 锁，但不能获得 X 锁除非 S 锁已释放**

**获取了 X 锁后，其他事务不能继续获得 S/X 锁**

### 读操作

要么获取 S 锁，要么获取 X 锁（有些场景的读操作也需要排他性）

获取共享锁的方式读

Select * from tb_user lock in share mode;

Select * from tb_user for share; (8.0 版本)

获取排他锁的方式读

Select * from tb_user for update;

![](static/OKAPbVQrfoVPvexXZQJcJOSPnqb.png)

### 写操作

包含 insert、delete、update 操作

Delete 实际上是加 X 锁修改标记

Update 有 3 种情况：

1. 修改主键字段，delete + insert，加 X 锁和隐式锁；
2. 修改非主键字段，且字段数据占用存储不变，加 X 锁；
3. 修改非主键字段，且字段数据占用存储有变，delete + insert，加 X 锁和隐式锁；

Insert 实际上是加隐式锁

![](static/ZC49bqOVMopRcTxlcfycEUwynud.png)

## 从数据操作的粒度划分

![](static/AXD9b58C5ozPZjxrnZvcIvwCnWd.png)

### 表锁

![](static/CMsMbHiTyoXJfVxEA1LcwZlIn4b.png)

#### 表级别的 S 锁和 X 锁

![](static/CQifbGXCroQllZxymEQc37q2nJd.png)

查看表加的锁

Show open tables

手动加锁

Lock tables tb_user [read | write]

##### Myisam 下的表级 S 锁和 X 锁

![](static/DVJnbOqxkobHJUxqXFPckF20n1b.png)

#### 意向锁 Intention Lock

![](static/DEQmbgtTQop8ENxnvU7cIhk5nhh.png)

![](static/S5Lxb1vQPo3UPPxkekRcV63mnBh.png)

##### 意向锁要解决的问题

考虑一个场景：事物 A 对某一行记录添加了排他锁，此时事务 B 需要对该行所在的表添加锁，那么事务 B 如何判断 该表已经被加过锁？ 难道事务 B 需要对该表一行一行判断是否有行级锁？ 显然不是

实际上是事物 A 对某一行添加排他锁的同时，在行级锁的上层如页锁、表锁均添加了意向锁，事务 B 只需要判断该表有没有意向锁即可

![](static/CyQybdkHMo8TDJxqI55cHfbhneh.png)

##### 特点

![](static/PLO6bUfljogw59xZXeUccFLqnuf.png)

#### 自增锁 AUTO-INC Lock

![](static/HX6kbYbnzoCPnvxI2XIc1pJWn6b.png)

##### 3 种锁定模式

![](static/LortbJ8fZoNNFKx0SRzc0xJDn7c.png)

![](static/K3RGbl5nHoZADjxGy72cg8D3neh.png)

![](static/M760brSVeoehajxKqJ2c2zghneg.png)

#### 元数据锁 MDL Lock

其实就是针对于表结构/表元数据的锁，分为 MDL 读锁和 MDL 写锁

MDL 读锁就是**不影响表结构时**添加的，对表数据的增删改查不涉及表结构的修改

MDL 写锁就是需要**修改表结构时**需要添加的

![](static/YAUjbvcsIoG3nLxDFBOckmn9nQh.png)

### 行锁

![](static/FW8LbxkJQoU1sLxkOrvcSWRCnGe.png)

#### 记录锁 Record Lock

![](static/JVXJb0M5Jox4JgxZqXJcW48HnFd.png)

#### 间隙锁 Gap Lock

![](static/EoQMb1OYdo1E7Jx4VPMcgWs4n3d.png)

![](static/VzkMbxHQVoRNuGxTWs9cBbkDndV.png)

间隙锁随着对行记录加 S 锁时自动加上

select * from user where id = 1 for share ;

查看锁（显式锁）

Select * from performance_schema.data_locks\G

查看显示锁，insert 的隐式锁看不到的

间隙锁会出现死锁问题，当两个事务均拥有某个范围的间隙锁、且在进行插入操作时，就会出现死锁

##### 解决死锁策略（下面死锁部分详述）

1. 各自等待直至某一方超时，超时方自我回滚且释放锁
2. 检测机制检测到死锁后，回滚某个事务，释放其持有的锁，即手动破坏死锁

![](static/Tq9bbqit5oMnQcxTBQMcmq0En7c.png)

#### 临键锁 Next-Key Lock

其实就是 行记录锁 + 间隙锁

当给一个范围时，这个范围内匹配的数据行会加记录锁，间隙部分会加间隙锁

#### 插入意向锁 Insert Intention Lock

**是在 insert 操作时产生的。是一种特殊的间隙锁**

![](static/OgyjbW1OgoNAuWxRatncj0T9ndc.png)

![](static/RmRHbtNXPoetMExaHQbcquednxh.png)

### 页锁

![](static/NopgbjjLQoTImwxOts1cnFaonJN.png)

## 从对待锁的态度划分

![](static/EeEbb7jF3o3voXxrK3hcdExCnJL.png)

秒杀案例 - 不使用锁

![](static/ZxwvbjeNfoHM5FxwAmQcjIv9ncf.png)

### 悲观锁 Pessimistic Lock

适合写操作多的场景，加锁具有排他性

![](static/VEsDbSD1gowS65xdHEscSkfynVd.png)

秒杀案例 - 使用悲观锁

![](static/VNV0bE4Gfo9tZqxsgRdctymmnff.png)

![](static/CdvqbOFSbojOmJxi2cEc6cKlnIe.png)

使用悲观锁，要确定使用索引，否则会导致因顺序扫描使当前事务不需要数据行也上锁，开销大也影响并发性能

### 乐观锁 Optimistic Lock

适合读操作多的场景，无死锁

![](static/JEYrbHCGjoUYZyxKTx8c2JAPnEe.png)

#### 乐观锁的版本号机制

![](static/AjVcbUODeokdlXx7uHzcuXKQn1Q.png)

#### 乐观锁的时间戳机制

![](static/VO9lbPx4boNhqHxQCNMcoPSlnUh.png)

秒杀案例 - 使用乐观锁

![](static/IeLab0rNeorhfQx8twFcxLx8nkf.png)

![](static/Ul2LbdUDuo7Bw4xFRnVciISxn7b.png)

### 两种锁的对比、适用场景

![](static/HZ0ibl616o3JlrxoS9NcOedLnMd.png)

## 按加锁的方式划分

### 隐式锁

![](static/Fdc7bGPuNoxt36xyd1IcbCQRnQd.png)

![](static/VDBAb1NDlowIdTxRrQsccM3PnfZ.png)

![](static/K7T6buQGPoPQ5VxXp3Yc66RHnsi.png)

#### **对隐式锁的理解：**

**insert 时不加锁（含隐式锁，无锁），可以避免加锁的开销，当其他事务来读写时给当前事务的 insert 加锁（转化成显式锁），是乐观态度的体现，当出现情况时再悲观处理。而在 insert 过程中，其他事务来读写是可能发生的，若不发生就减少了加锁的开销，若发生则加锁，这就是延迟加锁！**

#### 对 insert **的情况，理解 隐式锁 与 插入意向锁**

**插入意向锁，是当前事务想 insert 却发现存在临键锁时，会加的一个锁**

**而隐式锁，是当前事务 A 进行 insert （进来时未被干扰即没有临键锁，产生了隐藏列）且还未提交时，含有隐式锁/无锁（查锁查不出来的，内存中不存在的），另一个事务 B 进来了发现该隐藏列中的 trx_id（事务 A）依然活跃，为事务 A 创建了锁。同时事务 B 也为自己创建一个锁进行等待**

### 显式锁

通过 Select * from performance_schema.data_locks 能查看得到的

通过特定语句加的锁

Select .. For share;

Select ... For update;

## 全局锁

![](static/LI1rbn8Gjoyxocx28kccJtJ7nth.png)

## 死锁

双方都持有对方的资源、双方都在等待对方释放，双方都不主动释放对方的资源

### 产生死锁的必要条件

![](static/Y6LZbQT6roRh03x0CLscuvwhnXd.png)

### 如何处理死锁

![](static/G9DkbX9u9osf2ZxRcwJcj5mjnae.png)

#### 超时等待

![](static/K9wpbuk62opr2hxvX7GcAD3InLc.png)

#### 死锁检测

![](static/Ig0QbWXI5oFZQCxDWqpcES7enab.png)

![](static/Yi24b2Ka9orHDcxq8QKcUxM0nSc.png)

![](static/NyXhbVS5EoYLilxwcPNcBS1BnCr.png)

![](static/VXOMb2EPdoD8NRxvGiTcq33lnWh.png)

### 如何避免死锁

![](static/Z8OEba3dkoZohOxHnXCcFplwnnb.png)

# 锁的内存结构

符合以下条件的记录会放在一个锁结构中：

![](static/TVaXb0uLCoA6n4xXbPWcivqbnag.png)

## 锁结构

![](static/YFy6bF6Pbo6yF4xTaujcoeYfnDg.png)

![](static/BWObbpChcolXukxrpALcQNVGnNj.png)

![](static/Em6ibz1VIoFyMVxDjSGc4PCNn5d.png)

![](static/MQPYbwOozoFvC4xaPTvc2mdqn7d.png)

![](static/Tuseb6KAroUUX8xAUHccOGZrn4e.png)

![](static/ESjMbApuboKp2RxyyzscnYsSn1f.png)

![](static/RrpGbcyKJom5GXxBKAdcPbdgn4c.png)

# 锁监控

![](static/E9uCbx5TSoG5oKxZJ2kc2LydnNc.png)

## 其他监控方法

### 三张表

5.7 之前，

使用 information_schema 库的表 innodb_trx、innodb_locks、innodb_lock_waits 表

其中，innodb_locks 表中只能看到阻塞事务的锁，不能看到未阻塞事务的锁

8.0 后，

沿用 information_schema.innodb_trx，

并使用 performance_schema.data_locks（所有的锁） 代替了原先的 information_schema.innodb_locks，除了能看到阻塞事务的锁，未阻塞事务的锁也能看到了;

使用 performance_schema.innodb_lock_waits（等待的锁） 代替了原先的 information_schema.innodb_lock_waits
