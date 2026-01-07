import sys
import os
import traceback
import time

# 添加dist/baidusearch目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'dist', 'baidusearch'))

# 直接导入search_app模块，而不是从其中导入函数
import search_app

def test_baidu_search():
    """测试百度搜索功能"""
    print("=== 测试百度搜索爬虫 ===")
    
    # 测试关键词
    test_keywords = ["人工智能"]
    
    for keyword in test_keywords:
        print(f"\n测试搜索: {keyword}")
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            # 搜索第一页
            print("正在发送请求...")
            # 设置最大执行时间为30秒
            import threading
            results = None
            error = None
            
            def search_task():
                nonlocal results, error
                try:
                    results = search_app.search_baidu(keyword, page=1)
                except Exception as e:
                    error = e
            
            thread = threading.Thread(target=search_task)
            thread.daemon = True
            thread.start()
            thread.join(30)  # 等待最多30秒
            
            if thread.is_alive():
                raise TimeoutError("搜索超时")
            if error:
                raise error
            end_time = time.time()
            print(f"请求完成，耗时: {end_time - start_time:.2f}秒")
            print(f"返回了 {len(results)} 条结果")
            
            if not results:
                print(f"❌ 未找到搜索结果")
            else:
                print(f"✅ 找到 {len(results)} 条结果")
                
                # 显示前3条结果
                for i, result in enumerate(results[:3], 1):
                    print(f"\n[{i}]")
                    print(f"标题: {result['title']}")
                    print(f"摘要: {result['abstract'][:100]}..." if len(result['abstract']) > 100 else f"摘要: {result['abstract']}")
                    print(f"来源: {result['source']}")
                    if result['cover']:
                        print(f"封面: {result['cover']}")
                
        except TimeoutError as e:
            end_time = time.time()
            print(f"❌ 搜索超时: {e}")
            print(f"耗时: {end_time - start_time:.2f}秒")
        except Exception as e:
            end_time = time.time()
            print(f"❌ 搜索出错: {e}")
            print(f"耗时: {end_time - start_time:.2f}秒")
            print("错误详情:")
            traceback.print_exc()
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_baidu_search()
