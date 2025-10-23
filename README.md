# AI Town - 智能体驱动的交互式故事生成系统
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![LLM](https://img.shields.io/badge/LLM-Kimi%20%7C%20OpenAI%20%7C%20Gemini-orange.svg)](https://github.com)
一个基于大语言模型(LLM)的智能体交互系统，创建动态生成的虚拟世界，其中多个AI智能体自主行动、互动并共同推进故事情节。
## ✨ 核心特性
- 🤖 **智能体系统**：具有个性、目标和记忆的自主AI智能体
- 🌍 **动态场景生成**：自动创建具有房间、连接和互动元素的场景
- 📖 **故事引擎**：基于智能体行为生成连贯的故事情节
- 🎮 **可视化界面**：实时观察智能体行动和故事进展
- 🔧 **多LLM支持**：兼容Kimi、OpenAI和Gemini模型
- 💾 **故事管理**：保存、加载和管理多个故事项目
## 🚀 快速开始
### 环境要求
- Python 3.8+
- 有效的LLM API密钥（Kimi/OpenAI/Gemini）
### 安装步骤
```
1. 安装依赖
```bash
pip install -r requirements.txt
```
3. 配置LLM API密钥
编辑 `llm_config.json` 文件，添加您的API密钥：
```json
{
  "api_keys": {
    "kimi": "your_kimi_api_key",
    "openai": "your_openai_api_key",
    "gemini": "your_gemini_api_key"
  }
}
```
4. 启动应用
```bash
python main.py
```
5. 访问Web界面
打开浏览器访问 [http://127.0.0.1:5000](http://127.0.0.1:5000)
## 🎮 使用指南
### 创建新故事
1. 在主界面配置故事参数：
   - 场景描述（如："一个神秘的小镇，传闻在旧车站附近有失落的神器"）
   - 智能体数量（2-8个）
   - 最大步数（故事长度）
   - 是否启用LLM增强
2. 点击"生成故事"创建新世界
### 观察智能体互动
- 智能体会根据其个性和目标自主行动
- 实时查看位置变化、对话和互动
- 观察故事情节的动态发展
### 管理故事项目
- 在主界面查看所有已创建的故事
- 加载、删除或重新生成故事
- 每个故事独立保存配置和进度
## 🏗️ 系统架构
```
AI Town/
├── agent_state_manager.py  # 智能体状态管理
├── LLM.py                 # LLM接口封装
├── llm_config.py          # LLM配置管理
├── scene_generator.py     # 场景生成器
├── scene_map_generator.py # 地图生成器
├── simulator.py           # 故事模拟引擎
├── story_outline_generator.py # 故事大纲生成
├── main.py                # Web应用入口
└── templates/             # 前端模板
```
### 核心组件
1. **智能体系统** (`agent_state_manager.py`)
   - 管理智能体状态（位置、情绪、能量等）
   - 处理智能体决策和行动
   - 维护智能体间关系
2. **LLM集成** (`LLM.py`)
   - 统一接口支持多种LLM模型
   - 智能体行为生成
   - 故事情节推进
3. **场景生成** (`scene_generator.py`)
   - 从文本描述提取场景元素
   - 生成房间布局和连接关系
   - 创建互动元素
4. **模拟引擎** (`simulator.py`)
   - 协调智能体行动
   - 推进故事时间线
   - 处理事件触发
## 🎯 应用场景
- **教育**：展示AI决策和交互原理
- **创意写作**：生成故事灵感和情节
- **游戏设计**：原型NPC行为系统
- **研究**：多智能体系统研究平台
## 🛠️ 配置选项
在 `llm_config.json` 中可配置：
- API密钥和端点
- 默认LLM模型
- 温度和令牌限制
- 可用模型列表
## 🤝 贡献指南
我们欢迎各种形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。
1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request
## 📄 许可证
本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

⭐ 如果这个项目对您有帮助，请给我们一个星标！

--------------------------------
以上内容由AI生成，仅供参考和借鉴