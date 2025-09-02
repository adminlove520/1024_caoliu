import re
import os
import time
from config.settings import Config
from utils.logger import logger, load_crawled_urls, save_crawled_url
from utils.request_utils import request_utils
from utils.file_utils import file_utils
from bs4 import BeautifulSoup

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
            return "default", "unknown", ""
        
        try:
            soup = BeautifulSoup(text, 'html.parser')
            
            # 提取标题
            title_tag = soup.find('h4')
            if title_tag:
                title = title_tag.text.strip()
                # 清理标题
                title = re.sub(r'\s+', ' ', title)
                title = re.sub(r'^\d+\.', '', title)  # 移除开头的数字编号
                title = title.strip()
            else:
                title = "default"
            
            # 提取作者信息
            author = "unknown"
            author_tag = soup.find('div', class_='postinfo')
            if author_tag:
                author_match = re.search(r'作者: ([^<]+)', str(author_tag))
                if author_match:
                    author = author_match.group(1)
            
            # 提取正文内容
            content = ""
            content_tag = soup.find('div', class_='t t2')
            if content_tag:
                # 移除所有script标签
                for script in content_tag(['script', 'style']):
                    script.decompose()
                
                # 获取纯文本内容
                content = content_tag.get_text()
                # 清理内容
                content = re.sub(r'\s+', '\n', content)  # 连续空白替换为换行
                content = re.sub(r'\n{3,}', '\n\n', content)  # 多个换行替换为两个换行
                content = content.strip()
            
            logger.info(f"获取帖子内容成功: '{title}'")
            return title, author, content
        except Exception as e:
            logger.exception(f"解析帖子页面失败: {full_url}")
            return "default", "unknown", ""
    
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
            if not safe_title or len(safe_title) > 100:
                safe_title = f"{forum_key}_{int(time.time())}"
            
            # 创建保存目录
            literature_dir = os.path.join(self.literature_dir, forum_name)
            file_utils.create_directory(literature_dir)
            
            # 构建保存路径
            file_name = os.path.join(literature_dir, f"{safe_title}.txt")
            
            # 写入文件
            with open(file_name, 'w', encoding='utf-8') as f:
                if author:
                    f.write(f"作者: {author}\n\n")
                if title:
                    f.write(f"标题: {title}\n\n")
                if content:
                    f.write(content)
            
            logger.info(f"保存文学文件成功: {file_name}")
            return True
        except Exception as e:
            logger.exception(f"保存文学文件失败: {safe_title}.txt")
            return False
    
    def crawl(self, forum_key, start_page, end_page):
        """
        执行爬虫任务
        
        参数:
            forum_key: 板块键名
            start_page: 起始页面
            end_page: 结束页面
        
        返回:
            成功爬取的帖子数量
        """
        logger.info(f"开始爬取板块 '{Config.get_forum_name(forum_key)}'，页面范围 {start_page}-{end_page}")
        
        # 加载已爬取的URL
        crawled_urls = load_crawled_urls(self.log_file)
        logger.info(f"已爬取 {len(crawled_urls)} 个帖子")
        
        success_count = 0
        
        # 遍历页面
        for page in range(start_page, end_page + 1):
            post_urls = self.get_urls_from_page(str(page), forum_key)
            
            # 遍历帖子
            for post_url in post_urls:
                if post_url not in crawled_urls:
                    try:
                        # 获取文学内容
                        title, author, content = self.get_literature_content(post_url)
                        
                        # 如果有内容，保存
                        if content and len(content) > 50:
                            if self.save_literature(title, author, content, forum_key):
                                success_count += 1
                        
                        # 保存已爬取的URL
                        save_crawled_url(post_url, self.log_file)
                        
                    except Exception as e:
                        logger.exception(f"处理帖子失败: {post_url}")
                else:
                    logger.info(f"已爬取，跳过: {post_url}")
        
        logger.info(f"爬取完成，成功处理 {success_count} 个帖子")
        return success_count

# 创建全局文学爬虫实例
literature_crawler = LiteratureCrawler()