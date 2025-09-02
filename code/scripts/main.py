#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# 确保能够正确导入项目模块
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

import argparse
import random
import time
from config.settings import Config
from utils.logger import logger
from utils.file_utils import file_utils, optimized_zipper
from core.pic_crawler import pic_crawler
from core.literature_crawler import literature_crawler

class CrawlerMain:
    """爬虫主程序类"""
    
    @staticmethod
    def parse_arguments():
        """解析命令行参数"""
        parser = argparse.ArgumentParser(description='草榴论坛爬虫工具')
        
        # 模式选择
        parser.add_argument('--mode', '-m', type=str, default='github_actions',
                            choices=['auto', 'manual', 'github_actions', 'literature', 'pic'],
                            help='爬虫运行模式')
        
        # 通用参数
        parser.add_argument('--forum', '-f', type=str, default='pics',
                            help='论坛板块键名')
        parser.add_argument('--start_page', type=int, default=5,
                            help='起始页面')
        parser.add_argument('--end_page', type=int, default=3,
                            help='结束页面')
        
        # 自动模式参数
        parser.add_argument('--random', action=argparse.BooleanOptionalAction, default=True,
                            help='是否随机选择板块')
        
        # 打包参数
        parser.add_argument('--zip', action=argparse.BooleanOptionalAction, default=True,
                            help='是否打包下载的内容')
        
        # 性能优化参数
        parser.add_argument('--max_posts', type=int, default=5, 
                            help='每页最多处理的帖子数量')
        parser.add_argument('--max_pics', type=int, default=20, 
                            help='每个帖子最多下载的图片数量')
        
        return parser.parse_args()
    
    @staticmethod
    def run_pic_crawler(args):
        """运行图片爬虫"""
        forum_key = args.forum
        start_page = args.start_page
        end_page = args.end_page
        max_posts = getattr(args, 'max_posts', 5)
        max_pics = getattr(args, 'max_pics', 20)
        
        logger.info("===== 开始图片爬虫任务 ====")
        logger.info(f"配置参数: 板块={forum_key}, 页面范围={start_page}-{end_page}, 每页最多{max_posts}个帖子, 每个帖子最多{max_pics}张图片")
        
        # 传递限制参数给爬虫
        success_count = pic_crawler.crawl(forum_key, start_page, end_page, use_multiprocess=False, 
                                         max_posts=max_posts, max_pics=max_pics)
        logger.info(f"===== 图片爬虫任务完成，成功爬取 {success_count} 个帖子 ====")
        
        if args.zip:
            CrawlerMain.zip_crawled_content('pic', forum_key)
    
    @staticmethod
    def run_literature_crawler(args):
        """运行文学爬虫"""
        forum_key = args.forum
        start_page = args.start_page
        end_page = args.end_page
        max_posts = getattr(args, 'max_posts', 5)
        
        logger.info("===== 开始文学爬虫任务 ====")
        logger.info(f"配置参数: 板块={forum_key}, 页面范围={start_page}-{end_page}, 每页最多{max_posts}个帖子")
        
        # 传递限制参数给爬虫
        success_count = literature_crawler.crawl(forum_key, start_page, end_page, max_posts=max_posts)
        logger.info(f"===== 文学爬虫任务完成，成功爬取 {success_count} 个帖子 ====")
        
        if args.zip:
            CrawlerMain.zip_crawled_content('literature', forum_key)
    
    @staticmethod
    def run_manual_mode(args):
        """运行手动模式"""
        print("===== 手动爬虫模式 ====")
        
        # 显示可用板块
        print("可用板块列表:")
        for key, name in Config.FORUMS.items():
            print(f"{key}: {name}")
        
        # 用户选择板块
        forum_key = input("请输入要爬取的板块键名 (默认: pics): ").strip() or "pics"
        if forum_key not in Config.FORUMS:
            print(f"无效的板块键名: {forum_key}")
            forum_key = "pics"
        
        # 用户输入页面范围
        try:
            start_page = int(input("请输入起始页面 (默认: 5): ").strip() or "5")
            end_page = int(input("请输入结束页面 (默认: 10): ").strip() or "10")
        except ValueError:
            print("输入无效，使用默认值")
            start_page, end_page = 5, 10
        
        # 选择爬取类型
        crawl_type = input("请选择爬取类型 (pic/literature, 默认: pic): ").strip().lower() or "pic"
        
        # 更新参数
        args.forum = forum_key
        args.start_page = start_page
        args.end_page = end_page
        
        # 执行爬虫
        if crawl_type == 'literature':
            CrawlerMain.run_literature_crawler(args)
        else:
            CrawlerMain.run_pic_crawler(args)
    
    @staticmethod
    def run_auto_mode(args):
        """运行自动模式"""
        logger.info("===== 自动爬虫模式 ====")
        
        # 选择板块
        if args.random:
            # 随机选择一个板块
            forum_key = random.choice(list(Config.FORUMS.keys()))
            logger.info(f"随机选择板块: {forum_key} - {Config.FORUMS[forum_key]}")
        else:
            forum_key = args.forum
            logger.info(f"使用指定板块: {forum_key} - {Config.FORUMS[forum_key]}")
        
        # 更新参数
        args.forum = forum_key
        
        # 执行爬虫（默认使用图片爬虫）
        CrawlerMain.run_pic_crawler(args)
    
    @staticmethod
    def run_github_actions_mode(args):
        """运行GitHub Actions模式"""
        logger.info("===== GitHub Actions 模式 ====")
        
        # 如果没有指定参数，则使用环境变量或默认值
        forum_key = os.environ.get('FORUM_KEY', args.forum)
        start_page = int(os.environ.get('START_PAGE', str(args.start_page)))
        end_page = int(os.environ.get('END_PAGE', str(args.end_page)))
        random_forum = os.environ.get('RANDOM_FORUM', str(args.random)).lower() == 'true'
        zip_content = os.environ.get('ZIP_CONTENT', str(args.zip)).lower() == 'true'
        
        # 读取性能优化参数
        max_posts = int(os.environ.get('MAX_POSTS_PER_PAGE', str(args.max_posts)))
        max_pics = int(os.environ.get('MAX_PICS_PER_POST', str(args.max_pics)))
        
        # 如果需要随机选择板块
        if random_forum:
            forum_key = random.choice(list(Config.FORUMS.keys()))
            # 随机页面范围
            start_page = random.randint(1, 10)
            end_page = start_page  # 只爬取一个随机页面
            
            logger.info(f"随机选择板块: {forum_key} - {Config.FORUMS[forum_key]}")
            logger.info(f"随机选择页面: {start_page}")
        
        # 更新参数
        args.forum = forum_key
        args.start_page = start_page
        args.end_page = end_page
        args.zip = zip_content
        args.max_posts = max_posts
        args.max_pics = max_pics
        
        logger.info(f"GitHub Actions 运行配置:")
        logger.info(f"- 模式: {args.mode}")
        logger.info(f"- 板块: {args.forum}")
        logger.info(f"- 页面范围: {args.start_page}-{args.end_page}")
        logger.info(f"- 每页最多处理: {args.max_posts}个帖子")
        logger.info(f"- 每个帖子最多下载: {args.max_pics}张图片")
        
        # 执行爬虫
        CrawlerMain.run_pic_crawler(args)
        
        # 检查是否有内容被爬取
        forum_name = Config.get_forum_name(forum_key)
        pic_dir = os.path.join(Config.PIC_DIR, forum_name)
        
        if not os.path.exists(pic_dir) or not os.listdir(pic_dir):
            logger.warning(f"没有爬取到任何内容，尝试爬取文学板块")
            # 尝试爬取文学板块
            literature_forums = ['literature', 'story', 'poem']
            lit_forum_key = random.choice(literature_forums) if literature_forums else 'literature'
            args.forum = lit_forum_key
            CrawlerMain.run_literature_crawler(args)
    
    @staticmethod
    def zip_crawled_content(content_type, forum_key):
        """打包已爬取的内容"""
        if content_type == 'pic':
            source_dir = os.path.join(Config.PIC_DIR, Config.get_forum_name(forum_key))
        else:
            source_dir = os.path.join(Config.LITERATURE_DIR, Config.get_forum_name(forum_key))
        
        if not os.path.exists(source_dir) or not os.listdir(source_dir):
            logger.warning(f"源目录为空，跳过打包: {source_dir}")
            return
        
        # 执行打包
        logger.info(f"开始打包 {content_type} 内容")
        
        # 创建输出文件名
        if content_type == 'pic':
            zip_filename = "每日涩涩-雅俗共赏.zip"
        else:
            zip_filename = "每日涩涩-快乐齐天.zip"
        
        # 使用统一的ZIP输出目录
        output_dir = Config.ZIP_OUTPUT_DIR
        
        # 创建分类子目录
        category = 'pictures' if content_type == 'pic' else 'literature'
        category_dir = os.path.join(output_dir, category)
        file_utils.create_directory(category_dir)
        
        # 构建完整的输出路径
        output_path = os.path.join(category_dir, zip_filename)
        
        # 执行打包
        success, file_count, total_size = optimized_zipper.zip_directory(source_dir, output_path)
        
        if success:
            logger.info(f"打包完成，生成ZIP文件: {output_path}")
            # 记录创建的ZIP文件路径
            with open(os.path.join(script_dir, 'created_zips.txt'), 'w', encoding='utf-8') as f:
                # 转换为相对路径，便于GitHub Actions使用
                rel_path = os.path.relpath(output_path)
                f.write(f"{rel_path}\n")
        else:
            logger.warning("打包失败，没有生成ZIP文件")

    @staticmethod
    def main():
        """主函数"""
        try:
            # 解析命令行参数
            args = CrawlerMain.parse_arguments()
            
            # 创建必要的目录
            file_utils.create_directory(Config.PIC_DIR)
            file_utils.create_directory(Config.LITERATURE_DIR)
            file_utils.create_directory(Config.ZIP_OUTPUT_DIR)
            file_utils.create_directory(Config.LOG_DIR)
            
            # 根据模式执行不同的爬虫任务
            if args.mode == 'manual':
                CrawlerMain.run_manual_mode(args)
            elif args.mode == 'auto':
                CrawlerMain.run_auto_mode(args)
            elif args.mode == 'github_actions':
                CrawlerMain.run_github_actions_mode(args)
            elif args.mode == 'literature':
                CrawlerMain.run_literature_crawler(args)
            elif args.mode == 'pic':
                CrawlerMain.run_pic_crawler(args)
            
            logger.info("爬虫任务已完成")
            return 0
        except KeyboardInterrupt:
            logger.info("用户中断爬虫任务")
            return 1
        except Exception as e:
            logger.exception("爬虫任务发生错误")
            return 2

if __name__ == '__main__':
    sys.exit(CrawlerMain.main())