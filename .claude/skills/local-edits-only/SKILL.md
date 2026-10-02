---
name: local-edits-only
description: 在本仓库工作时只修改本地文件，不执行 git 写操作（commit/branch/reset/push）或部署（mkdocs gh-deploy）。任何修改、修复、重构任务都适用。
---

# 只在本地修改

本仓库的所有任务默认**只改本地文件**：

- 不要 `git add` / `commit` / `branch` / `checkout` / `reset` / `stash` / `merge` / `push`
- 不要运行 `mkdocs gh-deploy`，也不要手动操作 `gh-pages` 分支
- 只读命令可以用：`git status`、`git diff`、`git log`、`git show`
- 验证用临时目录构建（`mkdocs build -d <临时目录>`），不要写进 `site/`（`site/` 已被提交进仓库）
- 临时脚本/配置用完即删，别留在仓库里

改完后告诉用户：改了哪些文件、怎么本地预览验证、是否会随部署一起上线。
提交与部署由用户自己决定、自己执行；只有用户明确说"帮我提交/部署"才可以做。
