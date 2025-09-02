#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
草榴论坛爬虫 - GitHub Actions 专用版本

此脚本为GitHub Actions环境优化，特点:
- 单线程下载，避免多线程在GitHub Actions中引发的问题
- 绝对路径处理，确保在GitHub Actions容器中正确读写文件
- 自动选择随机板块和页面进行爬取
- 包含空目录检测逻辑，避免打包空文件夹
- 自动生成created_zips.txt文件，记录创建的ZIP文件路径
"""

import sys
import os
from utils.logger import logger

# 设置工作目录为脚本所在目录的父目录
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

sys.path.append(project_root)

# 导入并运行main.py中的GitHub Actions模式
if __name__ == '__main__':
    logger.info("===== 启动GitHub Actions专用爬虫 ====")
    logger.info(f"当前工作目录: {os.getcwd()}")
    logger.info(f"脚本目录: {script_dir}")
    logger.info(f"项目根目录: {project_root}")
    
    try:
        # 导入主模块
        from main import CrawlerMain
        import argparse
        
        # 创建命令行参数对象
        parser = argparse.ArgumentParser()
        parser.add_argument('--mode', type=str, default='github_actions')
        parser.add_argument('--zip', action='store_true', default=True)
        args = parser.parse_args([])  # 创建空参数列表，使用默认值
        
        # 运行GitHub Actions模式
        sys.exit(CrawlerMain.main())
    except Exception as e:
        logger.exception("GitHub Actions专用爬虫启动失败")
        sys.exit(1)