# Scan_Blacklink

## English:

Scan the source code of the website application to see if there is a third-party black chain

Most website systems are susceptible to blacklink injection. Analysis indicates that this issue most likely falls into one of the following two categories:

1. It's possible that developers cut corners during website development by directly copying and pasting open-source framework code containing blacklink code into certain parts of the website's source code. This leads to the website being flagged as having blacklinks injected by attackers, when in reality it's a developer error. 【This falls under local code invocation issues】

2. It could be that during website development, the developer directly invoked certain insecure third-party resources remotely. These third-party resources themselves contained blacklink code, leading to the website being flagged as having blacklinks injected by attackers. In reality, this is a developer error. 【This falls under remote resource invocation issues】


Therefore, I referenced the latest TLD list provided by the IANA Root Zone to accommodate most top-level domain suffixes on the internet. By employing multiple regular expressions, I ensured that third-party domain names within the local source code were extracted.

💡Here are three scripts: Scan_Blacklink.py, Get_Pagesource.py, and Download_har.py.


### 1、Scan_Blacklink:

Usage: python3 scan_blacklink.py [-h] [-d DIRECTORY] [-b BASE_DOMAIN] [-o OUTPUT] [--no-timestamp] [-r] [-nr] [-e EXTENSIONS | -a] [-t THREADS] [-bl BLACKLIST] [--probe]
               [--probe-timeout PROBE_TIMEOUT] [--probe-workers PROBE_WORKERS]

Extract hidden links and external links from all source code files in the directory (supports multi-threading acceleration and HTTP probing for suspected black links)

```
options:
  -h, --help            show this help message and exit
  -d DIRECTORY, --directory DIRECTORY
                        Directory path to process, defaults to current directory
  -b BASE_DOMAIN, --base-domain BASE_DOMAIN
                        Base domain used to determine external links (e.g., https://example.com)
  -o OUTPUT, --output OUTPUT
                        Output file path. Default: automatically generates filenames with timestamps
  --no-timestamp        Output filenames without timestamps
  -r, --recursive       Recursively process subdirectories (enabled by default)
  -nr, --no-recursive   Do not recursively process subdirectories
  -e EXTENSIONS, --extensions EXTENSIONS
                        Comma-separated file extensions (e.g., html,php,js) or (.html,.php,.js)
  -a, --all             Scan all files (no extension restrictions, may be slower)
  -t THREADS, --threads THREADS
                        Number of threads (default: 4, recommended range: 1-16)
  -bl BLACKLIST, --blacklist BLACKLIST
                        Blacklist domain/keyword list file, one entry per line, supports substring matching (e.g., test.xyz, ppp.qr, etc.), appended to built-in keywords
  --probe               Perform HTTP probes on detected suspected blacklinks/hidden links (requires requests library installation)
  --probe-timeout PROBE_TIMEOUT
                        HTTP probe timeout (seconds), default 5 seconds
  --probe-workers PROBE_WORKERS
                        Number of concurrent HTTP probe threads, default 8


Example:
  scan_blacklink.py -d /path/to/dir                  # Scan specified directory
  scan_blacklink.py --all                            # Scan all files (no extension restrictions)
  scan_blacklink.py -e html,php,js                   # Scan only specified extensions
  scan_blacklink.py -t 8                             # Use 8 threads for acceleration
  scan_blacklink.py -b https://example.com           # Specify root domain for external link detection
  scan_blacklink.py -bl blacklist.txt                # Append blacklink domain/keyword list to built-in keywords
  scan_blacklink.py --probe                          # Perform HTTP probe on suspected blacklinks

Common parameters, such as:
python3 scan_blacklink.py -d /path/to/dir --probe

During the process of scanning source code, extract corresponding domain names while simultaneously performing HTTP probes to obtain response information.
```

Dec 17 update:

Added script program execution recovery functionality; parameters remain unchanged.

<img width="1771" height="446" alt="image" src="https://github.com/user-attachments/assets/bf76bf29-b95b-4e11-a895-0fd325fcc8c7" />




### 2、Get_Pagesource:

This script's functionality involves using Selenium to simulate requests, then downloading the corresponding frontend page source code files locally. Simply define the target URL within the script code to enable automated crawling. Of course, you'll need to configure the proxy auto-switching mode to avoid having your IP blocked by WAF.

Usage: python3 Get_Pagesource.py


### 3、Download_har:

If you simply use the Get_Pagesource.py script to download the frontend page source files, some files may be missing. This is because many websites now employ asynchronous loading to enable faster access. Consequently, corresponding resource files are only loaded when you intentionally click a specific function or page during browsing. You can view detailed information about this loading process in the Network tab of your browser's console. Simultaneously, you can download the contents of the Network tab page—i.e., the currently loaded resource files—to your local machine as a har file. This file contains URLs pointing to all resource files. Simply executing the Download_har.py script will automatically download the corresponding resource files. The Download_har.py script was actually created to complement the Get_Pagesource.py script mentioned above. It enables the complete download of a target website's frontend source code, allowing you to even set it up locally. Of course, you'll need to configure the proxy auto-switching mode to avoid having your IP blocked by WAF.

Usage: python3 Download_har.py


## Simplified Chinese(简体中文):


扫描网站应用程序的源代码，查看是否存在第三方黑链

大部分网站系统存在被挂黑链的现象，经过分析大概率是属于下面的这两种情况：

1、有可能是开发人员在开发网站的时候偷懒了，直接把一些包含了黑链代码的开源框架代码复制粘贴到网站源码的某些地方，导致网站被认为是被攻击者挂黑链，但实际上是开发人员的失误。【这是属于本地代码调用问题】

2、有可能是开发人员在开发网站的时候，直接远程调用了某些不安全的第三方资源，这些第三方资源本身就包含了黑链代码，导致网站被认为是被攻击者挂黑链，但实际上是开发人员的失误。【这是属于远程资源调用问题】

因此，我参考了IANA根域提供的最新顶级域名列表，以覆盖互联网上绝大多数顶级域名后缀，并通过运用多重正则表达式，确保从本地源代码中提取出所有第三方域名。

💡这里有三个脚本，分别是Scan_Blacklink.py、Get_Pagesource.py、Download_har.py



### 1、Scan_Blacklink:

usage: scan_blacklink.py [-h] [-d DIRECTORY] [-b BASE_DOMAIN] [-o OUTPUT] [--no-timestamp] [-r] [-nr] [-e EXTENSIONS | -a] [-t THREADS] [-bl BLACKLIST] [--probe]
                         [--probe-timeout PROBE_TIMEOUT] [--probe-workers PROBE_WORKERS]

提取目录中所有源代码文件的暗链和外链地址（支持多线程加速，并可对疑似黑链进行HTTP探测）

```
options:
  -h, --help            show this help message and exit
  -d DIRECTORY, --directory DIRECTORY
                        要处理的目录路径，默认为当前目录
  -b BASE_DOMAIN, --base-domain BASE_DOMAIN
                        基础域名，用于判断是否为外链（如 https://example.com）
  -o OUTPUT, --output OUTPUT
                        输出文件路径，默认自动生成带时间戳的文件名
  --no-timestamp        输出文件名不包含时间戳
  -r, --recursive       是否递归处理子目录（默认启用）
  -nr, --no-recursive   不递归处理子目录
  -e EXTENSIONS, --extensions EXTENSIONS
                        逗号分隔的文件扩展名（如: html,php,js）或（.html,.php,.js）
  -a, --all             扫描所有文件（不限扩展名，可能较慢）
  -t THREADS, --threads THREADS
                        线程数（默认为4，建议范围：1-16）
  -bl BLACKLIST, --blacklist BLACKLIST
                        黑链域名/关键字列表文件，每行一个，支持子串匹配（如：ceshi.xyz、ppp.qr 等），会在内置关键词基础上追加
  --probe               对命中的疑似黑链/隐藏链接进行HTTP探测（需要安装requests库）
  --probe-timeout PROBE_TIMEOUT
                        HTTP探测超时时间（秒），默认5秒
  --probe-workers PROBE_WORKERS
                        HTTP探测并发线程数，默认8

示例:
  scan_blacklink.py -d /path/to/dir                  # 扫描指定目录
  scan_blacklink.py --all                            # 扫描所有文件（不限扩展名）
  scan_blacklink.py -e html,php,js                   # 只扫描指定扩展名
  scan_blacklink.py -t 8                             # 使用8个线程加速
  scan_blacklink.py -b https://example.com           # 指定基础域名识别外链
  scan_blacklink.py -bl blacklist.txt                # 在内置关键词基础上追加黑链域名/关键字列表
  scan_blacklink.py --probe                          # 对疑似黑链进行HTTP探测

常用的参数，比如：
python3 scan_blacklink.py -d /path/to/dir --probe

在扫描源码的过程中提取对应的域名并同时进行HTTP探测获取响应信息
```

12月7日更新: 

新增脚本程序恢复执行功能，使用参数依然不变

<img width="1771" height="446" alt="image" src="https://github.com/user-attachments/assets/bf76bf29-b95b-4e11-a895-0fd325fcc8c7" />


### 2、Get_Pagesource:

这个脚本的功能是属于通过selenium去模拟请求后，然后把对应的前端页面源码内容文件进行下载到本地，只要在脚本代码里面定义好对应的目标URL即可进行自动爬取，当然需要设置好代理自动切换模式，避免被WAF封IP。

Usage: python3 Get_Pagesource.py


### 3、Download_har:

因为如果单纯的使用了Get_Pagesource.py脚本去下载前端页面源码内容文件的话，可能会存在部分文件缺失，因为目前很多网站为了能方便大家能够快速的访问，基本上都是用了异步加载方式，因此只有当你在浏览的过程中刻意去点击某个功能或者某个页面的时候才会加载对应的资源文件，这个加载的情况可以在浏览器的控制台的Network选项卡页面查看详细信息，那么同时也可以把Network选项卡的页面内容【即当前已经完成加载的资源文件】进行下载到本地为har文件，里面有指向所有资源文件的URL地址，那么只要执行这个Download_har.py脚本即可自动完成下载对应的资源文件，其实Download_har.py脚本的诞生是为了对上面的Get_Pagesource.py脚本的一个补充，可以完整的下载一个目标网站的前端源码，甚至你可以在本地搭建它。当然需要设置好代理自动切换模式，避免被WAF封IP。

Usage: python3 Download_har.py
