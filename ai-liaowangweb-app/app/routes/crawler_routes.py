from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from app.models.crawler import Crawler
from app.models.collect_data import CollectData
from app import db
import json
import threading
import time
from datetime import datetime
import sys
import os

crawler_bp = Blueprint('crawler', __name__, url_prefix='/crawler')

@crawler_bp.route('/')
def list_crawlers():
    crawlers = Crawler.query.all()
    return render_template('crawler/list.html', crawlers=crawlers)

@crawler_bp.route('/add', methods=['GET', 'POST'])
def add_crawler():
    if request.method == 'POST':
        name = request.form['name']
        type = request.form['type']
        status = request.form['status']
        config = request.form['config']
        
        # 验证配置是否为有效的JSON
        try:
            json.loads(config)
        except json.JSONDecodeError:
            flash('配置必须是有效的JSON格式', 'danger')
            return redirect(url_for('crawler.add_crawler'))
        
        # 检查爬虫名称是否已存在
        existing_crawler = Crawler.query.filter_by(name=name).first()
        if existing_crawler:
            flash('爬虫名称已存在', 'danger')
            return redirect(url_for('crawler.add_crawler'))
        
        new_crawler = Crawler(
            name=name,
            type=type,
            status=status,
            config=config
        )
        
        try:
            db.session.add(new_crawler)
            db.session.commit()
            flash('爬虫添加成功', 'success')
            return redirect(url_for('crawler.list_crawlers'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败: {str(e)}', 'danger')
            return redirect(url_for('crawler.add_crawler'))
    
    return render_template('crawler/add.html')

@crawler_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_crawler(id):
    crawler = Crawler.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form['name']
        type = request.form['type']
        status = request.form['status']
        config = request.form['config']
        
        # 验证配置是否为有效的JSON
        try:
            json.loads(config)
        except json.JSONDecodeError:
            flash('配置必须是有效的JSON格式', 'danger')
            return redirect(url_for('crawler.edit_crawler', id=id))
        
        # 检查爬虫名称是否已被其他爬虫使用
        existing_crawler = Crawler.query.filter_by(name=name).filter(Crawler.id != id).first()
        if existing_crawler:
            flash('爬虫名称已存在', 'danger')
            return redirect(url_for('crawler.edit_crawler', id=id))
        
        try:
            crawler.name = name
            crawler.type = type
            crawler.status = status
            crawler.config = config
            db.session.commit()
            flash('爬虫更新成功', 'success')
            return redirect(url_for('crawler.list_crawlers'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败: {str(e)}', 'danger')
            return redirect(url_for('crawler.edit_crawler', id=id))
    
    return render_template('crawler/edit.html', crawler=crawler)

@crawler_bp.route('/delete/<int:id>', methods=['POST'])
def delete_crawler(id):
    crawler = Crawler.query.get_or_404(id)
    
    try:
        db.session.delete(crawler)
        db.session.commit()
        flash('爬虫删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}', 'danger')
    
    return redirect(url_for('crawler.list_crawlers'))

@crawler_bp.route('/run/<int:id>')
def run_crawler(id):
    crawler = Crawler.query.get_or_404(id)
    
    # 导入爬虫服务
    from app.services.crawler_service import run_baidu_crawler
    
    # 根据爬虫类型运行不同的爬虫
    if crawler.type == 'baidu':
        result = run_baidu_crawler(id)
        if result['status'] == 'success':
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'danger')
    else:
        # 其他类型爬虫的处理逻辑
        try:
            crawler.last_run_at = db.func.current_timestamp()
            crawler.run_count += 1
            crawler.status = 'active'
            db.session.commit()
            flash('爬虫已启动', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'启动失败: {str(e)}', 'danger')
    
    return redirect(url_for('crawler.list_crawlers'))

# 全局变量，用于存储采集过程中的数据
collect_data = []
collect_status = {'running': False, 'current': 0, 'total': 0}

@crawler_bp.route('/collect')
def collect_page():
    """采集管理页面"""
    # 获取所有可用的爬虫源
    crawlers = Crawler.query.filter_by(status='active').all()
    return render_template('crawler/collect.html', crawlers=crawlers)

@crawler_bp.route('/collect/start', methods=['POST'])
def start_collect():
    """开始采集数据"""
    global collect_data, collect_status
    
    # 重置采集数据和状态
    collect_data = []
    collect_status = {'running': True, 'current': 0, 'total': 0}
    
    # 获取用户输入的关键字和选择的爬虫源
    keyword = request.form.get('keyword', '')
    crawler_ids = request.form.getlist('crawler_ids')
    
    if not keyword:
        return jsonify({'status': 'error', 'message': '请输入关键字'})
    
    if not crawler_ids:
        return jsonify({'status': 'error', 'message': '请选择至少一个爬虫源'})
    
    # 启动采集线程
    def collect_thread():
        global collect_data, collect_status
        
        try:
            # 导入app实例以创建应用上下文
            from app import app
            
            # 在应用上下文中执行数据库操作
            with app.app_context():
                # 获取选中的爬虫源
                selected_crawlers = Crawler.query.filter(Crawler.id.in_(crawler_ids)).all()
                
                # 导入百度搜索爬虫
                sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../dist/baidusearch')))
                from search_app import search_baidu
                
                # 根据选择的爬虫源执行不同的采集逻辑
                for crawler in selected_crawlers:
                    if crawler.type == 'baidu':
                        # 执行百度搜索采集
                        for i in range(1, 3):  # 假设采集2页数据
                            results = search_baidu(keyword, i)
                            for result in results:
                                # 为每个结果添加唯一标识、时间戳、来源和关键字
                                result['id'] = f"{int(time.time())}-{len(collect_data)}"
                                result['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                result['source'] = result.get('source', '百度搜索')
                                result['keyword'] = keyword  # 添加关键字信息
                                # 提取或生成封面图片
                                result['cover_image'] = result.get('cover_image', 'https://neeko-copilot.bytedance.net/api/text2image?prompt=news%20article%20placeholder%20image&image_size=square')
                                collect_data.append(result)
                                collect_status['current'] += 1
                                # 模拟采集延迟
                                time.sleep(0.5)
                    else:
                        # 其他类型爬虫的采集逻辑
                        # 这里可以根据需要扩展其他爬虫源的采集逻辑
                        pass
            
            collect_status['running'] = False
            collect_status['total'] = len(collect_data)
        except Exception as e:
            collect_status['running'] = False
            collect_status['error'] = str(e)
    
    # 启动线程
    threading.Thread(target=collect_thread, daemon=True).start()
    
    return jsonify({'status': 'success', 'message': '采集已开始'})

@crawler_bp.route('/collect/data')
def get_collect_data():
    """获取实时采集数据"""
    global collect_data, collect_status
    return jsonify({'data': collect_data, 'status': collect_status})

@crawler_bp.route('/collect/save', methods=['POST'])
def save_collect_data():
    """保存选中的数据到数据库"""
    global collect_data
    
    # 获取选中的数据ID
    selected_ids = request.form.getlist('selected_ids')
    
    if not selected_ids:
        return jsonify({'status': 'error', 'message': '请选择至少一条数据'})
    
    # 过滤出选中的数据
    selected_data = [item for item in collect_data if item.get('id') in selected_ids]
    
    # 保存到数据库
    saved_count = 0
    try:
        for data_item in selected_data:
            # 创建新的CollectData实例
            collect_item = CollectData(
                title=data_item.get('title'),
                url=data_item.get('url'),
                abstract=data_item.get('abstract'),
                source=data_item.get('source'),
                timestamp=datetime.strptime(data_item.get('timestamp'), '%Y-%m-%d %H:%M:%S') if data_item.get('timestamp') else datetime.utcnow(),
                cover_image=data_item.get('cover_image'),
                keyword=data_item.get('keyword')
            )
            db.session.add(collect_item)
            saved_count += 1
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': f'已保存 {saved_count} 条数据到数据库'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'保存失败: {str(e)}'})

@crawler_bp.route('/collect/status')
def get_collect_status():
    """获取采集状态"""
    global collect_status
    return jsonify(collect_status)