import requests
import json

# 测试保存功能
def test_save_function():
    url = 'http://127.0.0.1:5001/crawler/collect/save'
    
    # 模拟前端发送的selected_ids参数
    data = {
        'selected_ids': ['1767794543-0', '1767794543-1']  # 模拟两个数据ID
    }
    
    try:
        response = requests.post(url, data=data)
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")
        
        # 解析响应
        if response.status_code == 200:
            result = response.json()
            print(f"Status: {result.get('status')}")
            print(f"Message: {result.get('message')}")
            print(f"New count: {result.get('new_count')}")
            print(f"Update count: {result.get('update_count')}")
            print(f"Saved IDs: {result.get('saved_ids')}")
        else:
            print(f"Error: {response.status_code}")
            print(f"Error message: {response.text}")
    except Exception as e:
        print(f"Request failed: {str(e)}")

if __name__ == "__main__":
    test_save_function()
