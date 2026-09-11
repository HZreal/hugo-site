+++
title = "Redo 日志"
weight = 10
type = "docs"
layout = "page"
+++

## Redo 日志

![](static/OWifbSkZHoApCDxsuphcX0LEnVc.png)

### why?

![](static/TwSobxwBnoYwGcx3ybMcZqpKnLd.png)

![](static/HJnjbzyT9oX4FPxsMq2cuWqcn2f.png)

PS：体会一下 WAL 技术

![](static/VVxEbGmqDojZLpxmUd2cdkAEnKg.png)

### 好处、特点

![](static/ONOQbC58uomEGFxusxJcrQm0nOc.png)

### Redo 组成

#### Redo Log Buffer

![](static/FYI6bWCEjoeoKGx8QYZcF0b8nDd.png)

#### Redo Log File

![](static/XCYebMOW6omeK3xeVvocAV7unEe.png)

日志路径：/var/lib/mysql/ib_logfile0

### Redo 整体流程

事务执行过程中，redo log buffer 是实时跟进写的

![](static/NjCRbvk8TotkYUxRlwycwSSsnke.png)

### Redo 日志刷盘策略

![](static/K0kdbSbU9oxYFCxtJabcn8annac.png)

![](static/TraAb1KsPouoeXxatmjcVXnVnyh.png)

SHOW VARIABLES LIKE 'innodb_flush_log_at_trx_commit';

PS：从这里结合 Redis 的 AOF 日志刷盘策略， Redis 默认选择的是设置为 0。因此，MySQL 选择了一致性，抛弃了部分性能；Redis 平衡了性能，抛弃了部分一致性

#### innodb_flush_log_at_trx_commit = 1 时

Mysql  默认的，也是最安全的，保证持久化，效率相对最低

![](static/LTzgbojpnomGp1xjvqVc1w56nrh.png)

#### innodb_flush_log_at_trx_commit = 0 时

![](static/ZrbSb5eJeoji7nxIejXcALIznBe.png)

![](static/KuBQbGjvtosx7WxFvzQcIBHvn5e.png)

#### innodb_flush_log_at_trx_commit = 2 时

![](static/LgrfbSoxPoFSL5x1dm9cBig7nXZ.png)

#### 测试 3 种情况的效率

![](static/MAB7bgDJFoHMqGxkhP2c8r8dncb.png)

### Redo log buffer

#### Mini-Transaction 概念

![](static/OTOXbN7aFoHqVcxD1Bycr3ton3f.png)

#### Redo 日志写入 log buffer

![](static/DOxObHVODoDTv7x5CjEcAHPMnvb.png)

![](static/Nuctbp4N4oLRUdxCY11czaaBnfh.png)

![](static/UiKob1Fm6oW9xoxe4bVc5MkGnzc.png)

#### Redo  log block 结构图

![](static/Z1pHbHp1ho21tVx0nXRcGX2cnVd.png)

![](static/VSLIb4tGboX1OmxTyVBcqQEjn3f.png)

### Redo log file

#### 相关参数

SHOW VARIABLES LIKE 'innodb_log_group_home_dir';

SHOW VARIABLES LIKE 'innodb_log_files_in_group';

SHOW VARIABLES LIKE 'innodb_log_file_size';

#### 日志文件组

![](static/GKD2bMEg2ow2NCxSVHbcuDzXn4b.png)

#### checkpoint

![](static/DpiPbuDjOofOvzxVr8UcF9mUnZc.png)

![](static/KEiUbMmKoowbYAx0Q7ncv5hunye.png)

### 小结

![](static/XMR5brreHo6pCqxpjU1ci7cenRh.png)
