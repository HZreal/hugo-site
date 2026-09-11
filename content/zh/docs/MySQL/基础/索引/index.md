+++
title = "索引"
weight = 90
type = "docs"
layout = "page"
+++

如下图为图书馆的图书摆放，仔细体会索引的奥义

![](static/K4dCb8msnoyhYexbAu7cdhW2nie.png)

目的：加快较慢的查询

注意：基于查询创建索引，而不是基于表创建索引！

#### 创建、查看索引

自定义索引通常称为二级索引，创建二级索引后，MySQL 会自动将主键 id 存储到该索引中。该索引中的每个记录都包含索引对应字段的值 和主键 id

Explain 分析执行计划

```sql
explain
select name
from user
where age > 17;

# create index idx_user_age on user (age); # 创建前后，分析上述查询的查询计划

# 查看表的所有索引
show indexes in user;
# Collation（排序规则） 表示数据在索引中的排序方式，A 表示升序，D 表示降序
# Cardinality（基数） 表示索引中唯一值的估计数量（非真实的唯一值数量）
# Index_type 索引类型，MySQL 中的索引类型大多是 BTTREE（二叉树）

analyze table user; # 执行后再次查看表的所有索引
```

#### 在字符串类型(char/varchar/text/blob)的字段上创建索引

##### 前缀索引

```sql
create index idx_user_last_name on user(last_name(20))
# 其中 20 是前缀字符数，对于 char/varchar 可选，对于 text/blob 必传
# 且 20 这个字符数设置为多少有讲究，为什么不设置为 1 等较小的字符数？原因是字符数较少，重复性就很高，就像不要给性别这样的大量重复的字段设置索引一样。因为重复性太高，MySQL 走索引时还是要在相同值上花大量扫描次数
# 目的是：最大化索引值中唯一值的数量！

# 如何判定这个字符数设置为多少较好？
select 
count(distinct left(last_name, 1)) as c1,  # 假设 c1=25
count(distinct left(last_name, 5)) as c2,  # 假设 c2=966
count(distinct left(last_name, 10)) as c3  # 假设 c3=996
from user # 总计 1010 条记录
c1、c2、c3 中，应选择基本上囊括大部分的唯一值且字符数又不是太多的。首先 c3 的唯一值肯定比其他多（字符数选择的多，必然唯一值更多），这里选择 c2 而不是 c3，原因是 c3 相对于 c2 增加了一倍的字符数换来的唯一值数量的增加不明显！
```

## 索引分类

![](static/JIBKbVyhuo5x2AxRHRycaSUVnng.png)
