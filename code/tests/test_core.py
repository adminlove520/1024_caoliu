#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Config
from utils.logger import logger
from utils.file_utils import file_utils
from core.pic_crawler import pic_crawler
from core.literature_crawler import literature_crawler

class TestCoreModules(unittest.TestCase):
    """测试核心模块的基本功能"""
    
    def setUp(self):
        """每个测试用例执行前的设置"""
        self.test_forum_key = 'pics'
        self.test_page = 1
        
        # 创建临时测试目录
        self.test_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tests', 'test_data')
        file_utils.create_directory(self.test_dir)
    
    def tearDown(self):
        """每个测试用例执行后的清理"""
        # 清理临时测试目录
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir)
    
    @patch('utils.request_utils.request_utils.get_text')
    def test_pic_crawler_get_urls(self, mock_get_text):
        """测试图片爬虫获取URL列表的功能"""
        # 模拟网页内容
        mock_html = '<a href="thread-123456-1-1.html">测试帖子</a><a href="thread-654321-1-1.html">另一个测试帖子</a>'
        mock_get_text.return_value = mock_html
        
        # 调用函数
        urls = pic_crawler.get_urls_from_page(self.test_page, self.test_forum_key)
        
        # 验证结果
        self.assertEqual(len(urls), 2)
        self.assertTrue(any('thread-123456-1-1' in url for url in urls))
        self.assertTrue(any('thread-654321-1-1' in url for url in urls))
    
    @patch('utils.request_utils.request_utils.get_text')
    def test_literature_crawler_get_urls(self, mock_get_text):
        """测试文学爬虫获取URL列表的功能"""
        # 模拟网页内容
        mock_html = '<a href="thread-111111-1-1.html">文学帖子</a><a href="thread-222222-1-1.html">另一个文学帖子</a>'
        mock_get_text.return_value = mock_html
        
        # 调用函数
        urls = literature_crawler.get_urls_from_page(self.test_page, 'literature')
        
        # 验证结果
        self.assertEqual(len(urls), 2)
        self.assertTrue(any('thread-111111-1-1' in url for url in urls))
        self.assertTrue(any('thread-222222-1-1' in url for url in urls))
    
    @patch('utils.request_utils.request_utils.download_file')
    def test_save_pic(self, mock_download_file):
        """测试保存图片的功能"""
        # 配置模拟返回值
        mock_download_file.return_value = True
        
        # 调用函数
        result = pic_crawler.save_pic('https://example.com/test.jpg', 0, 'test_title', self.test_forum_key)
        
        # 验证结果
        self.assertTrue(result)
        mock_download_file.assert_called_once()
    
    def test_config_settings(self):
        """测试配置设置的有效性"""
        # 验证基本配置项存在
        self.assertTrue(hasattr(Config, 'BASE_URL'))
        self.assertTrue(hasattr(Config, 'FORUMS'))
        self.assertTrue(hasattr(Config, 'PIC_DIR'))
        
        # 验证板块配置有效
        self.assertIn('pics', Config.FORUMS)
        self.assertIn('literature', Config.FORUMS)
        
        # 验证方法功能
        forum_name = Config.get_forum_name('pics')
        self.assertIsNotNone(forum_name)
        
        forum_url = Config.get_forum_url('pics', 1)
        self.assertIsNotNone(forum_url)
        self.assertIn('page=1', forum_url)
    
    def test_file_utils(self):
        """测试文件工具的基本功能"""
        # 测试目录创建
        test_path = os.path.join(self.test_dir, 'test_subdir')
        file_utils.create_directory(test_path)
        self.assertTrue(os.path.exists(test_path))
        
        # 测试文件名清理
        dirty_name = "test/title*with?illegal\"chars<.txt>"
        clean_name = file_utils.clean_filename(dirty_name)
        self.assertNotIn('/', clean_name)
        self.assertNotIn('*', clean_name)
        self.assertNotIn('?', clean_name)
        self.assertNotIn('"', clean_name)
        self.assertNotIn('<', clean_name)
        self.assertNotIn('>', clean_name)
        self.assertNotIn('|', clean_name)

if __name__ == '__main__':
    unittest.main()