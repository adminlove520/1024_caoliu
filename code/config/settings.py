import os
from datetime import datetime

# 获取当前脚本所在目录的绝对路径
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Config:
    """项目全局配置类"""
    
    # 网站URL配置
    BASE_URL = 'https://t66y.com'
    
    # 板块配置
    FORUMS = {
        'pics': {
            'fid': '7',
            'name': '技术交流',
            'url_template': '{base}/thread0806.php?fid=7&search=&page={page}'
        },
        'new_era': {
            'fid': '8',
            'name': '新時代的我們',
            'url_template': '{base}/thread0806.php?fid=8&search=&page={page}'
        },
        'daguerre_flag': {
            'fid': '16',
            'name': '達蓋爾的旗幟',
            'url_template': '{base}/thread0806.php?fid=16&search=&page={page}'
        },
        'literature': {
            'fid': '20',
            'name': '文学',
            'url_template': '{base}/thread0806.php?fid=20&search=&page={page}'
        },
        'story': {
            'fid': '2',
            'name': '故事',
            'url_template': '{base}/thread0806.php?fid=2&search=&page={page}'
        },
        'poem': {
            'fid': '3',
            'name': '诗歌',
            'url_template': '{base}/thread0806.php?fid=3&search=&page={page}'
        }
    }
    
    # 文件路径配置
    LITERATURE_DIR = os.path.join(base_dir, 'literature')  # 使用英文目录名
    PIC_DIR = os.path.join(base_dir, 'pic')
    ZIP_OUTPUT_DIR = os.path.join(base_dir, 'zips')  # 统一的ZIP输出目录
    LOG_DIR = os.path.join(base_dir, 'logs')
    
    # 日志文件路径
    PIC_LOG_FILE = os.path.join(LOG_DIR, 'pic_crawled.log')
    LITERATURE_LOG_FILE = os.path.join(LOG_DIR, 'literature_crawled.log')
    
    # 请求头配置
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # 爬取配置
    DEFAULT_PAGE_RANGE = (1, 2)  # 默认爬取页面范围
    DOWNLOAD_DELAY = 1  # 下载延迟（秒）
    MAX_RETRY = 3  # 最大重试次数
    
    # ZIP打包配置
    ZIP_CHUNK_SIZE = 10 * 1024 * 1024  # 10MB分块大小
    
    @staticmethod
    def get_forum_url(forum_key, page):
        """获取指定板块和页面的URL"""
        if forum_key in Config.FORUMS:
            config = Config.FORUMS[forum_key]
            return config['url_template'].format(base=Config.BASE_URL, page=page)
        return None
    
    @staticmethod
    def get_forum_name(forum_key):
        """获取板块名称"""
        if forum_key in Config.FORUMS:
            return Config.FORUMS[forum_key]['name']
        return '其他'
    
    @staticmethod
    def get_today_zip_filename(prefix):
        """获取包含当前日期和时间的ZIP文件名"""
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{prefix}_{current_time}.zip"
    
    @staticmethod
    def get_today_date_string():
        """获取当前日期字符串（YYYYMMDD格式）"""
        return datetime.now().strftime('%Y%m%d')

# 确保必要的目录存在
for dir_path in [
    Config.LITERATURE_DIR,
    Config.PIC_DIR,
    Config.ZIP_OUTPUT_DIR,
    Config.LOG_DIR
]:
    os.makedirs(dir_path, exist_ok=True)