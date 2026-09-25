# Hawkstore Registry

简体中文 · [English](README.md)

这是 Hawkstore 桌面客户端读取的公开插件 Registry。本仓库只保存元数据和可搜索索引；插件 DLL 与 ZIP 应保存在不可变的 GitHub Release 资源中。

## 目录结构

```text
index.json
categories.json
schemas/
  manifest.schema.json
  index.schema.json
mods/
  <package-id>/
    manifest.json
    README.md
examples/
tools/validate_registry.py
tools/verify_release_assets.py
```

首个正式条目为 `com.usami.dynamicterraincraters`（Dynamic Terrain Craters 1.9.0）。ZIP 通过 GitHub Release 资源分发，Registry 保存不可变下载地址、字节大小和 SHA-256 摘要。

## 投稿流程

1. 按 Hawkstore 包结构生成插件 ZIP。
2. 使用 `hawkstore-publishing` 在本地校验 manifest 和插件包。
3. 在投稿分支增加 `mods/<package-id>/manifest.json` 和 `README.md`。
4. 使用发布模板创建 Pull Request。
5. GitHub Actions 自动检查 ID、分类、版本、所有权、索引一致性，以及线上 Release 资源的大小和 SHA-256。
6. 新作者的第一次发布由维护者人工审核；已接受的版本不可覆盖。
7. 发布流水线创建 GitHub Release 并更新 `index.json`。

本地校验：

```bash
python tools/validate_registry.py
python tools/verify_release_assets.py
```

## 安全说明

进入 Registry 不代表插件绝对安全。BepInEx 插件可以执行任意代码。应尽可能公开源码、使用 SHA-256 校验，并保留人工审核与恶意软件扫描环节。
