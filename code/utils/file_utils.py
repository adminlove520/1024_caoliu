import os
import shutil
import zipfile
import time
from datetime import datetime
from config.settings import Config
from utils.logger import logger

class FileUtils:
    """文件操作工具类"""
    
    @staticmethod
    def is_directory_empty(directory):
        """检查目录是否为空"""
        try:
            for _, dirs, files in os.walk(directory):
                if files or dirs:
                    return False
            return True
        except Exception as e:
            logger.error(f"检查目录是否为空失败: {directory}, 错误: {e}")
            return True  # 默认认为空目录以避免打包错误
    
    @staticmethod
    def create_directory(path):
        """创建目录，如果已存在则忽略"""
        try:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                logger.info(f"目录创建成功: {path}")
            return True
        except Exception as e:
            logger.error(f"目录创建失败: {path}, 错误: {e}")
            return False
    
    @staticmethod
    def clean_filename(filename):
        """清理文件名中的非法字符"""
        import re
        # 移除Windows文件系统中的非法字符
        return re.sub(re.compile(r'[/:*?"<>|]'), '', filename)

class OptimizedZipper:
    """优化的ZIP打包工具类"""
    
    def __init__(self, chunk_size=Config.ZIP_CHUNK_SIZE):
        """初始化ZIP打包器"""
        self.chunk_size = chunk_size
    
    def add_file_to_zip(self, zipf, file_path, arcname):
        """将文件添加到zip文件中"""
        try:
            zipf.write(file_path, arcname)
            return True
        except Exception as e:
            logger.error(f"添加文件失败 {file_path}: {e}")
            return False
    
    def zip_directory(self, source_dir, output_path, exclude_empty_dirs=True):
        """
        优化的目录打包函数
        
        参数:
            source_dir: 源目录路径
            output_path: 输出ZIP文件路径
            exclude_empty_dirs: 是否排除空目录
        
        返回:
            (success, file_count, total_size)
        """
        start_time = time.time()
        total_files = 0
        total_size = 0
        
        # 创建父目录（如果不存在）
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            FileUtils.create_directory(output_dir)
        
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 遍历源目录
                for root, dirs, files in os.walk(source_dir):
                    # 检查当前目录是否为空且需要排除
                    if exclude_empty_dirs and not files and not dirs:
                        continue
                    
                    # 添加文件
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_dir)
                        
                        if self.add_file_to_zip(zipf, file_path, arcname):
                            total_files += 1
                            total_size += os.path.getsize(file_path)
                            
                            # 打印进度信息
                            if total_files % 100 == 0:
                                logger.info(f"已处理 {total_files} 个文件，总大小: {total_size/1024/1024:.2f} MB")
        except Exception as e:
            logger.error(f"打包过程出错: {e}")
            return False, 0, 0
        
        end_time = time.time()
        logger.info(f"打包完成: {output_path}")
        logger.info(f"总文件数: {total_files}")
        logger.info(f"总大小: {total_size/1024/1024:.2f} MB")
        logger.info(f"耗时: {end_time - start_time:.2f} 秒")
        
        return True, total_files, total_size
    
    def create_optimized_zips(self, target_dirs, output_base_dir):
        """
        为多个目录创建优化的zip文件
        
        参数:
            target_dirs: 目标目录列表
            output_base_dir: 输出基础目录
        
        返回:
            结果列表 [(dir_path, success, file_count, total_size), ...]
        """
        results = []
        
        for source_dir in target_dirs:
            if not os.path.exists(source_dir):
                logger.warning(f"源目录不存在: {source_dir}")
                results.append((source_dir, False, 0, 0))
                continue
            
            # 检查目录是否为空
            if FileUtils.is_directory_empty(source_dir):
                logger.warning(f"源目录为空: {source_dir}")
                results.append((source_dir, False, 0, 0))
                continue
            
            # 创建输出文件名
            dir_name = os.path.basename(source_dir)
            zip_filename = Config.get_today_zip_filename(dir_name)
            
            # 确定输出路径
            # 使用统一的ZIP输出目录
            output_dir = Config.ZIP_OUTPUT_DIR
            
            # 创建分类子目录
            # 尝试确定分类
            category = "other"
            # 检查是否是文学内容
            if "literature" in source_dir.lower():
                category = "literature"
            # 否则检查是否匹配论坛板块
            else:
                for forum_key, forum_info in Config.FORUMS.items():
                    if forum_info['name'] in source_dir or forum_key in source_dir:
                        category = forum_key
                        break
                         
            # 创建分类目录
            category_dir = os.path.join(output_dir, category)
            FileUtils.create_directory(category_dir)
            
            output_path = os.path.join(category_dir, zip_filename)
            
            # 创建zip文件
            success, file_count, total_size = self.zip_directory(source_dir, output_path)
            results.append((source_dir, success, file_count, total_size))
        
        return results

# 创建全局文件工具实例
file_utils = FileUtils()
optimized_zipper = OptimizedZipper()