+++
title = "临时记录 SQL"
weight = 20
type = "docs"
layout = "page"
+++

```sql
# show engines;
alter table tb_user_pp engine = myisam;


explain
select name
from tb_user
where age > 17
;

# create index idx_user_age on tb_user_pp (age);

# 查看表的所有索引
show indexes in tb_user_pp;
# Collation（排序规则） 表示数据在索引中的排序方式，A 表示升序，D 表示降序
# Cardinality（基数） 表示索引中唯一值的估计数量（非真实的唯一值数量）
# Index_type 索引类型，MySQL 中的索引类型大多是 BTTREE（二叉树）
analyze table tb_user;

select @@profiling;
SELECT @@optimizer_switch;

show processlist;
SHOW VARIABLES LIKE 'datadir';
-- 自适应 hash  索引开关
SHOW VARIABLES LIKE '%adaptive_hash_index';
SHOW VARIABLES LIKE '%innodb_page_size';
SHOW VARIABLES LIKE '%innodb_file_per_table';
SHOW VARIABLES LIKE 'innodb_flush_log_at_trx_commit';
SHOW VARIABLES LIKE 'innodb_log_group_home_dir';
SHOW VARIABLES LIKE 'innodb_log_files_in_group';
SHOW VARIABLES LIKE 'innodb_log_file_size';
SHOW VARIABLES LIKE 'innodb_undo%';
SHOW VARIABLES LIKE 'innodb_undo_directory';
SHOW VARIABLES LIKE 'innodb_undo_tablespaces';
SHOW VARIABLES LIKE 'innodb_row_lock%';
show open tables;


select @@innodb_default_row_format;
show table status like 'demo';
select @@completion_type;

CREATE TABLE `t_user` (
  `id` int(11) NOT NULL,
  `name` VARCHAR(20) DEFAULT NULL,
  `phone` VARCHAR(20) DEFAULT NULL,
  `age` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB DEFAULT CHARACTER SET = ascii ROW_FORMAT = COMPACT;

-- 事务
begin;
select * from user where id = 5 for share ;
commit;

-- 8.0
Select * from information_schema.innodb_trx;
Select * from performance_schema.data_locks;

-- 表锁
lock tables demo.user read;
lock tables demo.user write ;
unlock tables;


-- 日志
show variables like '%general%';
set global general_log = OFF;

show variables like 'log_err%';

show variables like 'log_bin%';
show binary logs;
show binlog events in "/var/lib/mysql/binlog.000016";
SHOW VARIABLES LIKE 'binlog_format';
```
