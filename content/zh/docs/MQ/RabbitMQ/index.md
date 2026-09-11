+++
title = "RabbitMQ"
weight = 20
type = "docs"
layout = "page"
+++


[https://www.cnblogs.com/fulongyuanjushi/p/16457753.html]()

[https://www.cnblogs.com/arthinking/p/15422958.html]()


队列即管道

管道坏了怎么办，能不能滴水不漏、无缝切换 \-〉高可用问题

管道断电了，管道中的数据是丢还是留 \-〉数据安全性问题

上游进来的水太猛了，管道会不会爆开？ \-〉吞吐量的问题



Exchange  类型

Direct：完全匹配，只会转发到指定的 routing key，topic 的特殊形式，应用于高可靠的任务分发，如交易、转账等

Fanout：扇出，广播模式。直接广播到所有绑定到自身的队列，不关注 routing key，

Topic：模糊匹配，routing key 中通过 \* （一个）或者 \# （0 或多个）来筛选不同的路由。应用于多个下游系统订阅上游系统的某个事件

Header ：匹配 AMQP 协议消息头而不是 routing key，和 direct 一样属于完全匹配，基本上也废弃了



Queue 类型

Classic：适用于快速消费，怕积压（性能断崖式下跌），已废弃

Quorum：满足大多业务，数据安全，极速增量同步，强一致性，基于 raft 协议，默认首先。

Stream：大数据流处理，日志收集，高吞吐，容忍少量数据丢失，吸收 kafka/rocketMQ 的实践

