+++
title = "键 过期"
weight = 70
type = "docs"
layout = "page"
+++

## 常用设置、查询操作

```c
EXPIRE key seconds
PEXPIRE key milliseconds

EXPIREAT key timestamp
PEXPIREAT key milliseconds-timestamp

SETEX key seconds value
PSETEX key milliseconds value

TTL key
PTTL key
```

Ttl

## 删除策略

定时删除： 设置键的过期时间时，同时设置一个定时器，当定时器到达过期时间时就自动触发删除操作

惰性删除： 不设置定时器， 当键过期时不做任何处理，当下一次访问此键时发现不存在就触发删除操作

定期删除： 设置一个全局周期检查定时器， 每次检查部分已过期的键并执行删除操作

Redis 选择 惰性删除 + 定期删除
