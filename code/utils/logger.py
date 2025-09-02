import os
import logging
from datetime import datetime
from config.settings import Config

class Logger:
    """日志记录工具类"""
    
    def __init__(self, log_file=None, log_name='caoliu_scraper'):
        """
        初始化日志记录器
        
        参数:
            log_file: 日志文件路径，如果为None则只输出到控制台
            log_name: 日志记录器名称
        """
        # 创建日志记录器
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.INFO)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            # 创建格式化器
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # 创建控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
            # 如果指定了日志文件，创建文件处理器
            if log_file:
                # 确保日志目录存在
                log_dir = os.path.dirname(log_file)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir, exist_ok=True)
                
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(logging.INFO)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
    
    def info(self, message):
        """记录信息日志"""
        self.logger.info(message)
    
    def warning(self, message):
        """记录警告日志"""
        self.logger.warning(message)
    
    def error(self, message):
        """记录错误日志"""
        self.logger.error(message)
    
    def exception(self, message, exc_info=True):
        """记录异常日志"""
        self.logger.exception(message, exc_info=exc_info)

# 创建全局日志实例
def get_logger(log_file=None, log_name='caoliu_scraper'):
    """获取日志记录器实例"""
    return Logger(log_file, log_name).logger

# 创建默认日志记录器
# 使用配置中的日志目录和当前日期作为日志文件名
default_log_file = os.path.join(Config.LOG_DIR, f"scraper_{datetime.now().strftime('%Y%m%d')}.log")
logger = get_logger(log_file=default_log_file)

# 已爬取URL记录相关函数
def load_crawled_urls(log_file):
    """从日志文件加载已爬取的URL列表"""
    crawled = []
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as file:
                for line in file:
                    stripped_line = line.strip()
                    if stripped_line:
                        crawled.append(stripped_line)
    except Exception as e:
        logger.error(f"加载已爬取URL失败: {e}")
    return crawled

def save_crawled_url(url, log_file):
    """保存已爬取的URL到日志文件"""
    try:
        with open(log_file, 'a', encoding='utf-8') as file:
            file.write(url + '\n')
        return True
    except Exception as e:
        logger.error(f"保存已爬取URL失败: {e}")
        return False