+++
title = '代码提交规范之 Conventional Commits'
date = 2025-01-08T09:32:11+08:00
categories = ["tech"]
tags = ["git"]
keywords = ["SEO", "Keywords", "Here"]
description = "SEO Description Here"
draft = false
+++

## 引言

在软件开发中，良好的版本控制实践是维持项目健康和可持续发展的关键。一个清晰、一致的提交历史不仅可以加强团队合作，还能提高代码的可维护性。本文将介绍 Conventional Commits 规范，一种帮助您实现这一目标的提交信息格式规范。

## 什么是 Conventional Commits？

Conventional Commits 是一个轻量级的、社区驱动的提交信息格式规范。它的核心目的是使提交信息更加可读和易于理解。遵循这一规范，可以让您的 Git 历史成为一个清晰的故事，而不仅仅是代码的变更记录。

可参考链接：[https://www.conventionalcommits.org](https://www.conventionalcommits.org)

### 核心要点

1. **清晰的类型定义**：规定了一系列预定义的提交类型，如 `feat`, `fix`, `docs`, 等，每种类型对应不同的代码更改目的。
2. **可选的范围**：允许在提交类型后指定影响范围，增加了额外的上下文信息。
3. **描述性的消息**：鼓励编写简短且具有描述性的信息，概括提交的主要内容。

## 如何使用 Conventional Commits？

使用 Conventional Commits 的提交注释**基本格式**如下：

```
<type>(<scope>): <description>

<body>

<footer>
```
格式描述如下：
- `<type>`：提交类型，用于说明本次提交的类别，常见类型包括：
  - `feat`：新功能
  - `fix`：修复 Bug
  - `docs`：文档更新
  - `style`：代码风格样式调整（不影响代码运行）
  - `refactor`：代码重构
  - `perf`：性能提升（performance的缩写）
  - `test`：测试相关
  - `chore`：其他无关紧要的改动（单词是琐事的意思）
- `(<scope>)`：可选，用于进一步细化提交类型，例如 `feat(login)` 表示登录功能的新功能。
- `<subject>`：简短描述本次提交的主要内容，建议不超过 50 个字符。
- `<body>`：可选，提供更详细的提交描述，可以包含以下内容： 
  - 修改原因
  - 修改内容
  - 影响范围
  - 相关测试  
- `<footer>`：可选，包含额外的元信息，例如：
  - 关联的 Jira 问题编号
  - 提交者
  - 评审者

### 示例

```
feat(auth): 添加 JWT 认证支持

- 实现 JWT 生成和验证
- 更新认证中间件以支持 JWT

关闭问题 #123
```

在这个示例中，
`feat` 表明这是一个添加新功能的提交，`auth` 是这次更改的范围，后面紧跟着的`description`是对提交内容的简短描述。
接着`body`是一个更详细的解释。
最后`footer`是相关问题的结果。

## Conventional Commits 的好处

1. **提高可读性**：清晰的提交历史使新团队成员更容易理解项目进展。
2. **自动化工具友好**：可以被用于自动化生成变更日志和版本控制。
3. **改善协作流程**：明确的提交类型和格式有助于代码审查和团队协作。

## 结语

Conventional Commits 规范为软件开发提供了一种简单而高效的提交历史管理方法。它的简洁性和自解释性使得项目维护变得更加容易。采纳这一规范，将为您的项目带来长期的好处。