import os
import zipfile
import multiprocessing
import time
from datetime import datetime
import shutil
import sys

# 确保中文正常显示
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def is_directory_empty(directory):
    """检查目录是否为空"""
    for _, dirs, files in os.walk(directory):
        if files or dirs:
            return False
    return True

class OptimizedZipper:
    def __init__(self, chunk_size=1024*1024*10):  # 10MB chunks
        self.chunk_size = chunk_size
        self.max_workers = multiprocessing.cpu_count()
    
    def add_file_to_zip(self, zipf, file_path, arcname):
        """将文件分块添加到zip文件中"""
        try:
            with open(file_path, 'rb') as f:
                zipf.write(file_path, arcname)
            return True
        except Exception as e:
            print(f"添加文件失败 {file_path}: {e}")
            return False
    
    def zip_directory(self, source_dir, output_path, exclude_empty_dirs=True):
        """优化的目录打包函数"""
        start_time = time.time()
        total_files = 0
        total_size = 0
        
        # 创建父目录（如果不存在）
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
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
                                print(f"已处理 {total_files} 个文件，总大小: {total_size/1024/1024:.2f} MB")
        except Exception as e:
            print(f"打包过程出错: {e}")
            return False, 0, 0
        
        end_time = time.time()
        print(f"打包完成: {output_path}")
        print(f"总文件数: {total_files}")
        print(f"总大小: {total_size/1024/1024:.2f} MB")
        print(f"耗时: {end_time - start_time:.2f} 秒")
        
        return True, total_files, total_size

    def create_optimized_zips(self, target_dirs, output_base_dir):
        """为多个目录创建优化的zip文件"""
        results = []
        
        for source_dir in target_dirs:
            if not os.path.exists(source_dir):
                print(f"源目录不存在: {source_dir}")
                results.append((source_dir, False, 0, 0))
                continue
            
            # 检查目录是否为空
            if is_directory_empty(source_dir):
                print(f"源目录为空: {source_dir}")
                results.append((source_dir, False, 0, 0))
                continue
            
            # 创建输出文件名
            current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
            dir_name = os.path.basename(source_dir)
            zip_filename = f"{dir_name}_{current_time}.zip"
            
            # 根据源目录确定输出路径
            if "文学" in source_dir:
                output_dir = os.path.join(output_base_dir, "欢迎回家", "Archive", "文学")
            else:
                # 提取分类名称（技术交流、新時代的我們、達蓋爾的旗幟）
                category_match = next((d for d in os.listdir(output_base_dir) if os.path.isdir(os.path.join(output_base_dir, d)) and d in ["技术交流", "新時代的我們", "達蓋爾的旗幟"]), None)
                if category_match:
                    current_date = datetime.now().strftime('%Y%m%d')
                    output_dir = os.path.join(output_base_dir, "Archive", f"{category_match}_{current_date}")
                else:
                    output_dir = os.path.join(output_base_dir, "Archive")
            
            output_path = os.path.join(output_dir, zip_filename)
            
            # 创建zip文件
            success, file_count, total_size = self.zip_directory(source_dir, output_path)
            results.append((source_dir, success, file_count, total_size))
        
        return results

if __name__ == "__main__":
    # 示例用法
    zipper = OptimizedZipper()
    
    # 要打包的目录列表
    target_directories = [
        # "文学",  # 文学目录
        # "pic/技术交流",  # 图片目录示例
    ]
    
    # 输出基础目录
    output_base = "."
    
    # 执行打包
    results = zipper.create_optimized_zips(target_directories, output_base)
    
    # 打印结果摘要
    print("\n打包结果摘要:")
    for dir_path, success, file_count, total_size in results:
        status = "成功" if success else "失败"
        print(f"{dir_path}: {status}, 文件数: {file_count}, 大小: {total_size/1024/1024:.2f} MB")