+++
title = 'canal 监听 MySQL Binlog 并推送 Redis 队列的增量同步方案'
date = 2025-11-08T09:32:11+08:00
categories = ["Tech"]
tags = ["canal", "MySQL", "Redis"]
keywords = ["canal", "MySQL", "Redis", "增量同步", "Binlog"]
description = "本文介绍了一种基于 Canal 监听 MySQL Binlog 并将变更事件推送到 Redis 队列的增量同步方案，适用于数据同步、异步补偿、缓存刷新等场景。"
draft = false
weights = 1
+++

# 基于 Canal 监听 MySQL Binlog 并推送 Redis 队列的增量同步方案

在一些业务系统中，我们经常会遇到这样的场景：主业务数据写入 MySQL 后，需要把变更通知给另一个系统处理，例如数据同步、异步补偿、缓存刷新、搜索索引更新、历史数据迁移等。

最直接的做法是在业务代码里写同步逻辑，但这种方式侵入性强，而且容易因为代码路径复杂而遗漏。更通用的方案是基于 MySQL Binlog 做 CDC（Change Data Capture）：业务系统正常写数据库，独立订阅服务监听 Binlog，解析出变更事件后投递到消息队列或缓存队列，下游消费者再异步处理。

本文记录一种轻量实现：使用 Canal 或 go-mysql SDK 订阅 MySQL Binlog，解析 INSERT、UPDATE、DELETE 事件，将变更主键写入 Redis 队列/集合，再由业务消费者异步处理。

## 一、整体架构

整体链路如下：

```text
业务系统写入 MySQL
        |
        v
MySQL ROW Binlog
        |
        v
Canal / go-mysql SDK 订阅解析
        |
        v
提取库名、表名、事件类型、主键
        |
        v
写入 Redis 队列或 Set
        |
        v
下游消费者异步处理业务
```

这个方案的核心思想是：同步服务不直接处理复杂业务，只负责把数据库变化转换成稳定、轻量的消息。下游消费者拿到表名和主键后，可以再回源数据库查询最新数据并执行实际业务。

## 二、MySQL Binlog 配置

Canal 和大多数 Binlog 订阅 SDK 都依赖 MySQL 复制协议，因此 MySQL 必须开启 Binlog，并建议使用 ROW 模式。

在 MySQL 配置文件中增加或确认如下配置：

```ini
[mysqld]
server_id=1
log-bin=mysql-bin
binlog_format=ROW
binlog_row_image=FULL
```

各配置含义：

- `server_id`：MySQL 复制协议需要的服务 ID，同一复制拓扑内不能重复；
- `log-bin`：开启二进制日志；
- `binlog_format=ROW`：记录行级变更，便于 CDC 程序准确解析每一行的 INSERT、UPDATE、DELETE；
- `binlog_row_image=FULL`：记录完整行镜像，兼容性最好。只同步主键时也可以考虑 `MINIMAL`，但如果后续需要字段级同步，推荐保持 `FULL`。

创建专用订阅账号：

```sql
CREATE USER 'canal_reader'@'%' IDENTIFIED BY '<password>';
GRANT SELECT, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'canal_reader'@'%';
FLUSH PRIVILEGES;
```

配置完成后，可以通过以下 SQL 验证：

```sql
SHOW VARIABLES LIKE 'log_bin';
SHOW VARIABLES LIKE 'binlog_format';
SHOW VARIABLES LIKE 'binlog_row_image';
SHOW MASTER STATUS;
```

## 三、Canal 安装与配置

Canal 是阿里巴巴开源的 MySQL Binlog 增量订阅组件。它会伪装成 MySQL slave，拉取 Binlog 并解析为结构化事件，然后供客户端消费。

### 1. 使用部署包安装

下载 Canal Deployer：

```bash
wget https://github.com/alibaba/canal/releases/download/canal-<version>/canal.deployer-<version>.tar.gz
mkdir -p /opt/canal
tar zxvf canal.deployer-<version>.tar.gz -C /opt/canal
cd /opt/canal
```

修改实例配置，例如 `conf/example/instance.properties`：

```properties
canal.instance.mysql.slaveId=1234
canal.instance.master.address=127.0.0.1:3306
canal.instance.dbUsername=canal_reader
canal.instance.dbPassword=<password>
canal.instance.connectionCharset=UTF-8
canal.instance.filter.regex=.*\\..*
```

如果只订阅部分表，可以把 `canal.instance.filter.regex` 改为更精确的规则，例如：

```properties
canal.instance.filter.regex=order_db\\.orders|user_db\\.users
```

启动 Canal：

```bash
sh bin/startup.sh
```

查看日志：

```bash
tail -f logs/canal/canal.log
tail -f logs/example/example.log
```

停止 Canal：

```bash
sh bin/stop.sh
```

### 2. 使用 Docker 启动

Canal 官方也提供 Docker 启动脚本，可以通过环境变量覆盖实例配置：

```bash
wget https://raw.githubusercontent.com/alibaba/canal/master/docker/run.sh

sh run.sh \
  -e canal.auto.scan=false \
  -e canal.destinations=example \
  -e canal.instance.master.address=127.0.0.1:3306 \
  -e canal.instance.dbUsername=canal_reader \
  -e canal.instance.dbPassword=<password> \
  -e canal.instance.connectionCharset=UTF-8 \
  -e canal.instance.tsdb.enable=true \
  -e canal.instance.gtidon=false \
  -e 'canal.instance.filter.regex=.*\\..*'
```

启动成功后，客户端连接 Canal Server 的 `11111` 端口，并指定 `destination=example` 消费对应实例。

## 四、订阅服务配置设计

一个典型订阅服务只需要配置 MySQL/Canal、Redis、订阅规则和批量大小。

示例：

```yaml
Redis:
  Addr: 127.0.0.1:6379
  Password: ""

Canal:
  Host: 127.0.0.1
  Port: 11111
  User: canal_reader
  Password: "<password>"
  Destination: example
  BatchSize: 100
  TimeoutMs: 60000

Subscribe:
  TableRegex: ".*\\..*"
```

如果使用 Canal Server，`Canal.Host` 和 `Canal.Port` 填 Canal Server 地址。如果使用 go-mysql 这类 SDK 直连 MySQL，则这里应填写 MySQL 地址和端口。

## 五、方案一：通过 Canal Server + canal-go 消费 Binlog

这种方式适合已有 Canal Server，或者希望统一管理多个订阅实例的场景。

Go 客户端连接 Canal Server：

```go
conn := client.NewSimpleCanalConnector(
    "127.0.0.1",
    11111,
    "canal_reader",
    "<password>",
    "example",
    60000,
    60000,
)

if err := conn.Connect(); err != nil {
    return err
}

if err := conn.Subscribe(".*\\..*"); err != nil {
    return err
}
```

循环拉取消息：

```go
for {
    message, err := conn.Get(100, nil, nil)
    if err != nil {
        time.Sleep(time.Second)
        continue
    }

    if message.Id == -1 || len(message.Entries) == 0 {
        time.Sleep(time.Second)
        continue
    }

    for _, entry := range message.Entries {
        handleEntry(&entry)
    }
}
```

解析 `Entry`：

```go
func parseEntry(entry *pbe.Entry) (*BinlogEvent, error) {
    if entry.GetEntryType() == pbe.EntryType_TRANSACTIONBEGIN ||
        entry.GetEntryType() == pbe.EntryType_TRANSACTIONEND {
        return nil, nil
    }

    rowChange := new(pbe.RowChange)
    if err := proto.Unmarshal(entry.StoreValue, rowChange); err != nil {
        return nil, err
    }

    if rowChange.GetIsDdl() {
        return nil, nil
    }

    event := &BinlogEvent{
        Schema:    entry.Header.SchemaName,
        Table:     entry.Header.TableName,
        EventType: rowChange.GetEventType().String(),
    }

    for _, row := range rowChange.GetRowDatas() {
        for _, col := range row.AfterColumns {
            if (event.EventType == "INSERT" || event.EventType == "UPDATE") && col.IsKey {
                event.PrimaryKey = append(event.PrimaryKey, col.Value)
            }
        }

        for _, col := range row.BeforeColumns {
            if event.EventType == "DELETE" && col.IsKey {
                event.PrimaryKey = append(event.PrimaryKey, col.Value)
            }
        }
    }

    return event, nil
}
```

## 六、方案二：通过 go-mysql SDK 直连 MySQL

如果不想单独部署 Canal Server，也可以使用 `github.com/go-mysql-org/go-mysql/canal` 直接订阅 MySQL Binlog。它同样会基于 MySQL 复制协议读取 Binlog，并回调行变更事件。

初始化客户端：

```go
cfg := canal.NewDefaultConfig()
cfg.Addr = "127.0.0.1:3306"
cfg.User = "canal_reader"
cfg.Password = "<password>"
cfg.IncludeTableRegex = []string{"order_db\\.orders|user_db\\.users"}

// 不做全量 dump，只监听增量变更
cfg.Dump.ExecutionPath = ""

c, err := canal.NewCanal(cfg)
if err != nil {
    return err
}

c.SetEventHandler(&eventHandler{
    handler: pushToRedis,
})

return c.Run()
```

事件处理器：

```go
type eventHandler struct {
    canal.DummyEventHandler
    handler func(*BinlogEvent)
}

func (h *eventHandler) OnRow(e *canal.RowsEvent) error {
    event := parseRowsEvent(e)
    if event == nil {
        return nil
    }

    h.handler(event)
    return nil
}
```

行事件解析：

```go
func parseRowsEvent(e *canal.RowsEvent) *BinlogEvent {
    event := &BinlogEvent{
        Schema: e.Table.Schema,
        Table:  e.Table.Name,
    }

    switch e.Action {
    case canal.InsertAction:
        event.EventType = "INSERT"
    case canal.UpdateAction:
        event.EventType = "UPDATE"
    case canal.DeleteAction:
        event.EventType = "DELETE"
    default:
        return nil
    }

    pkIndexes := e.Table.PKColumns
    if len(pkIndexes) == 0 {
        return nil
    }

    for i := 0; i < len(e.Rows); {
        switch e.Action {
        case canal.InsertAction, canal.DeleteAction:
            row := e.Rows[i]
            for _, idx := range pkIndexes {
                event.PrimaryKey = append(event.PrimaryKey, row[idx])
            }
            i++

        case canal.UpdateAction:
            after := e.Rows[i+1]
            for _, idx := range pkIndexes {
                event.PrimaryKey = append(event.PrimaryKey, after[idx])
            }
            i += 2
        }
    }

    return event
}
```

UPDATE 事件通常是 `before/after` 成对出现。同步下游时，一般使用 `after` 行里的主键，代表变更后的目标记录。

## 七、事件结构设计

为了降低下游复杂度，可以把 Binlog 解析结果统一成一个内部事件对象：

```go
type BinlogEvent struct {
    Schema     string `json:"schema"`
    Table      string `json:"table"`
    EventType  string `json:"event_type"`
    PrimaryKey []any  `json:"pk,omitempty"`
}
```

如果下游只需要知道“哪些数据变了”，主键已经足够。消费者可以根据 `schema/table/pk` 回查数据库，拿到最新状态再处理。

如果下游需要完整审计或历史变更，则可以扩展：

```go
type BinlogEvent struct {
    Schema     string                 `json:"schema"`
    Table      string                 `json:"table"`
    EventType  string                 `json:"event_type"`
    PrimaryKey []any                  `json:"pk,omitempty"`
    NewData    map[string]interface{} `json:"new,omitempty"`
    OldData    map[string]interface{} `json:"old,omitempty"`
    Timestamp  int64                  `json:"timestamp,omitempty"`
}
```

## 八、写入 Redis：队列还是 Set

写入 Redis 有两种常见模型。

### 1. Redis Set：适合去重批处理

如果下游只需要最终处理某个 ID 的最新状态，可以用 Set。

```go
const (
    ChangeKeyPrefix = "DATA-CHANGE-"
    DeleteKeyPrefix = "DATA-DELETE-"
)

func pushToRedis(ctx context.Context, rdb *redis.Client, event *BinlogEvent) error {
    var key string

    switch event.EventType {
    case "INSERT", "UPDATE":
        key = ChangeKeyPrefix + event.Table
    case "DELETE":
        key = DeleteKeyPrefix + event.Table
    default:
        return nil
    }

    return rdb.SAdd(ctx, key, event.PrimaryKey...).Err()
}
```

这种方式的特点：

- 同一个 ID 多次变化会自动去重；
- 按表分桶，消费者可以批量拉取；
- 不保证顺序；
- 不保留完整变更历史。

适用场景：缓存刷新、数据补偿、按 ID 重建索引、最终一致同步。

### 2. Redis Stream：适合可靠消费

如果需要消息顺序、消费确认、失败重试，可以使用 Redis Stream。

生产者：

```go
func pushStream(ctx context.Context, rdb *redis.Client, event *BinlogEvent) error {
    payload, _ := json.Marshal(event)

    return rdb.XAdd(ctx, &redis.XAddArgs{
        Stream: "binlog_stream",
        Values: map[string]interface{}{
            "event": string(payload),
        },
    }).Err()
}
```

消费者：

```go
msgs, err := rdb.XReadGroup(ctx, &redis.XReadGroupArgs{
    Group:    "group1",
    Consumer: "consumer1",
    Streams:  []string{"binlog_stream", ">"},
    Count:    10,
    Block:    2 * time.Second,
}).Result()

if err == nil {
    for _, msg := range msgs[0].Messages {
        // 解析并处理 msg.Values["event"]
        rdb.XAck(ctx, "binlog_stream", "group1", msg.ID)
    }
}
```

这种方式的特点：

- 支持 consumer group；
- 支持 ack；
- 可以处理 pending 消息；
- 可以保留完整事件流；
- 实现和运维复杂度高于 Set。

## 九、下游消费者处理逻辑

以 Redis Set 模型为例，消费者可以按表扫描待处理 ID：

```php
<?php

$redis = new Redis();
$redis->connect('127.0.0.1', 6379);

$table = 'orders';
$key = 'DATA-CHANGE-' . $table;

$ids = $redis->sMembers($key);
foreach ($ids as $id) {
    // 1. 根据主键回查 MySQL 最新数据
    // 2. 执行业务同步、缓存刷新或索引更新
    // 3. 成功后从集合中移除
    $redis->sRem($key, $id);
}
```

DELETE 可以用独立 key 处理：

```php
$deleteKey = 'DATA-DELETE-' . $table;
$deletedIds = $redis->sMembers($deleteKey);

foreach ($deletedIds as $id) {
    // 执行删除后的补偿逻辑
    $redis->sRem($deleteKey, $id);
}
```

实际生产中建议消费者按批次处理，例如每次 `SPOP` 固定数量，避免一次性拉取过大集合。

```php
$ids = $redis->sPop($key, 100);
```

## 十、异常和可靠性设计

### 1. 表必须有主键

基于主键投递的方案要求订阅表必须有主键。没有主键时，订阅服务很难给下游一个稳定的处理标识。

### 2. 明确是否需要顺序

Redis Set 不保证顺序。如果业务对顺序敏感，例如库存流水、资金流水、审计日志，应优先考虑 Redis Stream、Kafka、RocketMQ 等消息模型。

### 3. 消费失败不要丢 ID

使用 Set 时，建议消费者处理成功后再删除 ID。如果用 `SPOP` 先弹出再处理，需要自己设计失败补偿，例如失败时重新写回 Set 或写入失败集合。

### 4. 记录 Binlog 位点

更严谨的 CDC 系统会记录 Binlog file、position 或 GTID，便于重启后续读、回溯和排查。简单场景可以依赖 SDK 内部保存位点，但生产环境最好明确位点存储策略。

### 5. 订阅规则要尽量精确

不要默认订阅所有库表后再在业务代码中过滤。推荐在 Canal 或 SDK 层配置白名单正则，降低无关 Binlog 的解析成本。

### 6. DDL 事件单独处理

如果只做数据增量同步，可以忽略 DDL。如果下游依赖字段结构，DDL 事件需要单独记录、告警或触发元数据刷新。

## 十一、排查清单

如果订阅服务收不到数据，可以按下面顺序排查：

```sql
SHOW VARIABLES LIKE 'log_bin';
SHOW VARIABLES LIKE 'binlog_format';
SHOW MASTER STATUS;
```

然后检查：

- 订阅账号是否具备 `REPLICATION SLAVE`、`REPLICATION CLIENT` 权限；
- MySQL 地址、端口、账号、密码是否正确；
- `server_id` 是否和其他复制客户端冲突；
- 表名是否匹配订阅正则；
- 被订阅表是否存在主键；
- Canal Server 日志或 SDK 客户端日志是否有鉴权、网络、位点错误；
- Redis 是否可写；
- 消费者是否正常运行，是否存在失败重试堆积。

Redis 侧可以直接查看：

```bash
redis-cli SMEMBERS DATA-CHANGE-orders
redis-cli SMEMBERS DATA-DELETE-orders
```

Stream 模型可以查看：

```bash
redis-cli XLEN binlog_stream
redis-cli XINFO GROUPS binlog_stream
```

## 十二、方案小结

基于 MySQL Binlog 的增量订阅方案，可以把数据变更捕获从业务代码中解耦出来。Canal 或 go-mysql SDK 负责监听和解析 Binlog，订阅服务负责把变更事件转换成统一消息，下游消费者再异步处理具体业务。

如果业务只关心“哪些记录变了”，Redis Set 是一个很轻量的实现：按表分桶、自动去重、消费者批量处理。它适合最终一致的同步场景。

如果业务需要严格顺序、完整历史、消费确认和失败重试，则应选择 Redis Stream、Kafka 或 RocketMQ。架构上仍然是同一套 CDC 思路，只是消息存储和消费语义更强。

最终可以把这类系统抽象成一句话：

```text
MySQL Binlog 负责记录变化，Canal/SDK 负责解析变化，Redis/MQ 负责传递变化，消费者负责消化变化。
```

## 参考资料

- Alibaba Canal QuickStart: https://github.com/alibaba/canal/wiki/QuickStart
- Alibaba Canal Docker QuickStart: https://github.com/alibaba/canal/wiki/Docker-QuickStart
- go-mysql README: https://github.com/go-mysql-org/go-mysql/blob/master/README.md
- MySQL Binary Logging Options: https://dev.mysql.com/doc/refman/8.0/en/replication-options-binary-log.html
