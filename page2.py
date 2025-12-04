import os
import requests
import json
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

def extract_urls_from_har(har_file, target_pageref="page_2"):
    """
    从 .har 文件中提取指定页面的所有 URL。
    """
    with open(har_file, 'r', encoding='utf-8') as f:
        har_data = json.load(f)

    # 提取所有请求的url
    urls = []
    for entry in har_data['log']['entries']:
        # 查找每个请求的'pageref'和'url'值
        pageref = entry.get('pageref', '')
        url = entry.get('request', {}).get('url', '')
        
        # 只提取 pageref 为 "page_2" 的 url
        if pageref == target_pageref and url:
            urls.append(url)

    return urls

def download_homepage(url, save_dir):
    """
    处理主页的下载，保存为 index.html。
    """
    try:
        # 下载主页内容
        response = requests.get(url)
        response.raise_for_status()  # 如果请求失败，会抛出异常

        # 确保目录存在
        file_path = os.path.join(save_dir, 'index.html')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 保存主页文件
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        print(f"主页已保存: {file_path}")
        
        # 修改 HTML 文件中的资源链接为本地相对路径
        modify_html_links(file_path, url, save_dir)
        
    except Exception as e:
        print(f"下载主页失败: {url}，错误: {str(e)}")

def download_file(url, save_dir):
    """
    下载其他资源文件，并按实际目录结构保存。
    """
    try:
        # 发送请求获取文件
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 如果请求失败，会抛出异常
        
        # 解析url，获取文件名和目录
        parsed_url = urlparse(url)

        # 构造保存路径，保留查询参数
        file_path = os.path.join(save_dir, parsed_url.path.lstrip('/'))

        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 下载文件并保存
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):  # 分块下载，避免内存占用过大
                f.write(chunk)
        
        print(f"文件已保存: {file_path}")
        
        return file_path  # 返回保存的文件路径
    except Exception as e:
        print(f"下载文件失败: {url}，错误: {str(e)}")
        return None

def modify_html_links(html_file, base_url, save_dir):
    """
    修改 HTML 文件中的资源链接为本地相对路径。
    """
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # 获取所有资源文件链接并替换为本地相对路径
    for tag in soup.find_all(['link', 'script', 'img']):
        # 替换 href 和 src 属性
        url = tag.get('href') or tag.get('src')
        if url:
            # 只处理以原始域名开头的 URL
            if url.startswith(base_url):
                relative_path = url.replace(base_url, save_dir + '/')
                if '?' in relative_path:
                    relative_path = relative_path.split('?')[0]  # 去掉查询参数（如果有）
                
                # 更新 tag 中的路径为相对路径
                if tag.get('href'):
                    tag['href'] = relative_path
                elif tag.get('src'):
                    tag['src'] = relative_path

    # 保存修改后的 HTML 文件
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    print(f"HTML 文件中的资源链接已修改为相对路径: {html_file}")

def download_files_from_har(har_file, save_dir, target_pageref="page_2"):
    """
    从 .har 文件中提取所有 URL，并下载主页和资源文件。
    """
    # 提取所有 URL
    urls = extract_urls_from_har(har_file, target_pageref)
    
    # 处理主页
    homepage_url = urls[0] if urls else None
    if homepage_url:
        download_homepage(homepage_url, save_dir)  # 下载主页
        
    # 遍历并下载其他文件
    downloaded_files = []
    for url in urls:
        if url.startswith('http') and url != homepage_url:  # 跳过主页 URL
            file_path = download_file(url, save_dir)
            if file_path:
                downloaded_files.append(file_path)

# 使用示例
har_file_path = 'www.example.com.har'  # 替换成你自己的.har文件路径
save_directory = 'downloaded_resources1'  # 资源保存的根目录
download_files_from_har(har_file_path, save_directory)
