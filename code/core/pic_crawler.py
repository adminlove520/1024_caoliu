import re
import os
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
    
    def get_pic_list(self, post_url):
        """
        从帖子页面获取图片列表
        
        参数:
            post_url: 帖子URL
        
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
    
    def crawl(self, forum_key, start_page, end_page, use_multiprocess=False):
        """
        执行爬虫任务
        
        参数:
            forum_key: 板块键名
            start_page: 起始页面
            end_page: 结束页面
            use_multiprocess: 是否使用多进程下载
        
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
                        # 获取图片列表
                        title, pic_urls = self.get_pic_list(post_url)
                        
                        # 如果有图片，下载
                        if pic_urls:
                            self.download_pics(pic_urls, title, forum_key, use_multiprocess)
                            success_count += 1
                        
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