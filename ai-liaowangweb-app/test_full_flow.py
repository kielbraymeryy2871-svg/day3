import requests
import time

# 测试完整的采集和保存流程
base_url = 'http://127.0.0.1:5001'

def test_collect_start():
    """测试开始采集"""
    print("=== 测试开始采集 ===")
    data = {
        'keyword': 'Python',
        'crawler_ids': ['1']  # 假设爬虫ID为1
    }
    
    response = requests.post(f'{base_url}/crawler/collect/start', data=data)
    print(f"Start collect response: {response.json()}")
    return response.json()

def test_collect_data():
    """测试获取采集数据"""
    print("\n=== 测试获取采集数据 ===")
    response = requests.get(f'{base_url}/crawler/collect/data')
    data = response.json()
    print(f"Collect data status: {data['status']}")
    print(f"Collect data length: {len(data['data'])}")
    if data['data']:
        print(f"First item: {data['data'][0].get('title')}")
        print(f"First item ID: {data['data'][0].get('id')}")
    return data

def test_save_data(selected_ids):
    """测试保存数据"""
    print(f"\n=== 测试保存数据 ===")
    print(f"Selected IDs: {selected_ids}")
    
    data = {'selected_ids': selected_ids}
    response = requests.post(f'{base_url}/crawler/collect/save', data=data)
    result = response.json()
    print(f"Save response: {result}")
    return result

if __name__ == '__main__':
    # 1. 开始采集
    start_result = test_collect_start()
    if start_result.get('status') == 'success':
        # 2. 等待采集完成
        print("\n等待采集完成...")
        time.sleep(10)  # 等待10秒让采集完成
        
        # 3. 获取采集数据
        collect_data = test_collect_data()
        
        # 4. 测试保存数据
        if collect_data['data']:
            selected_ids = [item.get('id') for item in collect_data['data'][:2]]  # 选择前2条
            save_result = test_save_data(selected_ids)
        else:
            print("没有采集到数据，无法测试保存功能")
    else:
        print("开始采集失败")
