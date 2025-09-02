# 草榴

# 爬虫模块目录

此目录包含爬虫项目的核心代码。

## 目录结构

```
code/
├── core/              # 核心功能模块
│   ├── pic_crawler.py       # 图片爬虫模块
│   └── literature_crawler.py # 文学爬虫模块
├── utils/             # 工具函数模块
│   ├── logger.py            # 日志工具
│   ├── request_utils.py     # 网络请求工具
│   └── file_utils.py        # 文件操作工具
├── config/            # 配置文件目录
│   └── settings.py          # 全局配置
├── scripts/           # 脚本文件目录
│   ├── main.py              # 主入口脚本
│   ├── 草榴_P_github_actions.py  # GitHub Actions专用脚本
│   ├── format_novel.py      # 小说格式化工具
│   ├── init_project.py      # 项目初始化脚本
│   └── optimized_zip.py     # 优化的压缩工具
├── legacy_scripts/    # 遗留脚本目录（保留旧版本功能）
├── tests/             # 测试文件目录
├── zips/              # 打包文件目录
└── requirements.txt   # 依赖包列表
```

## 主要功能

1. **图片爬取**：支持从多个板块爬取图片内容
2. **文学爬取**：支持从文学板块爬取小说内容
3. **自动打包**：将爬取的内容自动打包为ZIP文件
4. **多模式支持**：支持手动模式、自动模式、GitHub Actions模式

## 使用方法

详情请参考项目根目录下的readme.md文件。