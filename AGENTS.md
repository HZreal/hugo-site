# Repository Guidelines

## 项目结构与内容组织

这是一个 Hugo 静态站点。当前主配置文件是 `hugo.toml`，站点域名为 `https://my.elastic-code.com/`，默认语言为中文 `zh`。当前主题只保留并使用 `themes/blowfish`。

主要目录：

- `content/zh/_index.md`：中文首页正文。
- `content/zh/profile/_index.md`：个人中心页面。
- `content/zh/docs/`：技术文档，按目录树组织；目录页使用 `_index.md`。
- `content/zh/posts/`：博客文章，按栏目目录组织，例如 `tech/`、`tool/`、`go/`。
- `content/zh/projects/`：项目专栏。
- `static/`：站点静态文件，例如 `CNAME`、图片等。
- `public/`：Hugo 构建后的发布仓库，对应 `HZreal/HZreal.github.io`，不要手工编辑。
- `feishu-export/`：飞书文档下载、迁移、构建和部署脚本。

## 构建、预览与部署命令

- `hugo server -D`：本地预览，包含草稿内容。它会生成带 `localhost:1313` 和 `livereload` 的开发产物，不要直接提交 `public/`。
- `hugo --destination public --cleanDestinationDir --gc --minify`：生产构建到 `public/`。
- `git submodule update --init --recursive`：初始化 `public` 和 `themes/blowfish` 子模块。
- `bash feishu-export/deploy_site.sh`：构建站点，提交并推送 `public/` 发布仓库，再提交并推送源码仓库。
- `bash feishu-export/sync_all.sh`：按 `feishu-export/links.tsv` 下载飞书文档、迁移到 `content/zh/docs` 并部署。

实际发布链路：`HZreal/hugo-site` 保存 Hugo 源码；`public/` 是构建结果并推送到 `HZreal/HZreal.github.io`；GitHub Pages 从发布仓库 `master` 分支根目录发布。源码仓库自身的 Pages/Actions 部署已停用。

## 写作与命名约定

Markdown 文件必须包含 Hugo front matter。示例：

```toml
+++
title = "文章标题"
date = 2026-09-15T10:00:00+08:00
categories = ["tech"]
tags = ["go", "linux"]
draft = false
+++
```

技术文档目录排序优先使用 `weight`，数字越小越靠前。目录页放在 `_index.md` 中，例如 `content/zh/docs/Go 语言/_index.md`。图片等附件建议放在文章同级 `static/` 目录，并用相对路径引用。

## 测试与验证

没有独立单元测试。内容或配置变更后至少运行：

```bash
hugo --destination public --cleanDestinationDir --gc --minify
```

发布前检查 `public/` 中不能出现开发地址：

```bash
rg -n "livereload|localhost:1313|127\\.0\\.0\\.1:1313" public || true
```

若改动了导航、首页、技术文档或样式，应同时用 `hugo server -D` 本地检查页面展示。

## 提交与发布规范

提交信息使用简短清晰的 Conventional Commit 风格，例如：

- `docs: update site content`
- `chore: remove unused Hugo themes`
- `deploy: publish content updates`

提交时区分源码仓库和发布仓库：`public/` 内部是单独 Git 仓库，发布产物需要在 `public/` 内提交并推送；源码仓库再提交 Markdown、配置和 `public` 子模块指针。不要提交 Hugo 缓存、`.DS_Store` 或开发服务器生成的 `public` 内容。

## Agent 注意事项

不要覆盖用户未说明的本地文档改动；提交前先看 `git status`，只暂存与当前任务相关的文件。
