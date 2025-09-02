import os
import requests
from fake_useragent import UserAgent
from config.settings import Config
from utils.logger import logger
import time

class RequestUtils:
    """网络请求工具类"""
    
    def __init__(self):
        """初始化请求工具"""
        # 初始化UserAgent生成器
        self.ua = UserAgent()
        # 默认请求头
        self.headers = Config.HEADERS.copy()
        # 添加随机User-Agent
        self.headers['User-Agent'] = self.ua.random
    
    def get(self, url, headers=None, timeout=30, retry=Config.MAX_RETRY, delay=Config.DOWNLOAD_DELAY, **kwargs):
        """
        发送GET请求，支持重试和延迟
        
        参数:
            url: 请求URL
            headers: 自定义请求头
            timeout: 超时时间（秒）
            retry: 重试次数
            delay: 请求延迟（秒）
            **kwargs: 传递给requests.get的其他参数
        
        返回:
            response对象或None（如果请求失败）
        """
        # 合并请求头
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)
        
        # 添加请求延迟
        time.sleep(delay)
        
        # 发送请求，支持重试
        for attempt in range(retry + 1):
            try:
                logger.info(f"请求URL: {url} (尝试 {attempt + 1}/{retry + 1})")
                response = requests.get(url, headers=request_headers, timeout=timeout, **kwargs)
                response.raise_for_status()  # 抛出HTTP错误
                logger.info(f"请求成功: {url}")
                return response
            except requests.exceptions.RequestException as e:
                error_msg = f"请求失败: {url}, 错误: {str(e)}"
                if attempt < retry:
                    logger.warning(f"{error_msg}, {delay}秒后重试...")
                    time.sleep(delay)
                else:
                    logger.error(f"{error_msg}, 已达到最大重试次数")
        
        return None
    
    def get_text(self, url, encoding=None, **kwargs):
        """
        获取URL的文本内容
        
        参数:
            url: 请求URL
            encoding: 文本编码，如果为None则自动检测
            **kwargs: 传递给get方法的其他参数
        
        返回:
            文本内容或None（如果请求失败）
        """
        response = self.get(url, **kwargs)
        if response:
            try:
                if encoding:
                    response.encoding = encoding
                else:
                    # 尝试自动检测编码
                    if not response.encoding or response.encoding == 'ISO-8859-1':
                        # 使用chardet库检测编码
                        import chardet
                        detected_encoding = chardet.detect(response.content)['encoding']
                        if detected_encoding:
                            response.encoding = detected_encoding
                return response.text
            except Exception as e:
                logger.error(f"解析文本失败: {url}, 错误: {e}")
        return None
    
    def download_file(self, url, save_path, **kwargs):
        """
        下载文件并保存到指定路径
        
        参数:
            url: 文件URL
            save_path: 保存路径
            **kwargs: 传递给get方法的其他参数
        
        返回:
            True（成功）或False（失败）
        """
        response = self.get(url, stream=True, **kwargs)
        if response:
            try:
                # 确保保存目录存在
                save_dir = os.path.dirname(save_path)
                if save_dir and not os.path.exists(save_dir):
                    os.makedirs(save_dir, exist_ok=True)
                
                # 下载文件
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                logger.info(f"文件下载成功: {save_path}")
                return True
            except Exception as e:
                logger.error(f"文件下载失败: {save_path}, 错误: {e}")
                # 清理失败的文件
                if os.path.exists(save_path):
                    os.remove(save_path)
        return False

# 创建全局请求工具实例
request_utils = RequestUtils()