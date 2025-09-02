# 草榴论坛爬虫项目

## 项目介绍

这是一个功能完备的草榴论坛爬虫工具，支持图片和文学内容的爬取、下载和打包。项目采用模块化设计，具有良好的扩展性和稳定性。

## 目录结构

```
1024_caoliu/
├── code/                  # 主代码目录
│   ├── core/              # 核心功能模块
│   │   ├── pic_crawler.py       # 图片爬虫模块
│   │   └── literature_crawler.py # 文学爬虫模块
│   ├── utils/             # 工具函数模块
│   │   ├── logger.py            # 日志工具
│   │   ├── request_utils.py     # 网络请求工具
│   │   └── file_utils.py        # 文件操作工具
│   ├── config/            # 配置文件目录
│   │   └── settings.py          # 全局配置
│   ├── logs/              # 日志文件目录
│   ├── tests/             # 测试文件目录
│   ├── main.py            # 主入口脚本
│   ├── 草榴_P_github_actions.py  # GitHub Actions专用脚本
│   └── requirements.txt   # 依赖包列表
└── .github/workflows/     # GitHub Actions工作流
    └── autoRelease.yml    # 自动发布工作流
```

## 功能特性

1. **模块化设计**：采用清晰的模块化结构，便于维护和扩展
2. **多种爬取模式**：支持手动模式、自动模式、GitHub Actions模式
3. **多种内容类型**：支持图片和文学内容的爬取
4. **自动打包功能**：可将爬取的内容自动打包为ZIP文件
5. **健壮的错误处理**：包含完善的异常处理和日志记录
6. **自动去重**：记录已爬取的URL，避免重复爬取
7. **GitHub Actions支持**：专为GitHub Actions环境优化的脚本

## 安装说明

1. 克隆项目代码
2. 安装依赖包：
   ```
   pip install -r code/requirements.txt
   ```

## 使用方法

### 主入口脚本

```bash
python code/main.py [参数]
```

参数说明：
- `--mode`, `-m`: 爬虫运行模式，可选值：auto, manual, github_actions, literature, pic
- `--forum`, `-f`: 论坛板块键名
- `--start_page`: 起始页面
- `--end_page`: 结束页面
- `--random`: 是否随机选择板块
- `--zip`: 是否打包下载的内容

### 运行模式含义

- **auto**: 自动模式，无需用户交互，根据配置自动爬取内容
- **manual**: 手动模式，交互式运行，用户可以选择板块和设置爬取参数
- **github_actions**: GitHub Actions专用模式，优化了在GitHub Actions环境下的运行体验
- **literature**: 文学模式，专注于爬取文学板块的内容
- **pic**: 图片模式，专注于爬取图片板块的内容

### 板块键名列表

项目支持以下板块键名，可以通过`--forum`或`-f`参数指定：

| 板块键名 | 对应的板块名称 | 板块ID |
|---------|--------------|-------|
| pics | 技术交流 | 7 |
| new_era | 新時代的我們 | 8 |
| daguerre_flag | 達蓋爾的旗幟 | 16 |
| literature | 文学 | 20 |
| story | 故事 | 2 |
| poem | 诗歌 | 3 |

### 示例

1. 手动模式（交互式）：
   ```bash
   python code/main.py --mode manual
   ```

2. 自动模式（随机板块）：
   ```bash
   python code/main.py --mode auto --random --zip
   ```

3. 爬取指定板块的图片：
   ```bash
   python code/main.py --mode pic --forum pics --start_page 1 --end_page 3 --zip
   ```

4. 爬取文学内容：
   ```bash
   python code/main.py --mode literature --forum literature --start_page 1 --end_page 2
   ```

## GitHub Actions自动发布

项目包含自动发布工作流，每天定时运行并发布爬取的内容。工作流配置位于 `.github/workflows/autoRelease.yml`。

## 配置说明

项目的主要配置位于 `code/config/settings.py` 文件中，包括：
- 网站URL和板块配置
- 文件保存路径
- 请求头和爬取参数
- ZIP打包设置

## 日志记录

项目使用统一的日志系统，日志文件保存在 `code/logs/` 目录下。日志包含详细的操作记录和错误信息，便于调试和监控。

## 注意事项

1. 请遵守相关法律法规，合理使用爬虫工具
2. 不要过度爬取，避免对目标网站造成过大压力
3. 定期清理日志文件，避免占用过多存储空间
4. 在GitHub Actions环境中运行时，注意工作流的时间限制

## 许可证

[MIT License](LICENSE)

## 功能
<ul><li>[ ] 使用多线程提升效率</li>//无对勾
<li>[x] 爬取图片放入指定文件夹下的分文件夹</li>//对勾
<li>[ ] 板块选择</li>
<li>[ ] 手动修改url的麻烦</li>
<li>[ ]文字爬取</li>
<li>[ ]</li>
<li>[ ]</li>
<li>[ ]</li>
</ul>
## 注意事项：
<p>已爬取草榴p.txt必须与py在同一文件夹。</p>
<p>~达咩达咩~</p>

## TODO
<ul><li>[√] 使用多线程提升效率</li>
<li>[x] 爬取图片放入指定文件夹下的分文件夹</li>
<li>[√] 板块选择</li>
<li>[ ] 手动修改url的麻烦</li>
<li>[ ]文字爬取</li>
<li>[ ]优化pic资源文件夹内多级分类</li>
<li>[ ]优化采集效率</li>
<li>[ ]</li>
</ul>