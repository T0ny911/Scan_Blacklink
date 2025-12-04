
import os
import time
from urllib.parse import urljoin, urlparse
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def setup_driver():
    """配置并初始化WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def download_file(url, folder):
    """下载单个文件到指定文件夹，保持网站目录结构"""
    try:
        parsed_url = urlparse(url)
        # 构建本地文件路径，保持网站的目录结构
        local_file_path = os.path.join(folder, parsed_url.netloc, parsed_url.path.strip('/'))
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
        
        response = requests.get(url, stream=True)
        with open(local_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return local_file_path
    except Exception as e:
        print(f"Failed to download {url}. Reason: {str(e)}")
        return None

def extract_resources(driver, url):
    """使用Selenium和BeautifulSoup提取网站所有资源链接"""
    driver.get(url)
    time.sleep(15)  # 等待页面动态内容加载
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    urls = set()
    for tag in soup.find_all(['link', 'script', 'img', 'source']):
        src = tag.get('src') or tag.get('href') or tag.get('srcset')
        if src and not src.startswith(('data:', '#', 'mailto:', 'javascript:')):
            urls.add(urljoin(url, src))
    return urls

def main():
    target_url = 'https://www.example.com'  # 目标网站URL
    driver = setup_driver()
    
    # 第二个需求：使用Selenium下载所有资源
    resource_urls = extract_resources(driver, target_url)
    downloaded_files = set()
    for resource_url in resource_urls:
        downloaded_path = download_file(resource_url, 'downloaded_files_selenium1')
        if downloaded_path:
            downloaded_files.add(downloaded_path)
    driver.quit()

    # 打印下载结果
    print(f"Total unique files downloaded by Selenium: {len(downloaded_files)}")
    # 实际存储所有结果的逻辑（包括文件去重和合并操作）根据实际需求编写。

if __name__ == "__main__":
    main()
