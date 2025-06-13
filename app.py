from flask import Flask, render_template, request, jsonify
import os
import json
from trajectory_prediction.data import get_trajectory

app = Flask(__name__)

# 确保上传文件夹存在
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 模型文件夹路径
MODELS_DIR = os.path.join(app.static_folder, 'models')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/maritime')
def maritime():
    return render_template('maritime.html')

@app.route('/emergency')
def emergency():
    return render_template('emergency_rescue.html')

@app.route('/api')
def api():
    return render_template('api_access.html')

@app.route('/api/models')
def get_models():
    try:
        models = []
        # 检查模型目录是否存在
        if not os.path.exists(MODELS_DIR):
            print(f"Models directory not found: {MODELS_DIR}")
            return jsonify([])

        # 遍历模型目录
        for model_dir in os.listdir(MODELS_DIR):
            model_path = os.path.join(MODELS_DIR, model_dir)
            if os.path.isdir(model_path):  # 确保是目录
                metadata_path = os.path.join(model_path, 'metadata.json')
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            models.append({
                                'id': model_dir,
                                'name': metadata.get('name', model_dir),
                                'version': metadata.get('version', '1.0'),
                                'description': metadata.get('description', ''),
                                'type': metadata.get('type', 'unknown')
                            })
                    except Exception as e:
                        print(f"Error reading metadata for {model_dir}: {str(e)}")
                else:
                    # 如果没有metadata文件，添加基本信息
                    models.append({
                        'id': model_dir,
                        'name': model_dir,
                        'version': '1.0',
                        'description': '无描述信息',
                        'type': 'unknown'
                    })
        
        print(f"Found {len(models)} models: {models}")  # 调试信息
        return jsonify(models)
    except Exception as e:
        print(f"Error loading models: {str(e)}")  # 调试信息
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/<model_id>')
def get_model_details(model_id):
    try:
        model_path = os.path.join(MODELS_DIR, model_id)
        metadata_path = os.path.join(model_path, 'metadata.json')
        
        if not os.path.exists(model_path):
            return jsonify({'error': 'Model not found'}), 404
            
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                return jsonify(metadata)
        else:
            # 返回基本信息
            return jsonify({
                'id': model_id,
                'name': model_id,
                'version': '1.0',
                'description': '无描述信息',
                'type': 'unknown'
            })
    except Exception as e:
        print(f"Error getting model details for {model_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': '没有上传图片'}), 400
    
    # 这里先返回模拟数据，后续我们会集成真实的模型
    return jsonify({
        'class_name': '测试物体',
        'confidence': 0.95
    })

# API endpoints
@app.route('/api/v1/vessels', methods=['GET'])
def get_vessels():
    # 模拟返回船只数据
    return jsonify({
        'vessels': [
            {
                'id': 'VS123',
                'location': {
                    'latitude': 30.2,
                    'longitude': 120.5
                },
                'status': 'active'
            }
        ]
    })

@app.route('/api/v1/rescue/request', methods=['POST'])
def rescue_request():
    # 处理救援请求
    data = request.json
    # 这里添加实际的救援请求处理逻辑
    return jsonify({
        'status': 'accepted',
        'rescue_id': 'R789'
    })

@app.route('/weather_map')
def weather_map():
    return render_template('weather_map.html')

@app.route('/trajectory')
def trajectory():
    return render_template('trajectory.html')

@app.route('/trajectory_result')
def trajectory_result():
    return render_template('trajectory_result.html')

@app.route('/api/predict_trajectory', methods=['POST'])
def predict_trajectory_api():
    try:
        data = request.get_json()
        
        # 验证必要的输入参数
        required_fields = ['latitude', 'longitude', 'time', 'model_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必要参数: {field}'}), 400
        
        # 获取输入参数
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        time_steps = int(data['time'])
        
        # 验证坐标范围
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return jsonify({'error': '无效的坐标范围'}), 400
            
        # 使用预测模型进行预测
        trajectory_points = get_trajectory(longitude, latitude, time_steps)
        
        if not trajectory_points:
            return jsonify({'error': '预测失败'}), 500
            
        # 格式化轨迹点
        formatted_trajectory = []
        for i, point in enumerate(trajectory_points):
            formatted_trajectory.append({
                'longitude': float(point[0]),
                'latitude': float(point[1]),
                'time': f'{i + 1}小时后'
            })
            
        return jsonify({
            'status': 'success',
            'trajectory': formatted_trajectory,
            'model_info': {
                'id': data['model_id'],
                'confidence': 0.85
            }
        })
        
    except ValueError as e:
        return jsonify({'error': '输入参数格式错误'}), 400
    except Exception as e:
        print(f"预测错误: {str(e)}")
        return jsonify({'error': '预测过程中发生错误'}), 500

def find_nearest_points(target_lat, target_lon, num_points=5):
    """
    从particle_NS.dat文件中找到距离目标点最近的num_points个点
    
    参数:
    target_lat: 目标纬度
    target_lon: 目标经度
    num_points: 需要返回的最近点数量（默认为5）
    
    返回:
    list: 包含最近点信息的列表，每个元素为(id, latitude, longitude, distance)元组
    """
    try:
        # 读取数据文件
        points = []
        with open('trajectory_prediction/particle_NS.dat', 'r') as f:
            # 跳过第一行（点的总数）
            next(f)
            # 读取所有点
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 4:  # 确保行有足够的数据
                    point_id = int(parts[0])
                    lon = float(parts[1])
                    lat = float(parts[2])
                    # 计算与目标点的距离（使���欧几里得距离）
                    distance = ((lat - target_lat) ** 2 + (lon - target_lon) ** 2) ** 0.5
                    points.append((point_id, lat, lon, distance))
        
        # 按距离排序并返回最近的n个点
        points.sort(key=lambda x: x[3])
        return points[:num_points]
    
    except Exception as e:
        print(f"Error finding nearest points: {str(e)}")
        return []

# 添加API端点
@app.route('/api/nearest_points', methods=['GET'])
def get_nearest_points():
    try:
        # 获取请求参数
        lat = float(request.args.get('latitude', 0))
        lon = float(request.args.get('longitude', 0))
        num_points = int(request.args.get('num_points', 5))
        
        # 查找最近的点
        nearest_points = find_nearest_points(lat, lon, num_points)
        
        # 格式化返回结果
        result = [{
            'id': point[0],
            'latitude': point[1],
            'longitude': point[2],
            'distance': point[3]
        } for point in nearest_points]
        
        return jsonify({
            'status': 'success',
            'points': result
        })
        
    except ValueError as e:
        return jsonify({'error': '无效的参数格式'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')