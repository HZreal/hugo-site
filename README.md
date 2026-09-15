# Hello, Welcome to My Site!


## 网站导航

访问 [地址 1](https://my.elastic-code.com) 或者点击 [地址 2](https://hzreal.github.io)


## 构建步骤

```shell
# 1. 拉取源码仓库
git pull --recurse-submodules

# 2. 修改 content/config/layout 等源码内容

# 3. 构建前停掉 hugo server，避免 dev 产物混入 public
pkill -f "hugo server" || true

# 4. 生产构建
hugo --destination public --cleanDestinationDir --gc --minify

# 5. 检查不要有本地开发地址
rg "livereload|localhost:1313|127\\.0\\.0\\.1:1313" public || true

# 6. 先提交发布仓库
git -C public add -A
git -C public commit -m "deploy: publish site updates"
git -C public push origin master

# 7. 再提交源码仓库，包括 public 指针
git add -A
git commit -m "docs: update site content"
git push origin master
```
