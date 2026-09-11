+++
title = "程序初始化"
weight = 50
type = "docs"
layout = "page"
+++

## 程序初始化

包内变量的初始化优先于 init 函数的初始化

从被导入包的最深处开始初始化，层层递出一直初始化至 main 包
