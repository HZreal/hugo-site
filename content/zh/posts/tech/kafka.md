+++
title = 'Kafka 简要实践'
date = 2024-11-08T09:32:11+08:00
categories = ["Tech"]
tags = ["Kafka", "Go"]
keywords = ["Kafka", "Go", "消息队列", "日志聚合", "异步削峰"]
description = "本文介绍了 Kafka 的核心概念、典型应用场景、消息写入流程以及如何使用 Go 客户端进行生产和消费消息的实践，包括同步生产者、异步生产者和日志采集案例。"
draft = false
+++

# Kafka 简要技术博客：从消息模型到 Go 实践

[Github 地址](https://github.com/HZreal/Go-scenery/blob/master/middleware/kafka/kafka.md)

## 背景

Kafka 是一个高吞吐、可持久化、分布式的发布订阅消息系统。它常被放在业务系统和数据处理系统之间，用来承接事件流、日志流、指标流和异步消息。和传统“发一条、取一条”的队列相比，Kafka 更强调顺序追加、分区扩展、按偏移量消费，以及消息在一定保留周期内可重复读取。

在本目录的示例中，Kafka 的使用分成三类：

1. 基础命令和概念：见 `kafka.md`。
2. Go 生产者与消费者：见 `productor.go`、`consumer.go`。
3. 日志采集案例：见 `watchLogAndSendToKafkaCase/`。

本文基于这些文件整理一份后续可复用的技术沉淀。

## 一、Kafka 要解决什么问题

在业务系统里，常见的直接调用方式会把上下游强绑定在一起：调用方必须等待被调用方成功返回，链路越长，失败面越大。Kafka 的典型价值是把“产生事件”和“处理事件”解耦：

- 生产者只负责把消息写入指定 Topic。
- Kafka Broker 负责持久化、分区、副本和偏移量管理。
- 消费者按自己的节奏订阅 Topic 并处理消息。

因此 Kafka 适合用在日志聚合、用户行为追踪、监控指标、异步削峰、事件驱动系统和实时数据处理等场景。

## 二、核心概念

### 1. Topic

Topic 是消息的逻辑分类。可以把它理解成业务事件的频道，例如 `web_log`、`order_created`、`payment_success`。生产者写入某个 Topic，消费者订阅某个 Topic。

### 2. Partition

Partition 是 Topic 的物理分片。一个 Topic 可以包含多个 Partition，每个 Partition 内部的消息是有序追加的，并且每条消息都有递增的 Offset。

需要注意的是：Kafka 只保证同一个 Partition 内有序，不保证不同 Partition 之间的全局顺序。

### 3. Offset

Offset 是消息在 Partition 内的位置。消费者通过 Offset 标识自己消费到哪里。这个设计让 Kafka 支持重复消费、断点续读和按保留周期回放历史消息。

### 4. Producer

Producer 是消息生产者，负责把消息发送到 Kafka。发送时可以指定 Topic、Key、Value，也可以通过配置控制 ACK 级别和分区策略。

### 5. Consumer 与 Consumer Group

Consumer 是消息消费者。多个 Consumer 可以组成一个 Consumer Group。

同一个 Consumer Group 内，一个 Partition 同一时刻最多只会分配给一个 Consumer 消费；不同 Consumer Group 之间则会各自收到同一份消息。这个机制既能实现队列式的负载均衡，也能实现发布订阅式的广播消费。

### 6. Broker 与副本

Broker 是 Kafka 服务节点。Topic 的 Partition 会分布在不同 Broker 上，并通过副本机制提高可用性。一个 Partition 会有 Leader 和 Follower，生产和消费通常围绕 Leader 进行，Follower 从 Leader 同步数据。

## 三、消息写入流程

Kafka 写入消息时，典型流程如下：

1. Producer 获取目标 Topic 对应 Partition 的 Leader 信息。
2. Producer 将消息发送给 Leader。
3. Leader 将消息追加到本地日志文件。
4. Follower 从 Leader 拉取消息并写入本地。
5. Follower 同步完成后返回 ACK。
6. Leader 根据 ACK 策略决定是否向 Producer 确认写入成功。

ACK 策略会直接影响可靠性和吞吐量：

- `acks=0`：发送后不等待 Broker 响应，吞吐最高，可靠性最低。
- `acks=1`：Leader 写入成功即确认，可靠性和性能居中。
- `acks=all`：Leader 和副本同步完成后确认，可靠性最高，吞吐相对最低。

在 Go 示例中，`productor.go` 和日志采集案例都使用了 `sarama.WaitForAll`，即更偏可靠性的 ACK 策略。

## 四、分区选择策略

生产者写消息时，Kafka 会决定消息进入哪个 Partition。常见规则如下：

1. 如果显式指定 Partition，则写入指定 Partition。
2. 如果没有指定 Partition，但设置了 Key，则通常按 Key 哈希选择 Partition。
3. 如果没有指定 Partition，也没有设置 Key，则由客户端分区器按策略分配。

在 `productor.go` 中，同步生产者设置了：

```go
config.Producer.Partitioner = sarama.NewRandomPartitioner
```

这表示消息会随机写入可用分区。随机分区适合演示吞吐和负载分散，但如果业务要求同一类事件有序，比如同一个订单的状态流，就应该使用稳定 Key，让同一 Key 尽量进入同一 Partition。

## 五、Go 中使用 Sarama 生产消息

本目录使用 `github.com/Shopify/sarama` 作为 Kafka 客户端。`productor.go` 展示了同步生产者和异步生产者两种模式。

### 1. 同步生产者

同步生产者调用 `SendMessage` 后会阻塞，直到 Kafka 返回确认或错误：

```go
partition, offset, err := syncProducer.SendMessage(msg)
```

同步模式的优点是调用路径简单，成功后能直接拿到 Partition 和 Offset，适合低频写入、命令行工具、后台任务或需要明确知道单条消息投递结果的场景。

它的代价是吞吐能力通常不如异步生产者，因为每次发送都要等待结果。

### 2. 异步生产者

异步生产者通过 Channel 写入消息：

```go
asyncProducer.Input() <- message
```

Kafka 客户端在后台批量处理发送逻辑。使用异步生产者时有两个关键点：

- 如果开启 `Producer.Return.Successes`，必须消费 `Successes()` 通道。
- 必须消费 `Errors()` 通道，否则错误堆积可能导致生产者阻塞。

`productor.go` 中的 `useAsyncProducerWithGoroutines` 使用两个 goroutine 分别读取成功和失败通道，这是更接近生产环境的写法。

### 3. 关闭生产者

无论同步还是异步生产者，都应该显式关闭：

- 同步生产者使用 `Close()`。
- 异步生产者可以使用 `Close()` 或 `AsyncClose()`。

如果不关闭，可能造成资源泄漏，异步缓冲区里的消息也可能来不及刷出。

## 六、Go 中消费 Kafka 消息

`consumer.go` 使用 Sarama 的低层 Consumer API，流程是：

1. 创建 Consumer。
2. 根据 Topic 获取 Partition 列表。
3. 为每个 Partition 创建 `PartitionConsumer`。
4. 每个 Partition 启动一个 goroutine 持续读取消息。

核心代码逻辑如下：

```go
partitionList, err := consumer.Partitions("web_log")
pc, err := consumer.ConsumePartition("web_log", int32(partition), sarama.OffsetNewest)
```

这里使用 `sarama.OffsetNewest`，表示从最新位置开始消费，只接收程序启动后的新消息。如果希望从历史消息开始消费，可以使用 `sarama.OffsetOldest`。

这个示例适合理解 Partition 级别消费模型。不过在实际业务中，更常见的是使用 Consumer Group API，让 Kafka 客户端自动处理分区分配、重平衡和 Offset 提交。

## 七、日志采集案例：tail 日志并写入 Kafka

`watchLogAndSendToKafkaCase/` 是一个小型日志采集程序，目标是监听本地日志文件的新增内容，并把每一行日志发送到 Kafka。

### 1. 目录结构

```text
watchLogAndSendToKafkaCase/
├── conf/go-conf.ini
├── main.go
├── serve/kafka.go
├── serve/tail.go
├── tailWatchFile.log
└── go_test/go_test.go
```

### 2. 配置文件

`conf/go-conf.ini` 中配置 Kafka 地址、Channel 缓冲大小和日志文件路径：

```ini
[kafka]
address = 127.0.0.1:9092
chan_size = 3

[tailfile]
path = .
fileName = tailWatchFile.log
```

`main.go` 使用 `go-ini` 将 ini 配置映射到结构体，避免把连接地址、文件路径等参数硬编码到业务逻辑里。

### 3. Tail 服务

`serve/tail.go` 使用 `github.com/hpcloud/tail` 监听文件追加：

```go
config := tail.Config{
    ReOpen:    true,
    Follow:    true,
    Location:  &tail.SeekInfo{Offset: 0, Whence: 2},
    MustExist: false,
    Poll:      true,
}
```

几个配置点值得关注：

- `Follow: true`：持续监听文件新增内容。
- `ReOpen: true`：文件轮转或重新打开时尝试继续监听。
- `Location: Whence: 2`：从文件末尾开始读，只关注后续新增日志。
- `MustExist: false`：文件不存在时不直接报错。

Tail 服务读到新行后，会把文本写入 Kafka 服务暴露的 `MsgChan`。

### 4. Kafka 服务

`serve/kafka.go` 初始化 Sarama 同步生产者，并启动 goroutine 监听 `MsgChan`：

```go
case content := <-ks.MsgChan:
    msg := &sarama.ProducerMessage{
        Topic: "weblog",
        Value: sarama.StringEncoder(content),
    }
    partition, offset, err := kafkaClient.SendMessage(msg)
```

这个设计把“日志文件监听”和“消息发送”通过 Channel 解耦：

- Tail 模块只负责读取日志。
- Kafka 模块只负责发送消息。
- Channel 作为两个模块之间的缓冲和通信边界。

这是 Go 中很自然的流水线式设计：一个 goroutine 生产日志行，另一个 goroutine 消费日志行并写入 Kafka。

### 5. 整体链路

完整流程可以概括为：

```text
日志文件追加内容
    -> tail 监听到新行
    -> 写入 MsgChan
    -> Kafka 服务从 MsgChan 读取
    -> 组装 ProducerMessage
    -> 发送到 Kafka Topic
    -> 返回 partition 和 offset
```

这个案例对应 Kafka 的典型日志聚合场景：应用侧只需要持续写日志，采集程序负责把日志转成事件流，再由 Kafka 交给后续消费者、存储系统或实时计算系统处理。

## 八、命令行快速验证

本目录笔记中使用本地 `127.0.0.1:9092` 作为 Kafka 地址。启动 Kafka 后，可以用以下命令创建 Topic：

```bash
kafka-topics --create \
  --topic order \
  --bootstrap-server 127.0.0.1:9092 \
  --partitions 1 \
  --replication-factor 1
```

查看 Topic：

```bash
kafka-topics --describe \
  --topic order \
  --bootstrap-server 127.0.0.1:9092
```

启动命令行生产者：

```bash
kafka-console-producer \
  --topic order \
  --bootstrap-server 127.0.0.1:9092
```

启动命令行消费者：

```bash
kafka-console-consumer \
  --topic order \
  --from-beginning \
  --bootstrap-server 127.0.0.1:9092
```

查看消费组：

```bash
kafka-consumer-groups \
  --bootstrap-server 127.0.0.1:9092 \
  --list
```

查看指定消费组详情：

```bash
kafka-consumer-groups \
  --bootstrap-server 127.0.0.1:9092 \
  --group consumer-group1 \
  --describe
```

其中：

- `CURRENT-OFFSET` 表示消费组已经消费到的位置。
- `LOG-END-OFFSET` 表示分区当前最新位置。
- `LAG` 表示消费积压量。

## 九、实践建议

### 1. Topic 命名要贴近业务事件

示例里出现了 `web_log` 和 `weblog` 两种 Topic 名称。真实项目中应统一命名，避免生产者和消费者订阅不一致。建议按业务域和事件命名，例如：

```text
web.log.raw
order.created
payment.succeeded
```

### 2. 根据场景选择同步或异步生产者

同步生产者简单可靠，适合低频、强结果感知场景。异步生产者吞吐更好，适合日志、埋点、指标这类高频写入场景，但要认真处理成功和错误通道。

### 3. Offset 起点要明确

`OffsetNewest` 只消费新消息，适合实时监听。`OffsetOldest` 会从历史消息开始消费，适合初始化回放或调试。生产环境中建议使用 Consumer Group 管理 Offset，而不是手动按分区消费。

### 4. 错误处理不能省略

当前示例中有些地方忽略了错误，例如 `sarama.NewSyncProducer(addr, config)` 的错误没有处理。真实项目应在连接失败、发送失败、tail 初始化失败时记录日志、重试或退出。

### 5. Channel 缓冲不是无限队列

日志采集案例中 `chan_size = 3`，这意味着 Kafka 发送变慢时，Tail 写入 Channel 很快会阻塞。这个行为有利于施加背压，但也要结合业务决定是否需要更大的缓冲、批量发送、丢弃策略或本地落盘。

### 6. 日志采集要考虑文件轮转

`tail.Config` 已开启 `ReOpen`，说明它考虑到了文件重新打开。但在生产环境里还需要验证日志轮转、文件删除、权限变化、进程重启后的恢复能力。

## 十、总结

Kafka 的核心不是“发消息”这么简单，而是把业务事件抽象成可持久化、可分区、可回放的消息流。Topic 负责分类，Partition 负责扩展和局部有序，Offset 负责消费位置，Consumer Group 负责横向扩展。

本目录中的 Go 示例展示了 Kafka 使用的三个关键层次：

1. 用命令行理解 Topic、生产、消费和消费组。
2. 用 Sarama 编写同步和异步生产者、按分区消费消息。
3. 用 tail + channel + Kafka 生产者实现一个简单日志采集链路。

如果后续要把这个案例推进到更接近生产环境，优先补齐 Consumer Group、错误处理、优雅关闭、Topic 配置统一、批量发送和可观测性指标。
