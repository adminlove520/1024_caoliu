#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import time
from bs4 import BeautifulSoup
from config.settings import Config
from utils.logger import logger, load_crawled_urls, save_crawled_url
from utils.request_utils import request_utils
from utils.file_utils import file_utils

class LiteratureCrawler:
    """文学爬虫类"""
    
    def __init__(self):
        """初始化文学爬虫"""
        self.base_url = Config.BASE_URL
        self.literature_dir = Config.LITERATURE_DIR
        self.log_file = Config.LITERATURE_LOG_FILE
    
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
    
    def get_literature_content(self, post_url):
        """
        从帖子页面获取文学内容
        
        参数:
            post_url: 帖子URL
        
        返回:
            (标题, 作者, 内容)
        """
        full_url = f"{self.base_url}/{post_url}html"
        text = request_utils.get_text(full_url)
        if not text:
            return "default", "未知作者", ""
        
        try:
            soup = BeautifulSoup(text, 'html.parser')
            
            # 提取标题
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text()
                # 清理标题
                title = re.sub(r'\|.*$', '', title)
                title = re.sub(r'【.*?】', '', title)
                title = title.strip()
            else:
                title = "default"
            
            # 尝试提取作者信息
            author = "未知作者"
            # 这里可以添加提取作者的逻辑，根据具体网页结构调整
            
            # 提取内容
            content = ""
            # 查找内容区域，根据具体网页结构调整
            content_divs = soup.find_all('div')
            for div in content_divs:
                # 查找可能的内容区域
                if 'id' in div.attrs and 'body' in div['id']:
                    paragraphs = div.find_all('p')
                    for p in paragraphs:
                        content += p.get_text() + '\n\n'
                    break
            
            # 如果没有找到内容，尝试另一种方式
            if not content:
                # 这是一个备选方案，根据实际情况调整
                content_match = re.findall(r'postmessage_.*?>(.*?)<\/td>', text, re.DOTALL)
                if content_match:
                    content_html = content_match[0]
                    content_soup = BeautifulSoup(content_html, 'html.parser')
                    content = content_soup.get_text()
            
            # 清理内容
            content = re.sub(r'\n{3,}', '\n\n', content)  # 移除多余的空行
            content = content.strip()
            
            return title, author, content
        except Exception as e:
            logger.exception(f"解析文学内容失败: {full_url}")
            return "default", "未知作者", ""
    
    def save_literature(self, title, author, content, forum_key):
        """
        保存文学内容到文件
        
        参数:
            title: 标题
            author: 作者
            content: 内容
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
            literature_dir = os.path.join(self.literature_dir, forum_name)
            file_utils.create_directory(literature_dir)
            
            # 构建保存路径
            file_name = os.path.join(literature_dir, f"{safe_title}.txt")
            
            # 格式化内容
            formatted_content = f"标题：{title}\n"
            formatted_content += f"作者：{author}\n"
            formatted_content += f"\n{content}\n"
            
            # 写入文件
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            
            logger.info(f"成功保存文学作品：{file_name}")
            return True
        except Exception as e:
            logger.exception(f"保存文学内容失败: {title}")
            return False
    
    def crawl(self, forum_key, start_page, end_page, max_posts=None):
        """
        执行文学爬虫任务
        
        参数:
            forum_key: 板块键名
            start_page: 起始页面
            end_page: 结束页面
            max_posts: 每页最多处理的帖子数量，None表示无限制
        
        返回:
            成功爬取的帖子数量
        """
        logger.info(f"开始爬取文学板块 '{Config.get_forum_name(forum_key)}'，页面范围 {start_page}-{end_page}")
        logger.info(f"性能限制参数: 每页最多{max_posts if max_posts else '无限制'}个帖子")
        
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
                        # 获取文学内容
                        title, author, content = self.get_literature_content(post_url)
                        
                        # 如果有内容，保存
                        if content:
                            if self.save_literature(title, author, content, forum_key):
                                success_count += 1
                                processed_posts += 1
                        
                        # 保存已爬取的URL
                        save_crawled_url(post_url, self.log_file)
                        
                    except Exception as e:
                        logger.exception(f"处理文学帖子失败: {post_url}")
                else:
                    logger.info(f"已爬取，跳过: {post_url}")
        
        logger.info(f"爬取完成，成功处理 {success_count} 个文学帖子")
        return success_count

# 创建全局文学爬虫实例
literature_crawler = LiteratureCrawler()