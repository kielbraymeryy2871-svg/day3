import sys
import os
import traceback
import time

# 添加dist/baidusearch目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'dist', 'baidusearch'))

# 导入search_app模块
import search_app

def test_simple_request():
    """简单测试百度搜索请求"""
    print("=== 简单测试百度爬虫 ===")
    
    # 测试关键词
    keyword = "人工智能"
    print(f"测试搜索: {keyword}")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        print("1. 开始构建请求...")
        # 直接测试搜索函数
        results = search_app.search_baidu(keyword, page=1)
        
        end_time = time.time()
        print(f"2. 请求完成，耗时: {end_time - start_time:.2f}秒")
        print(f"3. 返回了 {len(results)} 条结果")
        
        if not results:
            print("❌ 未找到搜索结果")
        else:
            print("✅ 找到搜索结果")
            # 显示前2条结果
            for i, result in enumerate(results[:2], 1):
                print(f"\n[{i}]")
                print(f"标题: {result['title']}")
                print(f"摘要: {result['abstract'][:50]}..." if len(result['abstract']) > 50 else f"摘要: {result['abstract']}")
                print(f"来源: {result['source']}")
                if result['cover']:
                    print(f"封面: {result['cover'][:50]}...")
        
    except Exception as e:
        end_time = time.time()
        print(f"❌ 搜索出错: {e}")
        print(f"耗时: {end_time - start_time:.2f}秒")
        print("错误详情:")
        traceback.print_exc()
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_simple_request()
