from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.models.ai_model import AIModel, AITokenStats
from app import db
import json

ai_routes = Blueprint('ai', __name__)

@ai_routes.route('/')
@login_required
def ai_page():
    return render_template('ai_page.html')

@ai_routes.route('/models', methods=['GET'])
def get_models():
    models = AIModel.query.all()
    model_list = []
    for model in models:
        # 计算总token消耗
        total_tokens = db.session.query(db.func.sum(AITokenStats.total_tokens)).filter_by(model_id=model.id).scalar() or 0
        model_list.append({
            'id': model.id,
            'name': model.name,
            'api_url': model.api_url,
            'model_name': model.model_name,
            'status': model.status,
            'description': model.description,
            'total_tokens': total_tokens
        })
    return jsonify(model_list)

@ai_routes.route('/models', methods=['POST'])
@login_required
def add_model():
    data = request.json
    try:
        new_model = AIModel(
            name=data['name'],
            api_url=data['api_url'],
            api_key=data['api_key'],
            model_name=data['model_name'],
            system_prompt=data.get('system_prompt'),
            description=data.get('description'),
            status='active'
        )
        db.session.add(new_model)
        db.session.commit()
        return jsonify({'success': True, 'model_id': new_model.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@ai_routes.route('/models/<int:model_id>', methods=['GET'])
@login_required
def get_model(model_id):
    model = AIModel.query.get(model_id)
    if not model:
        return jsonify({'success': False, 'error': '模型不存在'}), 404
    return jsonify({
        'id': model.id,
        'name': model.name,
        'api_url': model.api_url,
        'api_key': model.api_key,
        'model_name': model.model_name,
        'system_prompt': model.system_prompt,
        'status': model.status,
        'description': model.description
    })

@ai_routes.route('/models/<int:model_id>', methods=['PUT'])
@login_required
def update_model(model_id):
    data = request.json
    model = AIModel.query.get(model_id)
    if not model:
        return jsonify({'success': False, 'error': '模型不存在'}), 404
    try:
        model.name = data['name']
        model.api_url = data['api_url']
        model.api_key = data['api_key']
        model.model_name = data['model_name']
        model.system_prompt = data.get('system_prompt')
        model.status = data['status']
        model.description = data.get('description')
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@ai_routes.route('/models/<int:model_id>', methods=['DELETE'])
@login_required
def delete_model(model_id):
    model = AIModel.query.get(model_id)
    if not model:
        return jsonify({'success': False, 'error': '模型不存在'}), 404
    try:
        # 删除相关的token统计数据
        AITokenStats.query.filter_by(model_id=model_id).delete()
        # 删除模型
        db.session.delete(model)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@ai_routes.route('/inference', methods=['POST'])
def inference():
    from app.services.ai_service import AIService
    
    # 实现AI推理接口
    data = request.json
    model_id = data.get('model_id')
    prompt = data.get('prompt')
    
    model = AIModel.query.get(model_id)
    if not model:
        return jsonify({'success': False, 'error': '模型不存在'}), 404
    
    # 调用AI服务获取响应
    ai_service = AIService()
    result = ai_service.infer(
        model_config={
            'api_key': model.api_key,
            'api_url': model.api_url,
            'model_name': model.model_name
        },
        prompt=prompt,
        system_prompt=model.system_prompt
    )
    
    # 记录token消耗
    if result['success']:
        try:
            token_stats = AITokenStats(
                model_id=model_id,
                prompt_tokens=result['usage']['prompt_tokens'],
                completion_tokens=result['usage']['completion_tokens'],
                total_tokens=result['usage']['total_tokens'],
                usage_type='inference'
            )
            db.session.add(token_stats)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"记录token消耗失败: {e}")
    
    return jsonify(result)

@ai_routes.route('/test', methods=['POST'])
def test_model():
    from app.services.ai_service import AIService
    
    data = request.json
    model_id = data.get('model_id')
    prompt = data.get('prompt')
    
    model = AIModel.query.get(model_id)
    if not model:
        return jsonify({'success': False, 'error': '模型不存在'}), 404
    
    # 调用AI服务获取响应
    ai_service = AIService()
    result = ai_service.infer(
        model_config={
            'api_key': model.api_key,
            'api_url': model.api_url,
            'model_name': model.model_name
        },
        prompt=prompt,
        system_prompt=model.system_prompt
    )
    
    # 记录token消耗
    if result['success']:
        try:
            token_stats = AITokenStats(
                model_id=model_id,
                prompt_tokens=result['usage']['prompt_tokens'],
                completion_tokens=result['usage']['completion_tokens'],
                total_tokens=result['usage']['total_tokens'],
                usage_type='test'
            )
            db.session.add(token_stats)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"记录token消耗失败: {e}")
    
    return jsonify(result)
