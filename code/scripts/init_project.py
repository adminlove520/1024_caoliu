#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
项目初始化脚本
用于创建所有必要的目录和文件
"""

import os
import sys
from config.settings import Config
from utils.logger import logger
from utils.file_utils import file_utils


def init_project():
    """初始化项目目录结构"""
    logger.info("===== 开始初始化项目 ====")
    
    # 创建所有必要的目录
    directories = [
        Config.PIC_DIR,
        Config.LITERATURE_DIR,
        Config.ZIP_OUTPUT_DIR,
        Config.LOG_DIR,
        os.path.join(Config.ZIP_OUTPUT_DIR, 'pictures'),
        os.path.join(Config.ZIP_OUTPUT_DIR, 'literature'),
    ]
    
    for directory in directories:
        if file_utils.create_directory(directory):
            logger.info(f"目录已创建或已存在: {directory}")
        else:
            logger.error(f"目录创建失败: {directory}")
    
    # 验证目录是否存在
    missing_dirs = []
    for directory in directories:
        if not os.path.exists(directory):
            missing_dirs.append(directory)
    
    if missing_dirs:
        logger.error(f"以下目录创建失败: {missing_dirs}")
    else:
        logger.info("所有必要的目录创建成功")
    
    # 验证配置文件
    try:
        # 验证板块配置
        logger.info(f"配置的板块数量: {len(Config.FORUMS)}")
        for key, name in Config.FORUMS.items():
            logger.info(f"板块: {key} - {name}")
        
        # 验证获取URL方法
        test_url = Config.get_forum_url('pics', 1)
        logger.info(f"测试板块URL: {test_url}")
        
        # 验证获取日期方法
        today_date = Config.get_today_date_string()
        logger.info(f"当前日期: {today_date}")
        
        # 验证ZIP文件名方法
        zip_name = Config.get_today_zip_filename('test')
        logger.info(f"测试ZIP文件名: {zip_name}")
        
        logger.info("配置验证成功")
    except Exception as e:
        logger.exception(f"配置验证失败: {e}")
    
    logger.info("===== 项目初始化完成 ====")


if __name__ == '__main__':
    try:
        init_project()
    except Exception as e:
        logger.exception(f"初始化过程中发生错误: {e}")
        sys.exit(1)