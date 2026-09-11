+++
title = "备份与恢复"
weight = 60
type = "docs"
layout = "page"
+++

# 逻辑备份

mysqldump

# 物理备份

拷贝数据目录下指定数据库的指导表

Show global variables like '%secure%'

Select * from <db-name>.<table-name> Into outfile '/var/lib/mysql-files/aaa.txt'

Load data infile '/var/lib/mysql-files/aaa.txt' into table <db-name>.<table-name>

mysqlimport -uroot -p '/var/lib/mysql-files/aaa.txt'

# 数据库迁移

物理迁移

逻辑迁移
