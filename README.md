# AI Metropolis · The Autonomous Cinematic Operating System
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
AI Metropolis/
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
### 🔍 函数与类一览（简介）
为便于理解与扩展，这里按模块列出主要类/函数的用途与输入输出（省略不重要的内部字段）。

- agent_state_manager.py
  - `class AgentState`：单个智能体的状态与方法
    - 关键属性：`id,name,personality,goal,current_room,position,energy,mood,inventory,relationships,memory`
    - 关键方法：`update_position(x,y)`,`move_to_room(room_id)`,`add_memory(str)`,`update_relationship(other_id,change)`
  - `class AgentStateManager`
    - `initialize_agents(agent_configs, scene_structure) -> None`：根据配置创建智能体并放置到房间
    - `set_action_plan(plan: List[Dict]) -> None`：设置导演给出的“动作计划”
    - `is_plan_finished() -> bool`：当前计划是否执行完毕
    - `update_agents_with_plan(context) -> Dict`：按计划执行下一步，返回该步执行结果（含位置、情绪、能量、进度）
    - `get_agent_states() -> List[Dict]`：以渲染/导演可用的结构返回所有智能体的状态

- LLM.py
  - `class LLMCHAT(model, system, temperature, stream)`：统一封装 Kimi / OpenAI / Gemini 的聊天接口
    - `chat(user: str, stream: bool|None=None, **kwargs) -> str`：发送消息，返回字符串结果（内部可流式）
    - `change_model(model: str) -> None`：切换模型与底层客户端
  - `class LLMManager`
    - `change_model(model: str) -> None`：切换并保存配置
    - `update_config(new_config: Dict) -> None`：更新并重载配置
    - `generate_story_outline(scene_description: str, agent_count: int) -> Dict`：基于LLM生成故事大纲（失败则给默认）

- llm_config.py
  - `load_llm_config() -> Dict`：加载或返回默认 LLM 配置
  - `save_llm_config(config: Dict) -> bool`：保存配置文件
  - `get_available_models() -> List[Dict]`：返回所有模型列表
  - `get_model_info(model_id: str) -> Optional[Dict]`：按 ID 查模型信息
  - `get_provider_config(provider: str) -> Dict`：取某提供商的 `api_key/base_url`

- scene_generator.py
  - `class SceneGenerator`
    - `extract_elements(text) -> Dict`：从文本中提取名字/地点/动词等元素
    - `generate_comprehensive_scene(scene_description, agent_count, use_llm=False, max_steps=100) -> Dict`：一站式生成“故事大纲+场景结构+智能体列表”
    - 内部：`_generate_scene_with_llm(outline) -> Dict`，`_generate_default_scene(elements) -> Dict`，`_generate_agents_with_outline(outline, agent_count, use_llm) -> List[Dict]`，`_generate_default_agents(elements,num)`

- scene_map_generator.py
  - `class SceneMapGenerator`
    - `generate_scene_map(scene_data: Dict) -> Dict`：输入一个场景（或大纲场景）描述，生成可视化用的房间/路径/装饰布局

- story_outline_generator.py
  - `class StoryOutlineGenerator`
    - `generate_comprehensive_outline(scene_description, agent_count, max_steps=100) -> Dict`：调用LLM生成包含关键事件、房间结构、角色弧光的“详细大纲”，并做合法性修复
    - 内部：`_generate_default_outline(...) -> Dict`，`_generate_default_scene_structure() -> Dict`，`_validate_and_fix_outline(outline, ...) -> Dict`

- story_director.py
  - `class StoryDirector`
    - `generate_step_plan(context: Dict) -> Tuple[str, List[Dict]]`：根据全局上下文请 LLM 产出“剧情摘要 + 动作计划列表`
    - 内部：`_build_director_prompt(context) -> str`：构建导演提示词

- simulator.py
  - `class Simulator`
    - `get_instance(story_name: str) -> Simulator`：按故事名提供单例，便于逐步模拟
    - `initialize_simulation(scene_data: Dict, max_steps=100) -> Dict`：初始化（场景/智能体/大纲/步数）并返回可视化初始态
    - `simulate_step() -> Dict`：核心逐步模拟。若计划用尽，向导演要新计划，然后执行计划中的下一步，更新状态并返回结果（含 narrative_summary）
    - `run_full_simulation(scene_data: Dict, max_steps=100) -> List[Dict]`：循环调用 `simulate_step` 直到结束，返回时间线
    - 可视化辅助：`get_current_state() -> Dict`，`get_map_data() -> Dict`
  - 兼容函数
    - `run_simulation(scene, agents, steps=12) -> List[Dict]`：旧接口的适配器

- main.py（Flask 路由与服务）
  - 工具函数：`get_story_name_from_description`，`get_story_folder`，`load/save_story_config`，`load/save_story_data`，`list_stories`，`delete_story`
  - 路由：
    - `GET /`：主页；展示已有故事与默认配置
    - `POST /generate`：生成完整场景数据并持久化，返回可视化页面或 JSON
    - `GET /simulation/<story_name>`：按故事名渲染模拟页面
    - `GET /simulation`：向后兼容/重定向
    - `GET /api/stories`：返回故事列表
    - `POST /delete/<story_name>`：删除故事
    - `POST /api/simulate`：按指定步数重新生成时间线（一次性）
    - `POST /api/simulate_step`：逐步模拟（含仅获取状态）
    - `POST /api/simulate_with_llm`：在启用 LLM 的模式下重新生成时间线（一次性）
    - `GET /story_config`：故事配置页面
    - `POST /generate_story`：调用 LLM 生成故事大纲，并用 `SceneMapGenerator` 生成各场景地图
    - `GET /llm_config`：LLM 配置页面（读取可用模型）
    - `POST /api/llm_config`：保存 LLM 配置
    - `POST /api/test_llm`：切换模型并发送测试消息

### 🔗 主要调用关系（从用户到引擎）
- 生成新故事（一次性生成时间线场景数据）
  1. 前端提交到 `POST /generate`
  2. `SceneGenerator.generate_comprehensive_scene(...)`
     - 若 `use_llm=True`：`StoryOutlineGenerator.generate_comprehensive_outline(...)`（依赖 `LLMManager -> LLMCHAT`）
     - 生成场景结构、智能体、故事大纲
  3. 结果写入 `stories/<name>/config.json` 与 `data.json`，页面进入 `simulation.html`

- 逐步模拟（可被前端轮询或按钮触发）
  1. 前端调用 `POST /api/simulate_step`
  2. `Simulator.get_instance(story_name)` 获取对应模拟器
  3. 首次调用执行 `initialize_simulation(...)`（载入 `data.json` 中的 outline/scene/agents）
  4. `simulate_step()` 核心流程：
     - 若当前“动作计划”结束 → `StoryDirector.generate_step_plan(context)`（依赖 `LLMManager -> LLMCHAT`）产出“剧情摘要 + 动作计划”
     - 交由 `AgentStateManager.update_agents_with_plan(context)` 执行计划中的下一步
     - 更新智能体/事件/步数并返回结果（含 `narrative_summary` 与 `map_data`）

- 生成故事大纲与可视化地图（工具型）
  - `POST /generate_story`：`LLMManager.generate_story_outline(...)` → `SceneMapGenerator.generate_scene_map(...)`

### ✅ 开发者快速参考（输入/输出要点）
- 导演计划格式（`StoryDirector.generate_step_plan` 的返回）
  - `("narrative_summary": str, "action_plan": List[Dict])`
  - `action_plan` 的元素示例：
    - `{"agent_id": 0, "action_type": "move"|"talk"|"interact"|"investigate"|"rest", "destination": {"x":..,"y":..}, "target": "可选", "dialogue": "可选", "reasoning": "可选"}`
- 模拟单步返回（`Simulator.simulate_step`）核心字段
  - `status, step, agent_update, triggered_event, all_agent_states, scene_data, plan_progress, narrative_summary`

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