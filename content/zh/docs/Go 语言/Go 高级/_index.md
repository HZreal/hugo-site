+++
title = "Go 高级"
weight = 20
type = "docs"
layout = "section"
+++

1. 并发概述：进程、线程、协程

Go 有自己的协程调度器

![](static/WIAUbk3zboSaKMxh3alc31x7ngg.png)

1. Goroutine

见个人笔记

1. channel

channel 底层维护一个队列存储数据、有锁控制并发访问，保证协程安全

有无缓冲 channel

- 无缓冲 channel（同步模式），若没有消费者读，就无法写入（阻塞）
- 有缓冲 channel（异步模式），只要没满就可以写入，只要有数据就可以读。极端情况下若满了，发送还是会阻塞（相当于同步了）

向 channel 中写入数据但不关闭，读取方 for range 时会继续循环等待接收数据

[TODO] 利用 “缓冲 channel 满了继续写会阻塞”，可以实现 Goroutine 锁

1. Sync

不像传统其他语言，采用共享内存来通信，通过锁来保证并发安全。Go 倡导通过通信来共享内存，采用 sync 包对并发安全机制的支持。

1. select 多路复用。通过起一个 goroutine 来监听各个管道的读写事件，相当于单线程处理多个 IO
2. context 作用：控制协程优雅退出、传递上下文信息。
3. 定时器
4. 协程池
5. 反射
