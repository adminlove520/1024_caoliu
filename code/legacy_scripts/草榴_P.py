import requests
import re
import os
import multiprocessing
import time
from chardet.universaldetector import UniversalDetector
import chardet
from datetime import datetime
import shutil
import uuid
import random
import io
import sys
from fake_useragent import UserAgent
import requests
ua = UserAgent()
headers = {'User-Agent': UserAgent().chrome}

def get_pic_type_name(pic_type):
    if pic_type == '1':
        return '技术交流'
    elif pic_type == '2':
        return '新時代的我們'
    elif pic_type == '3':
        return '達蓋爾的旗幟'
    else:
        return '其他'

def _1_get_url(page, pic_type):
    if pic_type == '1':
        url = 'https://t66y.com/thread0806.php?fid=7&search=&page=' + page  # 技术交流
    if pic_type == '2':
        url = 'https://t66y.com/thread0806.php?fid=8&search=&page=' + page  # 新時代的我們
    if pic_type == '3':
        url = 'https://t66y.com/thread0806.php?fid=16&search=&page=' + page  # 達蓋爾的旗幟

    res = requests.get(url, headers=headers)
    code = re.findall('charset=(.*)\"', res.text)[0]
    if not code:
        code = chardet.detect(res.content)['encoding']
    res.encoding = code
    text = res.text
    a = re.findall('a href="(.*?)html"', text)
    return a  # 返回1级页面里面的url

def getimgscl(url, name='default'):
    count = 0
    res = requests.get(url, headers=headers)
    code = re.findall('charset=(.*)\"', res.text)[0]
    if not code:
        code = chardet.detect(res.content)['encoding']
    res.encoding = code
    text = res.text
    a = re.findall('ess-data=\'(.*?)\'', text)
    # 使用原始字符串 r'<title>(.*?)\|' 来避免转义问题
    title1 = re.findall(r'<title>(.*?)\|', text)
    title = re.findall('(.*?)P', title1[0])[0]
    print(title)
    print(code, url)
    if title:
        name = title
    pic_list = []
    pic_list.append(title)
    for i in a:
        pic_list.append(i)
    return pic_list

def save_pic(url, count, title, pic_type):
    pic_type_name = get_pic_type_name(pic_type)
    pic_dir = os.path.join('pic', pic_type_name, title)
    os.makedirs(pic_dir, exist_ok=True)

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

    file_name = os.path.join(pic_dir, f"{title}{count + 1}{extension}")
    # 使用原始字符串 r'[/:*?"<>|]' 来避免转义问题
    file_name = re.sub(re.compile(r'[/:*?"<>|]'), '', file_name)
    
    res = requests.get(url)
    print(len(res.content) // 1024 // 1024, url)
    with open(file_name, 'wb') as f:
        f.write(res.content)
    print('保存成功')

def process_download(save_pic, url_list, title, pic_type):
    processes = []
    start = time.time()
    for i in range(len(url_list)):
        p = multiprocessing.Process(target=save_pic, args=[url_list[i], i, title, pic_type])
        p.start()
        processes.append(p)
    for p in processes:
        p.join()
    end = time.time()
    print('多进程总耗时：%r' % (end - start))

def zip_pic_folder(pic_type):
    pic_type_name = get_pic_type_name(pic_type)
    pic_dir = os.path.join('pic', pic_type_name)
    if not os.path.exists(pic_dir):
        print(f"文件夹 {pic_dir} 不存在")
        return

    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    current_date = datetime.now().strftime('%Y%m%d')
    archive_subdir = os.path.join('Archive', f"{pic_type_name}_{current_date}")
    os.makedirs(archive_subdir, exist_ok=True)

    zip_filename = f"{pic_type_name}_{current_time}.zip"
    zip_filepath = os.path.join(archive_subdir, zip_filename)
    try:
        shutil.make_archive(os.path.splitext(zip_filepath)[0], 'zip', pic_dir)
        print(f'打包成功: {zip_filepath}')
    except Exception as e:
        print(f'打包失败: {e}')

if __name__ == '__main__':
    pic_type = input('输入类型\n1技术交流\n2新時代的我們\n3達蓋爾的旗幟\n')
    page1 = input("输入start页面：")
    page2 = input("输入end页面：")
    # types = ['1', '2', '3']
    # pic_type = random.choice(types)
    # page1 = '5'
    # page2 = '6'
    crawled = []
    try:
        with open('已爬取草榴p.log', 'r') as file:
            for line in file:
                crawled.append(line[:-1])
    except:
        pass
    for page in range(int(page1), int(page2) + 1):
        a = _1_get_url(str(page), pic_type)
        for i in a:
            if i not in crawled:
                try:
                    with open('已爬取草榴p.log', 'a') as file:
                        file.write(i + '\n')
                    imgs = getimgscl('https://t66y.com/' + i + 'html')
                    title = imgs[0]
                    print(title)
                    del imgs[0]
                    process_download(save_pic, imgs, title, pic_type)
                except:
                    print('下载失败')
            else:
                print('已爬取，跳过', i)
    # 打包pic文件夹
    zip_pic_folder(pic_type)