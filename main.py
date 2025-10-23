# main.py
import json
import sys
import os
import webbrowser
import shutil
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from scene_generator import SceneGenerator
from simulator import Simulator
from LLM import LLMManager
from scene_map_generator import SceneMapGenerator

app = Flask(__name__)

# 创建全局实例
scene_generator = SceneGenerator()

# 故事存储目录
STORIES_DIR = "stories"
os.makedirs(STORIES_DIR, exist_ok=True)

# 默认配置
DEFAULT_CONFIG = {
    "scene_description": "A small mysterious town with rumors about a lost artifact near the old station.",
    "agent_count": 4,
    "auto_play": True,
    "show_bubbles": True,
    "animation_speed": 900,
    "use_llm": False,
    "max_steps": 100
}

def get_story_name_from_description(description):
    """从场景描述中提取前5个字符作为故事名"""
    import re
    story_name = description[:5].strip()
    story_name = re.sub(r'[^\w\-_\.]', '_', story_name)
    return story_name if story_name else "untitled"

def get_story_folder(story_name):
    """获取故事文件夹路径"""
    return os.path.join(STORIES_DIR, story_name)

def load_story_config(story_name):
    """加载指定故事的配置"""
    story_path = get_story_folder(story_name)
    config_file = os.path.join(story_path, "config.json")
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_story_config(story_name, config):
    """保存故事配置到指定文件夹"""
    story_path = get_story_folder(story_name)
    os.makedirs(story_path, exist_ok=True)
    config_file = os.path.join(story_path, "config.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def save_story_data(story_name, data):
    """保存故事数据到指定文件夹"""
    story_path = get_story_folder(story_name)
    os.makedirs(story_path, exist_ok=True)
    data_file = os.path.join(story_path, "data.json")
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_story_data(story_name):
    """加载指定故事的数据"""
    story_path = get_story_folder(story_name)
    data_file = os.path.join(story_path, "data.json")
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def list_stories():
    """列出所有故事"""
    stories = []
    if os.path.exists(STORIES_DIR):
        for folder in os.listdir(STORIES_DIR):
            story_path = os.path.join(STORIES_DIR, folder)
            if os.path.isdir(story_path):
                config_file = os.path.join(story_path, "config.json")
                if os.path.exists(config_file):
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        created_time = os.path.getmtime(story_path)
                        created_str = datetime.fromtimestamp(created_time).strftime('%Y-%m-%d %H:%M')
                        stories.append({
                            "name": folder,
                            "description": config.get("scene_description", ""),
                            "agent_count": config.get("agent_count", 0),
                            "created": created_str,
                            "created_timestamp": created_time
                        })
    return sorted(stories, key=lambda x: x["created_timestamp"], reverse=True)

def delete_story(story_name):
    """删除指定故事"""
    story_path = get_story_folder(story_name)
    if os.path.exists(story_path):
        shutil.rmtree(story_path)
        return True
    return False

def generate_simulation_data(config, steps, use_llm=False):
    """生成模拟数据"""
    elements = scene_generator.extract_elements(config["scene_description"])
    scene = scene_generator.generate_scene(elements, use_llm=use_llm)
    agents = scene_generator.generate_agents(elements, num=config["agent_count"], use_llm=use_llm)
    
    simulator = Simulator()
    timeline = simulator.run_simulation(scene, agents, steps=steps, use_llm=use_llm)
    
    data = {
        "scene": scene,
        "agents": agents,
        "timeline": timeline,
        "config": config,
        "use_llm": use_llm
    }
    
    return data

@app.route('/')
def index():
    """主页面 - 配置和查看界面"""
    stories = list_stories()
    return render_template('index.html', stories=stories, default_config=DEFAULT_CONFIG)


@app.route('/generate', methods=['POST'])
def generate():
    """生成新的模拟"""
    config = {
        "scene_description": request.form.get('scene_description', DEFAULT_CONFIG["scene_description"]),
        "agent_count": int(request.form.get('agent_count', DEFAULT_CONFIG["agent_count"])),
        "auto_play": request.form.get('auto_play') == 'on',
        "show_bubbles": request.form.get('show_bubbles') == 'on',
        "animation_speed": int(request.form.get('animation_speed', DEFAULT_CONFIG["animation_speed"])),
        "use_llm": request.form.get('use_llm') == 'on',
        "max_steps": int(request.form.get('max_steps', 100))
    }
    
    story_name = get_story_name_from_description(config["scene_description"])
    save_story_config(story_name, config)
    
    # 生成完整场景数据
    scene_data = scene_generator.generate_comprehensive_scene(
        config["scene_description"], 
        config["agent_count"], 
        config["use_llm"],
        config["max_steps"]
    )
    
    save_story_data(story_name, scene_data)
    
    return render_template('simulation.html', data=scene_data, story_name=story_name)



@app.route('/load/<story_name>')
def load_story(story_name):
    """加载已有故事"""
    config = load_story_config(story_name)
    if config:
        data = load_story_data(story_name)
        if data:
            return render_template('simulation.html', data=data, story_name=story_name)
    return "故事不存在", 404

@app.route('/delete/<story_name>', methods=['POST'])
def delete_story_route(story_name):
    """删除故事"""
    if delete_story(story_name):
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "删除失败"}), 400

@app.route('/api/stories')
def get_stories():
    """API: 获取所有故事列表"""
    return jsonify(list_stories())

@app.route('/api/simulate', methods=['POST'])
def api_simulate():
    """API: 重新模拟指定步数"""
    data = request.json
    story_name = data.get("story_name")
    steps = int(data.get("steps", 14))
    
    if not story_name:
        return jsonify({"status": "error", "message": "缺少故事名"}), 400
    
    config = load_story_config(story_name)
    if not config:
        return jsonify({"status": "error", "message": "故事不存在"}), 404
    
    new_data = generate_simulation_data(config, steps=steps, use_llm=config.get("use_llm", False))
    save_story_data(story_name, new_data)
    
    return jsonify({"status": "success", "data": new_data})

@app.route('/story_config')
def story_config():
    """故事配置页面"""
    return render_template('story_config.html')

@app.route('/generate_story', methods=['POST'])
def generate_story():
    """生成完整故事"""
    data = request.json
    scene_description = data.get('scene_description', '')
    agent_count = int(data.get('agent_count', 4))
    use_llm = data.get('use_llm', False)
    
    llm_manager = LLMManager()
    story_outline = llm_manager.generate_story_outline(scene_description, agent_count)
    
    map_generator = SceneMapGenerator()
    scenes = []
    
    for scene_data in story_outline.get('scenes', []):
        scene_map = map_generator.generate_scene_map(scene_data)
        scenes.append(scene_map)
    
    return jsonify({
        'outline': story_outline,
        'scenes': scenes
    })

@app.route('/api/llm_config', methods=['POST'])
def update_llm_config():
    """更新LLM配置"""
    from llm_config import save_llm_config
    
    config = request.json
    if save_llm_config(config):
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "保存失败"}), 400

@app.route('/api/simulate_step', methods=['POST'])
def simulate_step():
    """模拟单步"""
    data = request.json
    story_name = data.get("story_name")
    
    if not story_name:
        return jsonify({"status": "error", "message": "缺少故事名"}), 400
    
    story_data = load_story_data(story_name)
    if not story_data:
        return jsonify({"status": "error", "message": "故事不存在"}), 404
    
    # 使用单例模式获取模拟器实例
    simulator = Simulator.get_instance(story_name)
    
    # 如果还没有初始化，先初始化
    if not hasattr(simulator, 'current_step') or simulator.current_step == 0:
        story_data["story_name"] = story_name  # 添加故事名
        simulator.initialize_simulation(story_data)
    
    step_result = simulator.simulate_step()
    
    # 保存更新后的数据
    story_data['agent_states'] = simulator.agent_manager.get_agent_states()
    story_data['current_step'] = simulator.current_step
    story_data['agents'] = simulator.agents  # 保存更新后的智能体数据
    save_story_data(story_name, story_data)
    
    return jsonify({
        "status": "success",
        "data": step_result,
        "current_state": simulator.get_current_state(),
        "map_data": simulator.get_map_data()  # 添加地图数据
    })



@app.route('/api/simulate_with_llm', methods=['POST'])
def simulate_with_llm():
    """使用LLM进行模拟"""
    data = request.json
    story_name = data.get('story_name')
    steps = int(data.get('steps', 14))
    use_llm = data.get('use_llm', False)
    
    if not story_name:
        return jsonify({"status": "error", "message": "缺少故事名"}), 400
    
    config = load_story_config(story_name)
    if not config:
        return jsonify({"status": "error", "message": "故事不存在"}), 404
    
    elements = scene_generator.extract_elements(config["scene_description"])
    scene = scene_generator.generate_scene(elements, use_llm=use_llm)
    agents = scene_generator.generate_agents(elements, num=config["agent_count"], use_llm=use_llm)
    
    simulator = Simulator()
    timeline = simulator.run_simulation(scene, agents, steps=steps, use_llm=use_llm)
    
    new_data = {
        "scene": scene,
        "agents": agents,
        "timeline": timeline,
        "config": config,
        "use_llm": use_llm
    }
    
    save_story_data(story_name, new_data)
    
    return jsonify({"status": "success", "data": new_data})

@app.route('/llm_config')
def llm_config():
    """LLM配置页面"""
    from llm_config import load_llm_config, get_available_models
    config = load_llm_config()
    models = get_available_models()
    return render_template('llm_config.html', config=config, models=models)

@app.route('/api/test_llm', methods=['POST'])
def test_llm():
    """测试LLM连接"""
    try:
        from LLM import LLMManager
        model = request.json.get('model', 'kimi-k2-turbo-preview')
        llm_manager = LLMManager()
        llm_manager.change_model(model)
        
        response = llm_manager.llm.chat("请回复'连接成功'")
        return jsonify({"status": "success", "response": response})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    os.makedirs('templates', exist_ok=True)
    
    print("AI小镇系统已启动!")
    print("访问 http://127.0.0.1:5000 开始使用")
    webbrowser.open('http://127.0.0.1:5000')
    app.run(debug=False, port=5000)
