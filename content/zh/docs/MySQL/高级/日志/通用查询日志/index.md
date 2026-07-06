+++
title = "通用查询日志"
weight = 50
type = "docs"
layout = "page"
+++

```sql
show variables like '%general%';
set global general_log = ON;

# 
更新日志名称或者删除日志后，需要刷新重新生成新日志文件
mysqladmin -uroot -p flush-logs;
```
