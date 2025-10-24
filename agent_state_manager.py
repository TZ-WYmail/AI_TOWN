# agent_state_manager.py
import json
import random
import re
from typing import Dict, List, Tuple, Optional
from LLM import LLMManager

class AgentState:
    def __init__(self, agent_id: int, name: str, personality: List[str], goal: str):
        self.id = agent_id
        self.name = name
        self.personality = personality
        self.goal = goal
        self.current_room = None
        self.position = {"x": 0, "y": 0}
        self.health = 100
        self.energy = 100
        self.mood = "neutral"
        self.inventory = []
        self.relationships = {}
        self.memory = []
        self.current_action = None
        self.action_cooldown = 0
        self.knowledge = {}
        
    def update_position(self, x: int, y: int):
        """更新位置"""
        self.position["x"] = x
        self.position["y"] = y
        
    def move_to_room(self, room_id: str):
        """移动到指定房间"""
        self.current_room = room_id
        
    def add_memory(self, memory: str):
        """添加记忆"""
        self.memory.append({
            "content": memory,
            "timestamp": len(self.memory),
            "importance": 1.0
        })
        
    def update_relationship(self, other_agent_id: int, change: float):
        """更新与其他角色的关系"""
        if other_agent_id not in self.relationships:
            self.relationships[other_agent_id] = 0.0
        self.relationships[other_agent_id] += change
        self.relationships[other_agent_id] = max(-1.0, min(1.0, self.relationships[other_agent_id]))

class AgentStateManager:
    def __init__(self):
        self.llm_manager = LLMManager()
        self.agents: Dict[int, AgentState] = {}
        self.current_step = 0
        self.current_action_plan: List[Dict] = [] # 新增：存储当前步骤的动作计划
        self.current_action_index = 0 # 新增：当前执行到动作计划的第几步
        
    def initialize_agents(self, agent_configs: List[Dict], scene_structure: Dict):
        self.agents.clear()
        for i, config in enumerate(agent_configs):
            agent = AgentState(
                agent_id=i,
                name=config["name"],
                personality=config["personality"],
                goal=config["goal"]
            )
            rooms = scene_structure["rooms"]
            if rooms:
                initial_room = random.choice(rooms)
                agent.current_room = initial_room["id"]
                agent.position["x"] = initial_room["x"] + initial_room["width"] // 2
                agent.position["y"] = initial_room["y"] + initial_room["height"] // 2
            self.agents[i] = agent

    # --- 修改：不再由单个Agent决定行动，而是执行一个预定的计划 ---
    def update_agents_with_plan(self, context: Dict) -> Dict:
        """根据动作计划更新所有智能体"""
        if not self.current_action_plan or self.current_action_index >= len(self.current_action_plan):
            return {"status": "no_plan", "reason": "没有可执行的动作计划或计划已执行完毕"}

        action_to_execute = self.current_action_plan[self.current_action_index]
        agent_id = action_to_execute.get("agent_id")
        agent = self.agents.get(agent_id)

        if not agent:
            return {"status": "error", "reason": f"未找到ID为 {agent_id} 的智能体"}

        # 执行动作
        result = self._execute_action(agent, action_to_execute, context)
        self._update_agent_state(agent, action_to_execute, result)

        # 移动到计划中的下一个动作
        self.current_action_index += 1

        return {
            "status": "executed",
            "agent_id": agent_id,
            "action": action_to_execute,
            "result": result,
            "position": agent.position.copy(),
            "current_room": agent.current_room,
            "mood": agent.mood,
            "energy": agent.energy,
            "plan_progress": f"{self.current_action_index}/{len(self.current_action_plan)}"
        }

    def set_action_plan(self, plan: List[Dict]):
        """设置新的动作计划"""
        self.current_action_plan = plan
        self.current_action_index = 0

    def is_plan_finished(self) -> bool:
        """检查当前动作计划是否已执行完毕"""
        return not self.current_action_plan or self.current_action_index >= len(self.current_action_plan)

    # --- 以下方法大部分保持不变，但 _generate_agent_action 不再被主流程调用 ---
    def _generate_agent_action(self, agent: AgentState, context: Dict) -> Dict:
        """(已弃用) 使用LLM生成智能体行动"""
        """使用LLM生成智能体行动"""
        other_agents = [a for a in self.agents.values() if a.id != agent.id]
        
        prompt = f"""
        你是{agent.name}，性格：{', '.join(agent.personality)}，目标：{agent.goal}。
        
        当前状态：
        - 位置：{agent.current_room} ({agent.position['x']}, {agent.position['y']})
        - 心情：{agent.mood}
        - 能量：{agent.energy}
        - 物品：{', '.join(agent.inventory) if agent.inventory else '无'}
        
        当前环境：
        - 场景描述：{context.get('scene_description', '')}
        - 同房间角色：{', '.join([a.name for a in other_agents if a.current_room == agent.current_room])}
        - 可用物品：{', '.join(context.get('available_items', []))}
        
        最近记忆：{agent.memory[-3:] if agent.memory else '无'}
        
        请决定下一步行动。以JSON格式返回：
        {{
            "action_type": "move/talk/interact/investigate/rest/use_item",
            "target": "目标对象（角色名、物品名或房间名）",
            "dialogue": "要说的话（如果action_type是talk）",
            "destination": {{"x": 100, "y": 100}},
            "expected_outcome": "预期结果",
            "reasoning": "行动原因",
            "priority": "high/medium/low"
        }}
        """
        
        try:
            response = self.llm_manager.llm.chat(prompt)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"LLM生成行动失败: {e}")
        
        return self._generate_default_action(agent)

    def _generate_default_action(self, agent: AgentState) -> Dict:
        """生成默认行动"""
        actions = ["move", "investigate", "rest"]
        action_type = random.choice(actions)
        
        return {
            "action_type": action_type,
            "target": None,
            "dialogue": f"{agent.name}: 继续探索...",
            "destination": {
                "x": agent.position["x"] + random.randint(-50, 50),
                "y": agent.position["y"] + random.randint(-50, 50)
            },
            "expected_outcome": "探索新区域",
            "reasoning": "随机探索",
            "priority": "medium"
        }
    
    def _execute_action(self, agent: AgentState, action: Dict, context: Dict) -> Dict:
        """执行行动"""
        action_type = action.get("action_type", "move")
        result = {"success": True, "details": ""}
        
        if action_type == "move":
            dest = action.get("destination", {})
            new_x = dest.get("x", agent.position["x"])
            new_y = dest.get("y", agent.position["y"])
            
            current_room_data = self._get_room_data(agent.current_room, context)
            if current_room_data:
                if self._is_position_in_room(new_x, new_y, current_room_data):
                    agent.update_position(new_x, new_y)
                    result["details"] = f"移动到 ({new_x}, {new_y})"
                else:
                    result["success"] = False
                    result["details"] = "无法移动到该位置"
        
        elif action_type == "talk":
            target = action.get("target")
            if target:
                target_agent = self._find_agent_by_name(target)
                if target_agent and target_agent.current_room == agent.current_room:
                    dialogue = action.get("dialogue", f"{agent.name}: 你好")
                    result["details"] = f"对{target}说：{dialogue}"
                    agent.update_relationship(target_agent.id, 0.1)
                else:
                    result["success"] = False
                    result["details"] = f"{target}不在这里"
        
        elif action_type == "interact":
            target = action.get("target")
            result["details"] = f"与{target}互动"
        
        elif action_type == "investigate":
            result["details"] = "调查周围环境"
            agent.add_memory(f"调查了{agent.current_room}")
        
        elif action_type == "rest":
            agent.energy = min(100, agent.energy + 10)
            result["details"] = "休息，恢复体力"
        
        return result
    
    def _update_agent_state(self, agent: AgentState, action: Dict, result: Dict):
        if action.get("action_type") in ["move", "investigate"]:
            agent.energy = max(0, agent.energy - 5)
        
        if result["success"]:
            agent.mood = "happy"
        else:
            agent.mood = "frustrated"
        
        agent.action_cooldown = 2
        
        memory_content = f"{action.get('action_type', '行动')}: {result.get('details', '')}"
        agent.add_memory(memory_content)
    
    def _get_room_data(self, room_id: str, context: Dict) -> Optional[Dict]:
        scene_structure = context.get("scene_structure", {})
        rooms = scene_structure.get("rooms", [])
        for room in rooms:
            if room.get("id") == room_id:
                return room
        return None
    
    def _is_position_in_room(self, x: int, y: int, room: Dict) -> bool:
        room_x = room.get("x", 0)
        room_y = room.get("y", 0)
        room_width = room.get("width", 100)
        room_height = room.get("height", 100)
        
        return (room_x <= x <= room_x + room_width and 
                room_y <= y <= room_y + room_height)
    
    def _find_agent_by_name(self, name: str) -> Optional[AgentState]:
        for agent in self.agents.values():
            if agent.name == name:
                return agent
        return None
    
    def get_agent_states(self) -> List[Dict]:
        return [
            {
                "id": agent.id,
                "name": agent.name,
                "position": agent.position.copy(),
                "current_room": agent.current_room,
                "mood": agent.mood,
                "energy": agent.energy,
                "inventory": agent.inventory.copy(),
                "current_action": agent.current_action,
                "memory": agent.memory[-5:], # 返回最近5条记忆
                "relationships": agent.relationships
            }
            for agent in self.agents.values()
        ]
