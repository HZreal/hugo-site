+++
title = 'etcd 应用与 Go 客户端实践'
date = 2024-11-08T09:32:11+08:00
categories = ["Tech"]
tags = ["etcd", "Go"]
keywords = ["etcd", "Go", "分布式协调", "服务注册发现", "分布式锁"]
description = "本文介绍了 etcd 的核心概念、典型应用场景、工作原理以及如何使用 Go 客户端进行基本操作，包括键值读写、监听变更、租约管理和分布式锁实现。"
draft = false
+++

# etcd 简要技术博客

[Github 地址](https://github.com/HZreal/Go-scenery/blob/master/middleware/etcd/goETCD.go)

## 一、etcd 是什么

etcd 是一个使用 Go 语言实现的分布式、高可用、强一致性的键值存储系统。它常被用作分布式系统中的协调组件，用来保存配置、服务节点信息、租约状态、锁状态等小体量但高价值的数据。

如果一个系统需要一个部署相对简单、读写性能稳定、支持高可用、具备强一致性语义，并且可以通过 API 访问的分布式存储，那么 etcd 是一个很常见的选择。

一句话概括：

> etcd 不是为了存大数据，而是为了可靠地存放分布式系统运行时最关键的状态。

## 二、etcd 适合解决什么问题

etcd 的典型应用场景如下：

* 配置管理：将公共配置存储到 etcd 中，服务启动或运行时读取配置。
* 服务注册：服务实例启动后，将自己的地址、端口、元信息注册到 etcd。
* 服务发现：客户端或网关监听服务节点变化，动态感知服务上下线。
* Leader 选举：多个节点通过 etcd 协调，选出一个主节点承担调度或写入职责。
* 集群监控：通过 key 的变化感知节点健康状态。
* 分布式锁：多个进程竞争同一份临界资源时，通过 etcd 保证同一时刻只有一个持有者。
* 分布式队列：基于有序 key、Watch 和事务能力实现任务分发。

这些场景有一个共同点：它们需要在多个节点之间共享状态，而且这个状态必须可靠、一致、可感知变化。

## 三、核心架构与工作原理

etcd 内部可以拆成几个关键部分理解：

* gRPC Server：对外处理客户端请求，对内处理集群节点之间的通信。
* WAL：Write Ahead Log，写前日志。写操作会先追加到 WAL 中，用于故障恢复和一致性复制。
* Raft：共识算法，负责 Leader 选举和日志复制。
* Snapshot：快照，用于压缩历史日志并帮助节点快速恢复状态。
* BoltDB：本地持久化存储引擎，用 B+ 树组织数据。
* MVCC：多版本并发控制，保存 key 的历史版本信息。

### 3.1 写入流程

一次写请求大致会经历下面的过程：

1. Client 通过 API 向 etcd 发起写请求。
2. 请求进入集群 Leader 节点。
3. Leader 将本次操作封装成 Raft 日志条目，先写入本地 WAL。
4. Leader 将日志复制给其他 Follower。
5. 当超过半数节点确认写入后，Leader 提交该日志。
6. Leader 通知其他节点提交，并将结果返回给 Client。

这里的关键是“多数派确认”。只要多数节点存活并达成一致，集群就可以继续对外提供强一致写入能力。

### 3.2 Leader 和 Follower

etcd 集群通常由一个 Leader 和多个 Follower 组成：

* Leader：处理写请求，负责日志复制和提交。
* Follower：接收 Leader 的日志，同步状态，并在 Leader 故障时参与新一轮选举。

Raft 通过任期 term、日志 index、心跳和选举超时来维护集群状态。任期可以理解为 Leader 选举的逻辑轮次，index 可以理解为日志的顺序编号。

### 3.3 Revision 与 MVCC

etcd 中每次数据变更都会产生一个全局递增的 revision。常见字段含义如下：

* `revision`：全局版本号，只要 etcd 中有修改就会递增。
* `create_revision`：某个 key 创建时对应的 revision。
* `mod_revision`：某个 key 最近一次修改时对应的 revision。
* `version`：某个 key 自身被修改的次数。
* `raft_term`：Raft 当前任期。

这套版本机制让 etcd 可以支持历史版本查询、事务比较、Watch 断点续传等能力。

## 四、etcd 与 ZooKeeper 的简单对比

etcd 和 ZooKeeper 都可以用于分布式协调，但两者的设计取向有所不同：

* etcd 使用 Go 编写，部署和二进制分发更简单。
* etcd 使用 Raft 共识算法，概念上比 ZooKeeper 使用的 Zab/Paxos 类协议更容易理解。
* etcd 原生提供 gRPC API，同时也有 etcdctl 命令行工具。
* etcd 默认写入会持久化到磁盘，并通过 WAL 保证可恢复性。
* etcd 支持 TLS/SSL 客户端认证，适合生产环境安全接入。

实际选型时，ZooKeeper 在老牌大数据生态中更常见；etcd 则在 Kubernetes、云原生和 Go 技术栈中更常见。

## 五、常用命令

### 5.1 写入和读取

```bash
etcdctl put key1 value1
etcdctl get key1
```

### 5.2 删除 key

```bash
etcdctl del key1
```

### 5.3 监听 key 变化

```bash
etcdctl watch key1
```

当其他客户端修改或删除 `key1` 时，当前命令会收到变更事件。

### 5.4 查看 key 的版本信息

```bash
etcdctl get key1 -w json
```

输出中的 `header.revision` 表示当前集群全局 revision，`kvs` 中会包含 key 的创建版本、修改版本、值等信息。

### 5.5 查询历史版本

```bash
etcdctl get key1 --rev=2
```

这可以查看某个 key 在指定 revision 时的值。

### 5.6 创建租约

```bash
etcdctl lease grant 5
```

创建一个 5 秒过期的 lease。key 可以绑定到这个 lease 上，lease 过期后，绑定的 key 会被自动删除。

### 5.7 事务

```bash
etcdctl txn -i
```

事务模式一般包含三段：

1. compares：比较条件，例如 value、mod、create 等。
2. success：比较成功时执行的操作。
3. failure：比较失败时执行的操作。

事务常用于 CAS 更新、锁竞争、状态机流转等场景。

## 六、Go 客户端实践

本项目的示例文件为 `middleware/etcd/goETCD.go`，使用的客户端依赖是：

```go
go.etcd.io/etcd/client/v3 v3.5.7
```

### 6.1 创建客户端

示例中通过 `clientv3.New` 连接本地 etcd：

```go
cli, err := clientv3.New(clientv3.Config{
    Endpoints:   []string{"127.0.0.1:2379"},
    DialTimeout: 5 * time.Second,
})
if err != nil {
    fmt.Printf("connect to etcd failed, err:%v\n", err)
    return
}
defer cli.Close()
```

生产环境中通常会配置多个 endpoint：

```go
Endpoints: []string{
    "10.0.0.1:2379",
    "10.0.0.2:2379",
    "10.0.0.3:2379",
}
```

这样客户端可以在某个节点不可用时切换到其他节点。

### 6.2 Put 和 Get

`Put` 用于创建或修改 key：

```go
ctx, cancel := context.WithTimeout(context.Background(), time.Second)
_, err = cli.Put(ctx, "key1", "value1")
cancel()
```

`Get` 用于读取 key：

```go
ctx, cancel = context.WithTimeout(context.Background(), time.Second)
resp, err := cli.Get(ctx, "key1")
cancel()
```

遍历返回结果时，可以看到 key、value、创建 revision、修改 revision 和 lease 信息：

```go
for _, ev := range resp.Kvs {
    fmt.Println(ev.Key, ev.Value, ev.CreateRevision, ev.ModRevision, ev.Lease)
}
```

实践建议：

* 每次请求都使用 `context.WithTimeout`，避免网络异常时调用长时间阻塞。
* 客户端使用完后调用 `Close`，释放连接资源。
* key 最好设计成带业务前缀的路径，例如 `/service/order/instance-1`。

### 6.3 Watch 监听变更

Watch 用于监听未来发生的变更：

```go
rch := cli.Watch(context.Background(), "key1")
for wresp := range rch {
    for _, ev := range wresp.Events {
        fmt.Printf("Type: %s Key:%s Value:%s\n", ev.Type, ev.Kv.Key, ev.Kv.Value)
    }
}
```

Watch 适合服务发现、配置热更新、节点上下线感知等场景。

例如服务发现中，可以让服务实例写入自己的节点信息：

```text
/services/order/instance-1 -> 10.0.0.1:8080
/services/order/instance-2 -> 10.0.0.2:8080
```

客户端监听 `/services/order/` 前缀，当实例新增、修改、删除时，动态更新本地服务列表。

### 6.4 Lease 租约

Lease 可以理解成 etcd 中的过期时间对象。多个 key 可以绑定同一个 lease；当 lease 过期时，所有绑定的 key 都会被删除。

示例中创建了一个 5 秒租约：

```go
resp, err := cli.Grant(context.TODO(), 5)
if err != nil {
    log.Fatal(err)
}
```

然后将 key 绑定到该租约：

```go
_, err = cli.Put(context.TODO(), "/lmh/", "lmh", clientv3.WithLease(resp.ID))
```

如果没有续约，5 秒后 `/lmh/` 会自动消失。

典型使用场景：

* 服务注册：服务进程退出后，注册信息自动删除。
* 临时任务状态：任务进程异常退出后，状态自动过期。
* 分布式锁：持锁进程异常退出后，锁可以被自动释放。

### 6.5 KeepAlive 续租

如果希望 key 在服务存活期间一直存在，可以使用 `KeepAlive`：

```go
ch, kaerr := cli.KeepAlive(context.TODO(), resp.ID)
if kaerr != nil {
    log.Fatal(kaerr)
}

for {
    ka := <-ch
    fmt.Println("ttl:", ka.TTL)
}
```

只要客户端持续续租，lease 就不会过期；一旦进程退出、网络断开或会话失效，续租停止，lease 到期后 key 会被删除。

实际项目中要注意：

* 需要处理 `KeepAlive` 返回 channel 被关闭的情况。
* 需要使用可取消的 context，方便服务退出时主动停止续租。
* 不要把过多无关 key 绑定到同一个 lease，否则过期时会一起删除。

### 6.6 分布式锁

etcd 官方客户端提供了 `concurrency` 包，可以基于 session 实现分布式锁：

```go
s1, err := concurrency.NewSession(cli)
if err != nil {
    log.Fatal(err)
}
defer s1.Close()

m1 := concurrency.NewMutex(s1, "/my-lock/")
```

加锁和解锁：

```go
if err := m1.Lock(context.TODO()); err != nil {
    log.Fatal(err)
}

if err := m1.Unlock(context.TODO()); err != nil {
    log.Fatal(err)
}
```

`NewMutex` 底层会在指定前缀下创建有序 key，通过 etcd 的顺序性、Watch 和 lease/session 机制协调锁竞争。

分布式锁实践建议：

* 锁路径要带业务含义，例如 `/locks/order-settlement/`。
* 持锁时间尽量短，避免把慢操作放在锁内。
* 加锁时使用带超时的 context，避免无限等待。
* 业务操作要尽量具备幂等性，不要只依赖锁保证正确性。
* 进程退出时要主动释放锁，同时依赖 lease 兜底处理异常退出。

## 七、一个服务注册与发现的思路

etcd 的 Lease 和 Watch 组合起来，可以实现一个简化版服务注册发现：

1. 服务启动后创建 lease，例如 TTL 为 10 秒。
2. 服务将自己的地址写入 `/services/{serviceName}/{instanceId}`，并绑定 lease。
3. 服务持续 KeepAlive，表示自己仍然存活。
4. 服务发现方 Watch `/services/{serviceName}/` 前缀。
5. 如果服务进程退出或网络断开，lease 过期，实例 key 被删除。
6. Watch 端收到删除事件后，从本地服务列表中移除该实例。

这种方式避免了服务异常退出后注册信息长期残留的问题。

## 八、生产使用注意事项

* 集群节点数建议使用奇数，例如 3 或 5 个节点，便于形成多数派。
* 不要把 etcd 当作大容量数据库使用，适合保存小而关键的元数据。
* key 的设计要有清晰前缀，便于按业务、环境和模块隔离。
* Watch 要考虑网络中断、revision 压缩、重连和重新拉取全量数据。
* Lease TTL 不宜过短，否则网络抖动可能导致误判下线。
* 分布式锁要配合业务幂等和超时控制，不能把锁当作唯一可靠边界。
* 生产环境应开启 TLS、认证和访问控制。
* 定期关注磁盘、WAL、快照、压缩和 defrag，避免历史版本占用过多空间。

## 九、总结

etcd 的核心价值是为分布式系统提供可靠的一致性状态存储。它通过 Raft 保证集群一致性，通过 WAL 和 Snapshot 保证可恢复性，通过 MVCC 提供版本能力，通过 Watch 和 Lease 支撑服务发现、配置更新和分布式锁等常见协调场景。

从 Go 客户端使用角度看，掌握下面几组 API 基本就能覆盖多数入门场景：

* `Put` / `Get`：基础键值读写。
* `Watch`：监听 key 或前缀变化。
* `Grant` / `WithLease`：创建租约并绑定 key。
* `KeepAlive`：持续续租，维持临时状态。
* `concurrency.NewSession` / `NewMutex`：实现分布式锁。

理解这些能力后，再回看服务注册、服务发现、Leader 选举、分布式锁等场景，本质上都是围绕“强一致 key-value + 版本 + 监听 + 租约”组合出来的分布式协调模式。
