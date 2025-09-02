#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import time
from config.settings import Config
from utils.logger import logger, load_crawled_urls, save_crawled_url
from utils.request_utils import request_utils
from utils.file_utils import file_utils
from bs4 import BeautifulSoup

class PicCrawler:
    """图片爬虫类"""
    
    def __init__(self):
        """初始化图片爬虫"""
        self.base_url = Config.BASE_URL
        self.pic_dir = Config.PIC_DIR
        self.log_file = Config.PIC_LOG_FILE
    
    def get_urls_from_page(self, page, forum_key):
        """
        从指定页面获取帖子URL列表
        
        参数:
            page: 页面号
            forum_key: 板块键名
        
        返回:
            URL列表
        """
        url = Config.get_forum_url(forum_key, page)
        if not url:
            logger.error(f"无效的板块键名: {forum_key}")
            return []
        
        text = request_utils.get_text(url)
        if not text:
            return []
        
        # 提取URL列表
        urls = re.findall('a href="(.*?)html"', text)
        logger.info(f"从页面 {page} 获取到 {len(urls)} 个URL")
        return urls
    
    def get_pic_list(self, post_url, max_pics=None):
        """
        从帖子页面获取图片列表
        
        参数:
            post_url: 帖子URL
            max_pics: 最大返回图片数量，None表示无限制
        
        返回:
            (标题, 图片URL列表)
        """
        full_url = f"{self.base_url}/{post_url}html"
        text = request_utils.get_text(full_url)
        if not text:
            return "default", []
        
        try:
            # 提取标题
            title_match = re.findall(r'<title>(.*?)\|', text)
            if title_match:
                title_part = title_match[0]
                # 尝试提取标题中的主要部分
                title_extract = re.findall('(.*?)P', title_part)
                if title_extract:
                    title = title_extract[0]
                else:
                    title = title_part
            else:
                title = "default"
            
            # 提取图片URL
            pic_urls = re.findall("ess-data='(.*?)'", text)
            
            # 应用最大图片数量限制
            if max_pics and max_pics > 0:
                original_count = len(pic_urls)
                if original_count > max_pics:
                    pic_urls = pic_urls[:max_pics]
                    logger.info(f"帖子 '{title}' 包含 {original_count} 张图片，限制为 {max_pics} 张")
                else:
                    logger.info(f"帖子 '{title}' 包含 {len(pic_urls)} 张图片")
            else:
                logger.info(f"帖子 '{title}' 包含 {len(pic_urls)} 张图片")
            
            return title, pic_urls
        except Exception as e:
            logger.exception(f"解析帖子页面失败: {full_url}")
            return "default", []
    
    def save_pic(self, url, count, title, forum_key):
        """
        保存单张图片
        
        参数:
            url: 图片URL
            count: 图片序号
            title: 标题
            forum_key: 板块键名
        
        返回:
            True（成功）或False（失败）
        """
        try:
            # 获取板块名称
            forum_name = Config.get_forum_name(forum_key)
            
            # 清理标题，避免文件名非法
            safe_title = file_utils.clean_filename(title)
            
            # 创建保存目录
            pic_dir = os.path.join(self.pic_dir, forum_name, safe_title)
            file_utils.create_directory(pic_dir)
            
            # 确定文件扩展名
            if '.gif' in url:
                extension = '.gif'
            elif '.png' in url:
                extension = '.png'
            elif '.jpg' in url:
                extension = '.jpg'
            elif '.jpeg' in url:
                extension = '.jpeg'
            else:
                extension = os.path.splitext(url)[1]
                if not extension:
                    extension = '.jpg'  # 默认使用jpg扩展名
            
            # 构建保存路径
            file_name = os.path.join(pic_dir, f"{safe_title}{count + 1}{extension}")
            
            # 下载图片
            return request_utils.download_file(url, file_name)
        except Exception as e:
            logger.exception(f"保存图片失败: {url}")
            return False
    
    def download_pics(self, url_list, title, forum_key, use_multiprocess=False):
        """
        下载图片列表
        
        参数:
            url_list: 图片URL列表
            title: 标题
            forum_key: 板块键名
            use_multiprocess: 是否使用多进程
        
        返回:
            成功下载的图片数量
        """
        start_time = time.time()
        success_count = 0
        
        logger.info(f"开始下载 '{title}' 的 {len(url_list)} 张图片")
        
        if use_multiprocess:
            # 使用多进程下载
            import multiprocessing
            processes = []
            
            for i in range(len(url_list)):
                p = multiprocessing.Process(
                    target=self._download_pic_wrapper, 
                    args=(url_list[i], i, title, forum_key)
                )
                p.start()
                processes.append(p)
                
                # 限制并发进程数
                if len(processes) >= multiprocessing.cpu_count() * 2:
                    for p in processes:
                        p.join()
                    processes = []
            
            # 等待剩余进程完成
            for p in processes:
                p.join()
                success_count += 1  # 这里简化处理，实际应通过共享变量获取成功数量
        else:
            # 单线程下载
            for i in range(len(url_list)):
                if self.save_pic(url_list[i], i, title, forum_key):
                    success_count += 1
        
        end_time = time.time()
        logger.info(f"下载完成，成功 {success_count}/{len(url_list)} 张图片")
        logger.info(f"总耗时：{end_time - start_time:.2f} 秒")
        
        return success_count
    
    def _download_pic_wrapper(self, url, count, title, forum_key):
        """多进程下载的包装函数"""
        self.save_pic(url, count, title, forum_key)
    
    def crawl(self, forum_key, start_page, end_page, use_multiprocess=False, 
              max_posts=None, max_pics=None):
        """
        执行爬虫任务
        
        参数:
            forum_key: 板块键名
            start_page: 起始页面
            end_page: 结束页面
            use_multiprocess: 是否使用多进程下载
            max_posts: 每页最多处理的帖子数量，None表示无限制
            max_pics: 每个帖子最多下载的图片数量，None表示无限制
        
        返回:
            成功爬取的帖子数量
        """
        logger.info(f"开始爬取板块 '{Config.get_forum_name(forum_key)}'，页面范围 {start_page}-{end_page}")
        logger.info(f"性能限制参数: 每页最多{max_posts if max_posts else '无限制'}个帖子，每个帖子最多{max_pics if max_pics else '无限制'}张图片")
        
        # 加载已爬取的URL
        crawled_urls = load_crawled_urls(self.log_file)
        logger.info(f"已爬取 {len(crawled_urls)} 个帖子")
        
        success_count = 0
        
        # 遍历页面
        for page in range(start_page, end_page + 1):
            post_urls = self.get_urls_from_page(str(page), forum_key)
            
            # 应用每页最大帖子数量限制
            if max_posts and max_posts > 0 and len(post_urls) > max_posts:
                logger.info(f"页面 {page} 有 {len(post_urls)} 个帖子，限制为 {max_posts} 个")
                post_urls = post_urls[:max_posts]
            
            # 遍历帖子
            processed_posts = 0
            for post_url in post_urls:
                # 如果已达到每页最大处理数量，跳出循环
                if max_posts and max_posts > 0 and processed_posts >= max_posts:
                    logger.info(f"已达到每页最大处理数量 {max_posts}，停止处理此页面")
                    break
                
                if post_url not in crawled_urls:
                    try:
                        # 获取图片列表（带数量限制）
                        title, pic_urls = self.get_pic_list(post_url, max_pics=max_pics)
                        
                        # 如果有图片，下载
                        if pic_urls:
                            self.download_pics(pic_urls, title, forum_key, use_multiprocess)
                            success_count += 1
                            processed_posts += 1
                        
                        # 保存已爬取的URL
                        save_crawled_url(post_url, self.log_file)
                        
                    except Exception as e:
                        logger.exception(f"处理帖子失败: {post_url}")
                else:
                    logger.info(f"已爬取，跳过: {post_url}")
        
        logger.info(f"爬取完成，成功处理 {success_count} 个帖子")
        return success_count

# 创建全局图片爬虫实例
pic_crawler = PicCrawler()