import requests
from bs4 import BeautifulSoup
import urllib.parse
import random
import time
import os

# 常用的用户代理列表，随机选择一个以减少被封禁的风险
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Linux; Android 14; SM-G998U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.7 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Linux; Android 13; SM-G991U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36"
]

# 常用的 Referer 列表
REFERERS = [
    "https://www.google.com/",
    "https://www.baidu.com/",
    "https://www.bing.com/",
    "https://www.sogou.com/",
    "https://www.so.com/"
]

def search_baidu(keyword, page=1):
    """搜索百度并返回结果"""
    print("[DEBUG] 开始搜索百度...")
    
    # 计算分页步长
    pn = (page - 1) * 10
    print(f"[DEBUG] 页码: {page}, 分页步长: {pn}")
    
    # 构建URL
    base_url = "https://www.baidu.com/s"
    params = {
        "wd": keyword,
        "pn": pn,
        "ie": "utf-8"
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    print(f"[DEBUG] 搜索URL: {url}")
    
    # 随机延迟，模拟真实用户行为
    delay = random.uniform(2, 3)
    print(f"[DEBUG] 随机延迟: {delay:.2f}秒")
    time.sleep(delay)
    
    # 优化请求头，使用更真实的浏览器请求头（强制PC端）
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "cache-control": "max-age=0",
        "connection": "keep-alive",
        "host": "www.baidu.com",
        "sec-ch-ua": '"Google Chrome";v="130", "Chromium";v="130", "Not?A_Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": random.choice([ua for ua in USER_AGENTS if "Mobile" not in ua]),
        "referer": "https://www.baidu.com/",
        "X-Requested-With": "XMLHttpRequest"
    }
    print(f"[DEBUG] User-Agent: {headers['user-agent']}")
    print(f"[DEBUG] Referer: {headers['referer']}")
    
    try:
        # 创建会话，模拟真实浏览器行为
        session = requests.Session()
        # 添加默认的Cookie
        session.cookies.set('BAIDUID', '1234567890ABCDEF1234567890ABCDEF:FG=1', domain='.baidu.com')
        session.cookies.set('BIDUPSID', '1234567890ABCDEF1234567890ABCDEF', domain='.baidu.com')
        session.cookies.set('PSTM', str(int(time.time())), domain='.baidu.com')
        print("[DEBUG] 创建会话并设置默认Cookie成功")
        
        # 先访问百度首页获取Cookie
        print("[DEBUG] 访问百度首页获取Cookie...")
        try:
            home_response = session.get("https://www.baidu.com", headers=headers, timeout=5, verify=False)
            print(f"[DEBUG] 首页访问状态码: {home_response.status_code}")
            print(f"[DEBUG] 首页响应URL: {home_response.url}")
        except Exception as e:
            print(f"[DEBUG] 首页访问异常: {e}")
        
        # 再次随机延迟
        delay = random.uniform(1, 2)
        print(f"[DEBUG] 二次随机延迟: {delay:.2f}秒")
        time.sleep(delay)
        
        # 发送搜索请求
        max_retries = 3
        for retry in range(max_retries):
            try:
                # 发送请求
                print(f"[DEBUG] 发送搜索请求 (尝试 {retry+1}/{max_retries})...")
                # 禁用重定向，避免被引导到验证页面
                response = session.get(url, headers=headers, timeout=10, allow_redirects=False, verify=False)
                print(f"[DEBUG] 搜索请求状态码: {response.status_code}")
                print(f"[DEBUG] 响应URL: {response.url}")
                
                # 检查是否成功获取响应
                if response.status_code == 200:
                    print("[DEBUG] 请求成功！")
                    break
                elif response.status_code == 302:
                    print(f"[DEBUG] 请求被重定向，Location: {response.headers.get('Location', '')}")
                    if retry < max_retries - 1:
                        print("[DEBUG] 等待后重试...")
                        time.sleep(random.uniform(2, 3))
                        # 更换User-Agent
                        headers['user-agent'] = random.choice(USER_AGENTS)
                        print(f"[DEBUG] 更换User-Agent: {headers['user-agent']}")
                else:
                    print(f"[DEBUG] 请求失败，状态码: {response.status_code}")
                    if retry < max_retries - 1:
                        print("[DEBUG] 等待后重试...")
                        time.sleep(random.uniform(2, 3))
            except requests.exceptions.Timeout:
                print("[DEBUG] 搜索请求超时")
                if retry < max_retries - 1:
                    print("[DEBUG] 等待后重试...")
                    time.sleep(random.uniform(3, 4))
            except requests.exceptions.ConnectionError:
                print("[DEBUG] 搜索请求连接错误")
                if retry < max_retries - 1:
                    print("[DEBUG] 等待后重试...")
                    time.sleep(random.uniform(3, 4))
            except Exception as e:
                print(f"[DEBUG] 搜索请求异常: {e}")
                if retry < max_retries - 1:
                    print("[DEBUG] 等待后重试...")
                    time.sleep(random.uniform(3, 4))
        else:
            # 所有重试都失败
            print("[DEBUG] 所有搜索请求尝试都失败")
            return []
        
        # 解析HTML
        print("[DEBUG] 开始解析HTML...")
        soup = BeautifulSoup(response.text, 'html.parser')
        print("[DEBUG] HTML解析完成")
        
        # 调试：打印部分HTML内容，了解页面结构
        print("[DEBUG] 打印部分HTML内容...")
        # 查找content_left容器
        content_left = soup.select_one('#content_left')
        if content_left:
            print("[DEBUG] 找到content_left容器")
            # 打印content_left的前1000个字符
            html_snippet = content_left.prettify()[:1000]
            print(f"[DEBUG] content_left内容片段: {html_snippet}...")
        else:
            print("[DEBUG] 未找到content_left容器")
            # 打印整个页面的前2000个字符
            html_snippet = response.text[:2000]
            print(f"[DEBUG] 页面内容片段: {html_snippet}...")
        
        # 提取搜索结果
        results = []
        seen_titles = set()  # 用于去重
        
        # 查找所有搜索结果项 - 使用更符合当前百度页面结构的选择器
        print("[DEBUG] 查找搜索结果容器...")
        # 尝试多种选择器策略
        result_containers = []
        
        # 策略1: 传统的content_left > div
        containers1 = soup.select('#content_left > div')
        print(f"[DEBUG] 策略1找到 {len(containers1)} 个结果容器")
        result_containers.extend(containers1)
        
        # 策略2: 直接查找结果项
        containers2 = soup.select('div.result')
        print(f"[DEBUG] 策略2找到 {len(containers2)} 个结果容器")
        result_containers.extend(containers2)
        
        # 策略3: 查找包含标题的div
        containers3 = soup.select('div[tpl]')
        print(f"[DEBUG] 策略3找到 {len(containers3)} 个结果容器")
        result_containers.extend(containers3)
        
        # 策略4: 查找移动端页面的结果容器
        containers4 = soup.select('div[class*="result"]')
        print(f"[DEBUG] 策略4找到 {len(containers4)} 个结果容器")
        result_containers.extend(containers4)
        
        # 策略5: 查找包含h3标题的容器
        containers5 = []
        for h3 in soup.select('h3'):
            parent = h3.find_parent('div')
            if parent:
                containers5.append(parent)
        print(f"[DEBUG] 策略5找到 {len(containers5)} 个结果容器")
        result_containers.extend(containers5)
        
        # 去重（基于容器内容和结构，而不仅仅是ID）
        unique_containers = []
        seen_signatures = set()
        for container in result_containers:
            # 生成容器签名（基于标题文本和结构）
            h3_elem = container.select_one('h3')
            if h3_elem:
                signature = h3_elem.get_text(strip=True)
                if signature and signature not in seen_signatures:
                    seen_signatures.add(signature)
                    unique_containers.append(container)
            else:
                # 没有h3的容器可能不是搜索结果
                continue
        
        result_containers = unique_containers
        print(f"[DEBUG] 最终找到 {len(result_containers)} 个唯一结果容器")
        
        for i, item in enumerate(result_containers):
            print(f"[DEBUG] 处理结果 {i+1}...")
            
            # 跳过广告和无关内容
            if 'ad' in item.get('class', []) or '广告' in item.get_text():
                print(f"[DEBUG] 跳过广告内容")
                continue
            
            # 提取标题
            title = ""
            # 尝试多种标题选择器
            title_selectors = ['h3.t a', 'h3.title a', 'h3 a', '.t a']
            for selector in title_selectors:
                title_elem = item.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title:
                        print(f"[DEBUG] 找到标题: {title[:20]}...")
                        break
            # 如果还是没有找到，尝试直接获取h3
            if not title:
                h3_elem = item.select_one('h3')
                if h3_elem:
                    title = h3_elem.get_text(strip=True)
                    print(f"[DEBUG] 从h3获取标题: {title[:20]}...")
            
            # 跳过无标题的结果
            if not title:
                print(f"[DEBUG] 跳过无标题结果")
                continue
            
            # 去重
            if title in seen_titles:
                print(f"[DEBUG] 跳过重复标题")
                continue
            seen_titles.add(title)
            
            # 提取摘要 - 尝试多种可能的选择器
            abstract = ""
            abstract_selectors = ['.c-abstract', '.content-right_8Zs40', '.abstract']
            for selector in abstract_selectors:
                abstract_elem = item.select_one(selector)
                if abstract_elem:
                    abstract = abstract_elem.get_text(strip=True)
                    if abstract:
                        print(f"[DEBUG] 找到摘要: {abstract[:30]}...")
                        break
            # 如果还是没有找到，尝试获取所有文本内容作为摘要
            if not abstract:
                text_content = item.get_text(strip=True)
                if text_content and len(text_content) > len(title):
                    abstract = text_content[len(title):].strip()[:100]
                    print(f"[DEBUG] 从文本内容提取摘要: {abstract[:30]}...")
            
            # 提取来源（尝试多种可能的选择器）
            source = ""
            # 尝试常见的来源信息选择器
            source_selectors = ['.c-author', '.c-showurl', '.c-from', '.t a.c-showurl', '.op-source','.site-link','.result-op .c-showurl']
            for selector in source_selectors:
                source_elem = item.select_one(selector)
                if source_elem:
                    source = source_elem.get_text(strip=True)
                    if source:
                        print(f"[DEBUG] 找到来源: {source}")
                        break
            # 尝试从链接中提取域名作为来源
            if not source:
                link_elem = item.select_one('a[href]')
                if link_elem:
                    href = link_elem.get('href', '')
                    if href:
                        # 从URL中提取域名
                        import re
                        domain_match = re.search(r'//([^/]+)', href)
                        if domain_match:
                            source = domain_match.group(1)
                            print(f"[DEBUG] 从URL提取来源: {source}")
            
            # 构建结果
            result = {
                "title": title,
                "abstract": abstract,
                "source": source,
                "cover": ""
            }
            results.append(result)
            print(f"[DEBUG] 添加结果: {title[:20]}...")
        
        print(f"[DEBUG] 搜索完成，返回 {len(results)} 条结果")
        return results
        
    except requests.exceptions.RequestException as e:
        print(f"[DEBUG] 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return []
    except Exception as e:
        print(f"[DEBUG] 其他异常: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    """主函数"""
    print("=== 搜搜App ===")
    print("请输入搜索关键字，按Enter键开始搜索")
    
    while True:
        keyword = input("关键字: ").strip()
        if not keyword:
            print("请输入有效的关键字")
            continue
        
        try:
            page = input("页码 (默认1): ").strip()
            page = int(page) if page.isdigit() else 1
        except EOFError:
            page = 1
        
        print(f"\n正在搜索: {keyword} (第{page}页)...")
        
        results = search_baidu(keyword, page)
        
        if not results:
            print("未找到搜索结果")
        else:
            print(f"\n找到 {len(results)} 条结果:")
            print("-" * 80)
            
            for i, result in enumerate(results, 1):
                print(f"[{i}]")
                print(f"标题: {result['title']}")
                print(f"摘要: {result['abstract']}")
                print(f"来源: {result['source']}")
                if result['cover']:
                    print(f"封面: {result['cover']}")
                print("-" * 80)
        
        # 询问是否继续
        continue_flag = input("\n是否继续搜索? (y/n): ").strip().lower()
        if continue_flag != 'y':
            print("谢谢使用！")
            break

if __name__ == "__main__":
    main()