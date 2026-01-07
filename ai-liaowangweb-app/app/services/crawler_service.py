import sys
import os
import json
from datetime import datetime

# 添加百度搜索爬虫模块的路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../dist/baidusearch')))

from app.models.crawler import Crawler
from app import db

try:
    from search_app import search_baidu
except ImportError as e:
    print(f"导入百度搜索爬虫模块失败: {e}")
    search_baidu = None

def run_baidu_crawler(crawler_id):
    """运行百度搜索爬虫"""
    crawler = Crawler.query.get_or_404(crawler_id)
    
    # 更新爬虫状态
    crawler.status = 'active'
    crawler.last_run_at = datetime.utcnow()
    crawler.run_count += 1
    
    try:
        # 解析爬虫配置
        config = json.loads(crawler.config)
        keywords = config.get('keywords', [])
        max_pages = config.get('max_pages', 1)
        
        # 检查百度搜索爬虫模块是否可用
        if not search_baidu:
            raise Exception("百度搜索爬虫模块未找到")
        
        # 执行搜索
        all_results = []
        for keyword in keywords:
            for page in range(1, max_pages + 1):
                results = search_baidu(keyword, page)
                all_results.extend(results)
                
        # 这里可以添加结果处理逻辑，比如存储到数据库
        # 暂时只更新成功计数
        crawler.success_count += 1
        db.session.commit()
        
        return {
            'status': 'success',
            'message': f'百度搜索爬虫执行成功，获取 {len(all_results)} 条结果',
            'results_count': len(all_results)
        }
        
    except Exception as e:
        # 更新失败计数
        crawler.failure_count += 1
        db.session.commit()
        
        return {
            'status': 'error',
            'message': f'百度搜索爬虫执行失败: {str(e)}'
        }

def stop_crawler(crawler_id):
    """停止爬虫"""
    crawler = Crawler.query.get_or_404(crawler_id)
    crawler.status = 'inactive'
    db.session.commit()
    
    return {
        'status': 'success',
        'message': '爬虫已停止'
    }

def get_crawler_status(crawler_id):
    """获取爬虫状态"""
    crawler = Crawler.query.get_or_404(crawler_id)
    
    return {
        'id': crawler.id,
        'name': crawler.name,
        'status': crawler.status,
        'last_run_at': crawler.last_run_at.strftime('%Y-%m-%d %H:%M:%S') if crawler.last_run_at else None,
        'run_count': crawler.run_count,
        'success_count': crawler.success_count,
        'failure_count': crawler.failure_count
    }
