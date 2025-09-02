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

# 设置工作目录为脚本所在目录的父目录
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

sys.path.append(project_root)

# 现在可以正确导入模块了
from utils.logger import logger

# 导入并运行main.py中的GitHub Actions模式
if __name__ == '__main__':
    logger.info("===== 启动GitHub Actions专用爬虫 ====")
    logger.info(f"当前工作目录: {os.getcwd()}")
    logger.info(f"脚本目录: {script_dir}")
    logger.info(f"项目根目录: {project_root}")
    
    # 显示环境变量，用于调试
    logger.info("当前环境变量配置:")
    logger.info(f"- MODE: {os.environ.get('MODE', '未设置')}")
    logger.info(f"- FORUM_KEY: {os.environ.get('FORUM_KEY', '未设置')}")
    logger.info(f"- START_PAGE: {os.environ.get('START_PAGE', '未设置')}")
    logger.info(f"- END_PAGE: {os.environ.get('END_PAGE', '未设置')}")
    logger.info(f"- RANDOM_FORUM: {os.environ.get('RANDOM_FORUM', '未设置')}")
    logger.info(f"- ZIP_CONTENT: {os.environ.get('ZIP_CONTENT', '未设置')}")
    logger.info(f"- MAX_POSTS_PER_PAGE: {os.environ.get('MAX_POSTS_PER_PAGE', '未设置')}")
    logger.info(f"- MAX_PICS_PER_POST: {os.environ.get('MAX_PICS_PER_POST', '未设置')}")
    
    try:
        # 导入主模块
        from main import CrawlerMain
        
        # 直接运行主程序，让它自己解析命令行参数和环境变量
        sys.exit(CrawlerMain.main())
    except Exception as e:
        logger.exception("GitHub Actions专用爬虫启动失败")
        sys.exit(1)