import requests
import re
import os
import shutil
import zipfile
import random
from datetime import datetime
from bs4 import BeautifulSoup
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
}

# 确保文学目录存在
LITERATURE_DIR = '文学'
os.makedirs(LITERATURE_DIR, exist_ok=True)

# 确保Archive/文学目录存在
ARCHIVE_DIR = os.path.join('欢迎回家', 'Archive', '文学')
os.makedirs(ARCHIVE_DIR, exist_ok=True)

def _1_get_url(page):
    # 获取today话题
    # url = 'https://t66y.com/thread0806.php?fid=20&search=today&page=' + page  # 文学
    url = 'https://t66y.com/thread0806.php?fid=20&search=&page=' + page  # 文学
    res = requests.get(url, headers=headers)
    res.encoding = res.apparent_encoding  # 使用自动检测的编码
    text = res.text
    a = re.findall('a href="(.*?)html"', text)
    print('总界面', a)
    return a  # 返回1级页面里面的url

def baocun(url, name):  # 此方法是将图片保存文件到本地 只需要传入图片地址
    n = re.findall('(.*?)[P\-]', name)
    if not n:
        print(f"无法提取文件夹名称: {name}")
        return
    folder_name = n[0][-3:]
    root = os.path.join(LITERATURE_DIR, folder_name)
    try:
        os.makedirs(root, exist_ok=True)
    except Exception as e:
        print(f"创建文件夹失败: {root}, 错误: {e}")
        return
    if url[-4] == '.':
        path = os.path.join(root, name + url[-4:])  # 通过’/‘把图片的url分开找到最后的那个就是带.jpg的保存起来
    elif url[-5] == '.':
        path = os.path.join(root, name + url[-5:])  # 通过’/‘把图片的url分开找到最后的那个就是带.jpg的保存起来
    if not os.path.exists(path):
        r = requests.get(url)
        r.raise_for_status()
        with open(path, 'wb') as f:  # 以二进制格式打开一个文件只用于写入
            f.write(r.content)  # r.content返回二进制，像图片
            print('爬取成功')

def _2_get_urlanddl(url, name='default'):
    res = requests.get(url, headers=headers)
    res.encoding = res.apparent_encoding  # 使用自动检测的编码
    text = res.text
    soup = BeautifulSoup(text, 'lxml')
    tag_title = soup.find('title')
    title = tag_title.text
    title = re.findall('(.*?)-', title)[0]
    content = soup.find(attrs={'class': 'tpc_content do_not_catch'}).text
    content = re.sub('<.*?>', '', content)
    # 提取分类名称
    category_match = re.search(r'\[(.*?)\]', title)
    if category_match:
        category = category_match.group(1)
    else:
        category = '其他'
    category_path = os.path.join(LITERATURE_DIR, category)
    try:
        os.makedirs(category_path, exist_ok=True)
    except Exception as e:
        print(f"创建分类文件夹失败: {category_path}, 错误: {e}")
        return
    file_path = os.path.join(category_path, title + '.txt')
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print('保存成功')
    except Exception as e:
        print('保存失败', url, e)

def zip_literature_folder():
    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = f'小说_{current_time}.zip'
    zip_filepath = os.path.join(ARCHIVE_DIR, zip_filename)
    try:
        shutil.make_archive(os.path.splitext(zip_filepath)[0], 'zip', LITERATURE_DIR)
        print(f'打包成功: {zip_filepath}')
    except Exception as e:
        print(f'打包失败: {e}')

if __name__ == '__main__':
    # page1 = input("输入start页面：")
    # page2 = input("输入end页面：")
    # 生成 page1 和 page2，确保间隔为一页
    start_page = random.randint(1, 10)  # 假设页面范围是 1 到 10，可以根据实际情况调整
    end_page = start_page + 1

    page1 = str(start_page)
    page2 = str(end_page)
    crawled = []
    try:
        with open('已爬取草榴word.log', 'r') as file:
            for line in file:
                crawled.append(line.strip())
    except:
        pass
    for page in range(int(page1), int(page2) + 1):
        a = _1_get_url(str(page))
        for i in a:
            if i not in crawled:
                try:
                    with open('已爬取草榴word.log', 'a') as file:
                        file.write(i + '\n')
                    _2_get_urlanddl('https://t66y.com/' + i + 'html')
                except Exception as e:
                    print('失败', e)
            else:
                print('已爬取，跳过', i)
    # 打包文件夹
    zip_literature_folder()