+++
title = "错误日志"
weight = 60
type = "docs"
layout = "page"
+++

show variables like 'log_err%';

/var/log/error.log

```bash
更名并刷新 
mv /var/log/error.log /var/log/error.log.old
install -omysql -gmysql -m0644 /dev/null /var/log/error.log
mysqladmin -uroot -p flush-logs;
```
