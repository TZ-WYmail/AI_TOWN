# story_director.py
import json
import re
from typing import Dict, List, Tuple
from LLM import LLMManager

class StoryDirector:
    def __init__(self):
        self.llm_manager = LLMManager()

    def generate_step_plan(self, context: Dict) -> Tuple[str, List[Dict]]:
        """
        根据当前全局状态，生成一个步骤内的动作计划和剧情摘要。
        
        返回:
            Tuple[str, List[Dict]]: (剧情摘要, 动作计划列表)
        """
        prompt = self._build_director_prompt(context)

        try:
            response = self.llm_manager.llm.chat(prompt)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                plan_data = json.loads(json_match.group())
                narrative = plan_data.get("narrative_summary", "导演正在构思...")
                action_plan = plan_data.get("action_plan", [])
                return narrative, action_plan
        except Exception as e:
            print(f"导演LLM生成计划失败: {e}")

        # 如果LLM失败，返回一个默认的计划和摘要
        return "导演暂时失语，世界陷入停滞。", []

    def _build_director_prompt(self, context: Dict) -> str:
        """构建给导演LLM的提示词"""
        scene_description = context.get("scene_description", "一个未知的地方")
        current_step = context.get("current_step", 0)
        agents = context.get("other_agents", [])
        scene_structure = context.get("scene_structure", {})
        rooms = scene_structure.get("rooms", [])
        key_events = context.get("story_outline", {}).get("key_events", [])

        # 格式化Agent信息
        agent_info_list = []
        for agent in agents:
            agent_info = (
                f"- {agent['name']} (ID: {agent['id']}):\n"
                f"  - 性格: {', '.join(agent.get('personality', []))}\n"
                f"  - 目标: {agent.get('goal', '无')}\n"
                f"  - 位置: 房间 '{agent.get('current_room', '未知')}', 坐标 ({agent.get('position', {}).get('x', 0)}, {agent.get('position', {}).get('y', 0)})\n"
                f"  - 心情: {agent.get('mood', 'neutral')}, 能量: {agent.get('energy', 100)}\n"
                f"  - 最近记忆: {agent.get('memory', [])[-1] if agent.get('memory') else '无'}"
            )
            agent_info_list.append(agent_info)

        # 格式化房间信息
        room_info_list = []
        for room in rooms:
            room_info = (
                f"- {room['name']} (ID: {room['id']}):\n"
                f"  - 描述: {room.get('description', '')}\n"
                f"  - 位置: ({room.get('x', 0)}, {room.get('y', 0)}), 尺寸: {room.get('width', 0)}x{room.get('height', 0)}\n"
                f"  - 连接到: {', '.join(room.get('connections', []))}"
            )
            room_info_list.append(room_info)

        # 查找当前步骤的关键事件
        current_key_event = next((ev for ev in key_events if ev.get("step") == current_step), None)
        key_event_str = ""
        if current_key_event:
            key_event_str = (
                f"当前步骤的关键事件是: '{current_key_event.get('description', '')}'。"
                f"请确保你的计划能推动此事件的发生。"
            )

        prompt = f"""
你是一个智能体小镇的“故事导演”。你的任务是根据当前世界的全局状态，为接下来的一小段时间（一个模拟步）编排一个连贯、有趣的剧情。

**当前世界状态:**
- **场景描述:** {scene_description}
- **当前步数:** {current_step}

**场景地图信息:**
{chr(10).join(room_info_list)}

**智能体状态:**
{chr(10).join(agent_info_list)}

**可用操作类型:**
- `move`: 移动到指定坐标
- `talk`: 与另一个智能体对话
- `interact`: 与物品或环境互动
- `investigate`: 调查当前房间
- `rest`: 休息恢复能量

{key_event_str}

**你的任务:**
请为这个模拟步生成一个包含多个动作的执行计划。计划应该像一个微型剧本，有逻辑地展开。例如，一个智能体移动到另一个房间，然后与那里的智能体对话。

**请以JSON格式返回你的计划:**
{{
  "narrative_summary": "用一句话总结这个步骤发生的剧情。",
  "action_plan": [
    {{
      "agent_id": 0,
      "action_type": "move",
      "destination": {{"x": 400, "y": 300}},
      "reasoning": "Alice想去广场看看有什么新鲜事。"
    }},
    {{
      "agent_id": 1,
      "action_type": "talk",
      "target": "Alice",
      "dialogue": "嗨，Alice，你来了！",
      "reasoning": "Bob看到Alice过来，主动打招呼。"
    }},
    {{
      "agent_id": 0,
      "action_type": "talk",
      "target": "Bob",
      "dialogue": "你好，Bob！今天有什么新消息吗？",
      "reasoning": "Alice回应Bob的问候并询问。"
    }}
  ]
}}
"""
        return prompt
