import requests
import time

# 测试采集结果图片显示问题
base_url = 'http://127.0.0.1:5001'

def test_collect_with_images():
    """测试采集结果的图片显示"""
    print("=== 测试采集结果图片显示 ===")
    
    # 1. 开始采集
    data = {
        'keyword': 'Python',
        'crawler_ids': ['1']
    }
    
    response = requests.post(f'{base_url}/crawler/collect/start', data=data)
    print(f"Start collect response: {response.json()}")
    
    if response.json().get('status') == 'success':
        # 2. 等待采集完成
        print("等待采集完成...")
        time.sleep(10)
        
        # 3. 获取采集数据
        response = requests.get(f'{base_url}/crawler/collect/data')
        result = response.json()
        
        print(f"\n采集数据状态: {result['status']}")
        print(f"采集数据数量: {len(result['data'])}")
        
        # 4. 检查每个采集结果的图片字段
        if result['data']:
            print("\n=== 采集结果图片信息 ===")
            for i, item in enumerate(result['data'][:3]):  # 只检查前3条
                print(f"\n结果 {i+1}:")
                print(f"标题: {item.get('title')}")
                print(f"ID: {item.get('id')}")
                print(f"URL: {item.get('url')}")
                print(f"cover字段: {item.get('cover')}")
                print(f"cover_image字段: {item.get('cover_image')}")
                print(f"图片URL是否默认: {'是' if 'placeholder' in item.get('cover_image', '') else '否'}")
        else:
            print("没有采集到数据")
    else:
        print("开始采集失败")

if __name__ == '__main__':
    test_collect_with_images()
