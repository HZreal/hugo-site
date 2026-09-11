+++
title = 'AI 工具发现平台'
description = '按真实需求快速找到值得使用的工具'
date = 2025-01-08T09:32:11+08:00
tags = [' typescript', 'react', 'vite', 'Cloudflare D1', 'D1 FTS5', 'Drizzle ORM']
categories = ['project']
+++

Github 地址： {{< button href="https://github.com/HZreal/AI-scenery/tree/feat/ai-scenery-mvp" target="_blank" >}}查看 GitHub{{< /button >}}

部署站点： {{< button href="https://ai-scenery.elasticcode.chatgpt.site/" target="_blank" >}}访问站点{{< /button >}}

面向中文用户的 AI 工具发现平台，覆盖国内外最具价值、应用广泛且已成熟可用的产品。它不以“收录数量”作为首要价值，而以“按真实任务快速找到值得使用的工具”为目标。用户应能在 30 秒内完成：表达需求、缩小选择范围、理解工具是否适合自己、进入官网试用。

采用 Sites 的 Cloudflare Worker 运行时, 前端和服务端均使用 TypeScript;

Sites 负责将构建产物部署到 Cloudflare Worker，并创建/管理逻辑 D1 绑定。应用代码、D1 migrations 与站点托管元数据共同保存
