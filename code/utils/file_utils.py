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
    
    # 分卷大小：2GB (GitHub单个文件上传限制)
    VOLUME_SIZE = 2 * 1024 * 1024 * 1024  # 2GB
    
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
    
    def get_file_sizes(self, directory):
        """获取目录中所有文件的大小"""
        total_size = 0
        file_sizes = []
        
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    file_sizes.append((file_path, file_size))
                except (OSError, PermissionError) as e:
                    logger.warning(f"无法获取文件大小: {file_path}, 错误: {e}")
        
        return total_size, file_sizes
    
    def should_use_volume_packaging(self, total_size, file_sizes):
        """判断是否应该使用分卷打包"""
        # 如果总大小超过2GB或者有单个文件超过2GB，使用分卷打包
        if total_size > OptimizedZipper.VOLUME_SIZE:
            return True
        
        # 检查是否有单个文件超过2GB
        for _, file_size in file_sizes:
            if file_size > OptimizedZipper.VOLUME_SIZE:
                return True
        
        return False
    
    def create_volume_zip(self, output_path, file_groups, base_dir):
        """创建分卷ZIP文件"""
        volume_paths = []
        
        for i, file_group in enumerate(file_groups):
            # 创建分卷文件名，如：xxx_part1.zip
            volume_name = f"{os.path.splitext(output_path)[0]}_part{i+1}.zip"
            volume_paths.append(volume_name)
            
            logger.info(f"开始创建分卷 {i+1}/{len(file_groups)}: {volume_name}")
            start_time = time.time()
            
            try:
                with zipfile.ZipFile(volume_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    current_size = 0
                    
                    for file_path, file_size in file_group:
                        # 计算相对路径
                        rel_path = os.path.relpath(file_path, base_dir)
                        
                        # 添加文件到ZIP
                        if self.add_file_to_zip(zipf, file_path, rel_path):
                            current_size += file_size
                            
                            # 记录进度
                            if current_size % 50000000 < file_size:  # 每50MB记录一次
                                logger.info(f"  已添加: {rel_path} ({file_size/1024/1024:.2f}MB)")
            except Exception as e:
                logger.error(f"创建分卷 {volume_name} 失败: {e}")
                return False, [], 0
            
            elapsed_time = time.time() - start_time
            volume_size = os.path.getsize(volume_name) if os.path.exists(volume_name) else 0
            logger.info(f"分卷 {i+1} 创建完成，耗时: {elapsed_time:.2f}秒, 大小: {volume_size/1024/1024:.2f}MB")
        
        # 创建分卷信息文件
        info_file = f"{os.path.splitext(output_path)[0]}_volume_info.txt"
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write(f"总卷数: {len(volume_paths)}\n")
            for i, path in enumerate(volume_paths):
                f.write(f"分卷 {i+1}: {os.path.basename(path)}\n")
            f.write(f"创建时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        return True, volume_paths, len(volume_paths)
    
    def group_files_for_volume(self, file_sizes):
        """将文件分组以适应分卷大小"""
        file_groups = []
        current_group = []
        current_size = 0
        
        # 对文件按大小降序排序，优先处理大文件
        sorted_files = sorted(file_sizes, key=lambda x: x[1], reverse=True)
        
        for file_path, file_size in sorted_files:
            # 如果单个文件超过分卷大小，单独创建一个分卷
            if file_size > OptimizedZipper.VOLUME_SIZE:
                if current_group:
                    file_groups.append(current_group)
                    current_group = []
                    current_size = 0
                file_groups.append([(file_path, file_size)])
            else:
                # 检查添加当前文件是否超过分卷大小
                if current_size + file_size > OptimizedZipper.VOLUME_SIZE * 0.9:  # 预留10%空间
                    file_groups.append(current_group)
                    current_group = []
                    current_size = 0
                current_group.append((file_path, file_size))
                current_size += file_size
        
        # 添加最后一个组（如果有）
        if current_group:
            file_groups.append(current_group)
        
        return file_groups
    
    def zip_directory(self, source_dir, output_path, exclude_empty_dirs=True):
        """优化的目录打包函数，支持分卷打包"""
        start_time = time.time()
        total_files = 0
        total_size = 0
        
        # 创建父目录（如果不存在）
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            FileUtils.create_directory(output_dir)
        
        # 获取目录中所有文件的大小
        total_size, file_sizes = self.get_file_sizes(source_dir)
        logger.info(f"检测到 {len(file_sizes)} 个文件，总大小: {total_size/1024/1024:.2f}MB")
        
        if not file_sizes:
            logger.warning("源目录中没有文件，跳过打包")
            return False, 0, 0
        
        # 判断是否需要分卷打包
        if self.should_use_volume_packaging(total_size, file_sizes):
            logger.info("文件大小超过2GB，将使用分卷打包策略")
            
            # 对文件进行分组
            file_groups = self.group_files_for_volume(file_sizes)
            logger.info(f"文件已分组为 {len(file_groups)} 个分卷")
            
            # 创建分卷ZIP
            success, volume_paths, volume_count = self.create_volume_zip(
                output_path, file_groups, os.path.dirname(source_dir)
            )
            
            if success:
                return True, len(file_sizes), total_size
            else:
                return False, 0, 0
        else:
            # 使用普通打包方式
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
        """为多个目录创建优化的zip文件"""
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