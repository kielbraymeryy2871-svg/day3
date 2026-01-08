from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from app.models.user import User
from app.models.crawler import Crawler
from app.models.collect_data import CollectData
import json

main = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main.route('/')
def index():
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('用户名或密码错误')
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    # 获取所有可用的爬虫源
    crawlers = Crawler.query.filter_by(status='active').all()
    return render_template('dashboard.html', crawlers=crawlers)

@main.route('/data-management')
@login_required
def data_management():
    # 显示数据管理页面
    search_keyword = request.args.get('search', '')
    return render_template('data_management.html', search_keyword=search_keyword)

@main.route('/data-management/get-data')
@login_required
def get_data():
    # 获取数据（支持分页和搜索）
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    # 构建查询
    query = CollectData.query
    
    # 模糊搜索
    if search:
        query = query.filter(
            (CollectData.title.ilike(f'%{search}%')) |
            (CollectData.abstract.ilike(f'%{search}%')) |
            (CollectData.source.ilike(f'%{search}%')) |
            (CollectData.keyword.ilike(f'%{search}%'))
        )
    
    # 按创建时间倒序排序
    query = query.order_by(CollectData.created_at.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 格式化数据
    data = []
    for item in pagination.items:
        data.append({
            'id': item.id,
            'title': item.title,
            'url': item.url,
            'abstract': item.abstract,
            'source': item.source,
            'timestamp': item.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'keyword': item.keyword,
            'type': item.type,
            'status': item.status,
            'thumbnail': item.cover_image
        })
    
    # 计算分页信息
    start_record = (page - 1) * per_page + 1
    end_record = min(page * per_page, pagination.total)
    total_pages = pagination.pages
    
    # 计算显示的页码范围
    start_page = max(1, page - 2)
    end_page = min(total_pages, start_page + 4)
    if end_page - start_page < 4:
        start_page = max(1, end_page - 4)
    
    pagination_info = {
        'total': pagination.total,
        'total_pages': total_pages,
        'current_page': page,
        'start_record': start_record,
        'end_record': end_record,
        'start_page': start_page,
        'end_page': end_page
    }
    
    return jsonify({
        'status': 'success',
        'data': data,
        'pagination': pagination_info
    })

@main.route('/data-management/delete', methods=['POST'])
@login_required
def delete_data():
    # 删除单条数据
    id = request.form.get('id', type=int)
    if not id:
        return jsonify({'status': 'error', 'message': '缺少ID参数'})
    
    try:
        data = CollectData.query.get(id)
        if not data:
            return jsonify({'status': 'error', 'message': '数据不存在'})
        
        db.session.delete(data)
        db.session.commit()
        return jsonify({'status': 'success', 'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'删除失败: {str(e)}'})

@main.route('/data-management/batch-delete', methods=['POST'])
@login_required
def batch_delete_data():
    # 批量删除数据
    ids_str = request.form.get('ids')
    if not ids_str:
        return jsonify({'status': 'error', 'message': '缺少IDs参数'})
    
    try:
        ids = json.loads(ids_str)
        if not isinstance(ids, list):
            return jsonify({'status': 'error', 'message': 'IDs格式错误'})
        
        # 批量删除
        CollectData.query.filter(CollectData.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
        return jsonify({'status': 'success', 'message': '批量删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'批量删除失败: {str(e)}'})

@main.route('/data-management/ai-collect', methods=['POST'])
@login_required
def ai_collect_data():
    # AI深度采集（后续实现）
    id = request.form.get('id', type=int)
    if not id:
        return jsonify({'status': 'error', 'message': '缺少ID参数'})
    
    # 后续实现AI深度采集逻辑
    return jsonify({'status': 'success', 'message': 'AI深度采集功能开发中'})

@main.route('/data-management/batch-ai-collect', methods=['POST'])
@login_required
def batch_ai_collect_data():
    # 批量AI深度采集（后续实现）
    ids_str = request.form.get('ids')
    if not ids_str:
        return jsonify({'status': 'error', 'message': '缺少IDs参数'})
    
    try:
        ids = json.loads(ids_str)
        if not isinstance(ids, list):
            return jsonify({'status': 'error', 'message': 'IDs格式错误'})
        
        # 后续实现批量AI深度采集逻辑
        return jsonify({'status': 'success', 'message': '批量AI深度采集功能开发中'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'批量AI深度采集失败: {str(e)}'})

@main.route('/save-collected-data', methods=['POST'])
@login_required
def save_collected_data():
    # 保存采集数据
    data = request.json.get('data', [])
    if not data:
        return jsonify({'status': 'error', 'message': '无数据可保存'})
    
    new_count = 0
    update_count = 0
    saved_ids = []
    
    try:
        for item in data:
            # 检查是否已存在（通过URL）
            existing = CollectData.query.filter_by(url=item['url']).first()
            if existing:
                # 更新现有记录
                existing.title = item.get('title', existing.title)
                existing.abstract = item.get('abstract', existing.abstract)
                existing.source = item.get('source', existing.source)
                existing.keyword = item.get('keyword', existing.keyword)
                existing.type = item.get('type', existing.type)
                existing.status = item.get('status', existing.status)
                existing.cover_image = item.get('cover_image', existing.cover_image)
                update_count += 1
            else:
                # 创建新记录
                new_data = CollectData(
                    title=item.get('title', ''),
                    url=item.get('url', ''),
                    abstract=item.get('abstract', ''),
                    source=item.get('source', ''),
                    keyword=item.get('keyword', ''),
                    type=item.get('type', '未知类型'),
                    status=item.get('status', 'completed'),
                    cover_image=item.get('cover_image', ''),
                    crawler_id=item.get('crawler_id', None)
                )
                db.session.add(new_data)
                new_count += 1
            saved_ids.append(item.get('id'))
        
        db.session.commit()
        return jsonify({
            'status': 'success', 
            'message': f'新增 {new_count} 条, 更新 {update_count} 条',
            'new_count': new_count,
            'update_count': update_count,
            'saved_ids': saved_ids
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'保存数据失败: {str(e)}'})
