# Feishu Export Tools

这里存放从飞书云文档同步到当前 Hugo 站点的长期工具。

## 目录说明

- `download_feishu.py`: 按清单逐个调用 `feishu2md dl` 下载文档，绕过 `--wiki` / 空间权限问题。
- `migrate_to_hugo.py`: 将飞书导出的 Markdown 与同级 `static/` 图片迁移到 `content/zh/docs`。
- `deploy_site.sh`: 构建 Hugo，提交并推送 `public` 发布仓库，再提交并推送源码仓库。
- `sync_all.sh`: 串联下载、迁移、构建、提交、部署。
- `links.example.tsv`: 下载清单示例，复制为 `links.tsv` 后维护。

## 1. 准备下载清单

`feishu2md` 固定使用本机命令：

```bash
/Users/huang/.local/bin/feishu2md
```

它是软链接，真实文件位于：

```bash
/Users/huang/Documents/tool/feishu2md-v2.4.5-darwin-arm64/feishu2md
```

复制示例文件：

```bash
cp feishu-export/links.example.tsv feishu-export/links.tsv
```

每行格式：

```text
目标目录	飞书文档分享链接
```

例如：

```text
学习笔记/Go 语言/Go 基础	https://iqop6is7zk9.feishu.cn/wiki/RWgtwYdy3i7IS7k7qAacKWn6nMG
```

注意：这里使用单个文档的分享链接逐个下载，不使用 `--wiki`。这是为了绕开飞书知识库空间权限不足导致的批量导出失败。

## 2. 批量下载飞书文档

```bash
python3 feishu-export/download_feishu.py \
  --manifest feishu-export/links.tsv \
  --output /Users/huang/Downloads/feishu \
  --feishu2md /Users/huang/.local/bin/feishu2md
```

下载后目录形如：

```text
/Users/huang/Downloads/feishu/学习笔记/Go 语言/Go 基础/*.md
/Users/huang/Downloads/feishu/学习笔记/Go 语言/Go 基础/static/*.png
```

## 3. 迁移到 Hugo 技术文档

```bash
python3 feishu-export/migrate_to_hugo.py \
  --source /Users/huang/Downloads/feishu/学习笔记 \
  --dest content/zh/docs \
  --clean
```

迁移规则：

- 有子目录的目录生成 `_index.md`。
- 叶子文档生成 `index.md`。
- 每篇文档的图片保留在文档同级 `static/` 目录。
- Markdown 中飞书导出的绝对图片路径会改写为 `static/<filename>`。

## 4. 构建、提交、部署

```bash
bash feishu-export/deploy_site.sh
```

默认会：

1. 执行 `hugo --destination public --cleanDestinationDir --gc --minify`。
2. 在 `public/` 仓库提交并推送到 `master`。
3. 在源码仓库提交并推送当前分支。

可通过环境变量覆盖提交信息：

```bash
PUBLIC_COMMIT_MSG="deploy: publish Feishu docs" \
SOURCE_COMMIT_MSG="docs: sync Feishu notes" \
bash feishu-export/deploy_site.sh
```

## 5. 一键同步

```bash
bash feishu-export/sync_all.sh
```

等价于按顺序执行下载、迁移、构建、提交、部署。首次使用前先维护 `feishu-export/links.tsv`。
