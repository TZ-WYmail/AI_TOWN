# simulator.py
import random
import time
from typing import Dict, List, Optional
from agent_state_manager import AgentStateManager
from story_director import StoryDirector
from story_outline_generator import StoryOutlineGenerator

class Simulator:
    _instances = {}
    
    def __init__(self):
        self.agent_manager = AgentStateManager()
        self.outline_generator = StoryOutlineGenerator()
        self.story_director = StoryDirector() # 实例化导演
        self.current_step = 0
        self.story_outline = None
        self.event_history = []
        self.story_name = None
        self.current_narrative_summary = "等待导演就绪..." # 新增：存储当前剧情摘要
        
    @classmethod
    def get_instance(cls, story_name: str):
        if story_name not in cls._instances:
            cls._instances[story_name] = Simulator()
        return cls._instances[story_name]
    
    def initialize_simulation(self, scene_data: Dict, max_steps: int = 100):
        self.story_name = scene_data.get("story_name", "default")
        self.story_outline = scene_data.get("outline", {})
        self.scene = scene_data.get("scene", {})
        self.agents = scene_data.get("agents", [])
        self.max_steps = max_steps
        self.current_step = 0
        self.event_history.clear()
        self.current_narrative_summary = "等待导演就绪..."
        
        self._ensure_agent_positions()
        self.agent_manager.initialize_agents(self.agents, self.scene.get("structure", {}))
        
        return {
            "status": "initialized",
            "outline": self.story_outline,
            "agent_states": self.agent_manager.get_agent_states(),
            "scene_structure": self.scene.get("structure", {})
        }
    
    def _ensure_agent_positions(self):
        """确保智能体有正确的位置信息"""
        scene_structure = self.scene.get("structure", {})
        rooms = scene_structure.get("rooms", [])
        
        for agent in self.agents:
            # 如果智能体没有位置信息，则分配一个
            if "x" not in agent or "y" not in agent:
                if rooms:
                    # 随机选择一个房间
                    initial_room = random.choice(rooms)
                    agent["x"] = initial_room.get("x", 100) + initial_room.get("width", 120) // 2
                    agent["y"] = initial_room.get("y", 100) + initial_room.get("height", 120) // 2
                    agent["current_room"] = initial_room.get("id")
                else:
                    # 如果没有房间，随机分配位置
                    agent["x"] = random.randint(50, 750)
                    agent["y"] = random.randint(50, 450)
                    agent["current_room"] = None
            
            # 确保智能体有必要的属性
            agent.setdefault("energy", 100)
            agent.setdefault("mood", "neutral")
            agent.setdefault("inventory", [])
    
   # --- 核心修改：模拟单步的逻辑 ---
    def simulate_step(self) -> Dict:
        """模拟单步，现在由导演编排"""
        if self.current_step >= self.max_steps:
            return {"status": "completed", "reason": "达到最大步数"}

        # 1. 检查当前动作计划是否已执行完毕
        if self.agent_manager.is_plan_finished():
            # 2. 如果完毕，让导演生成新的计划
            context = self._prepare_director_context()
            # --- 修改：解构返回值，获取摘要和计划 ---
            narrative, action_plan = self.story_director.generate_step_plan(context)
            
            # 存储摘要，以便在计划的每一步都能使用
            self.current_narrative_summary = narrative
            self.agent_manager.set_action_plan(action_plan)
            
            if not action_plan:
                return {"status": "error", "reason": "导演未能生成有效的动作计划"}

        # 3. 执行计划中的下一个动作
        agent_update = self.agent_manager.update_agents_with_plan(self._prepare_director_context())
        
        # 4. 更新原始智能体数据
        if agent_update.get("status") == "executed":
            self._update_agent_data(agent_update["agent_id"], agent_update)

        # 5. 检查故事事件（如果计划执行完毕）
        triggered_event = None
        if self.agent_manager.is_plan_finished():
            triggered_event = self._check_story_events(agent_update.get("agent_id"), agent_update)

        event_record = {
            "step": self.current_step,
            "agent_update": agent_update,
            "triggered_event": triggered_event,
            "timestamp": time.time()
        }
        self.event_history.append(event_record)

        # 只有当一个完整计划执行完毕后，步数才增加
        if self.agent_manager.is_plan_finished():
            self.current_step += 1
        
        return {
            "status": "running",
            "step": self.current_step,
            "agent_update": agent_update,
            "triggered_event": triggered_event,
            "all_agent_states": self.agent_manager.get_agent_states(),
            "scene_data": {
                "agents": self.agents,
                "scene_structure": self.scene.get("structure", {})
            },
            "plan_progress": agent_update.get("plan_progress", "N/A"),
            "narrative_summary": self.current_narrative_summary # --- 新增：返回当前剧情摘要 ---
        }

    def _prepare_director_context(self) -> Dict:
        """为导演准备所需的全局上下文"""
        return {
            "scene_description": self.scene.get("description", ""),
            "scene_structure": self.scene.get("structure", {}),
            "current_step": self.current_step,
            "other_agents": self.agent_manager.get_agent_states(), # 提供所有agent的详细状态
            "story_outline": self.story_outline
        }
    
    def _update_agent_data(self, agent_id: int, agent_update: Dict):
        """更新原始智能体数据中的位置和状态"""
        if agent_id < len(self.agents):
            agent = self.agents[agent_id]
            
            # 更新位置
            if "position" in agent_update:
                agent["x"] = agent_update["position"]["x"]
                agent["y"] = agent_update["position"]["y"]
            
            # 更新房间
            if "current_room" in agent_update:
                agent["current_room"] = agent_update["current_room"]
            
            # 更新其他状态
            if "mood" in agent_update:
                agent["mood"] = agent_update["mood"]
            if "energy" in agent_update:
                agent["energy"] = agent_update["energy"]
            if "inventory" in agent_update:
                agent["inventory"] = agent_update["inventory"]
    
    def _check_story_events(self, agent_id: int, agent_update: Dict) -> Optional[Dict]:
        """检查是否触发了故事事件"""
        if not self.story_outline:
            return None
        
        key_events = self.story_outline.get("key_events", [])
        
        for event in key_events:
            if event.get("step") == self.current_step:
                trigger_condition = event.get("next_step_trigger", "")
                if self._evaluate_trigger_condition(trigger_condition, agent_update):
                    return {
                        "event": event,
                        "triggered": True,
                        "impact": event.get("impact", "")
                    }
        
        return None
    
    def _evaluate_trigger_condition(self, condition: str, agent_update: Dict) -> bool:
        """评估触发条件"""
        if not condition:
            return True
        
        # 简单的条件评估逻辑
        if "move" in condition.lower():
            return agent_update.get("action", {}).get("action_type") == "move"
        elif "talk" in condition.lower():
            return agent_update.get("action", {}).get("action_type") == "talk"
        elif "interact" in condition.lower():
            return agent_update.get("action", {}).get("action_type") == "interact"
        
        return True
    
    def _get_available_items(self) -> List[str]:
        """获取可用物品列表"""
        items = []
        scene_structure = self.scene.get("structure", {})
        rooms = scene_structure.get("rooms", [])
        
        for room in rooms:
            room_items = room.get("key_items", [])
            items.extend(room_items)
        
        return items
    
    def get_current_state(self) -> Dict:
        """获取当前模拟状态"""
        try:
            return {
                "current_step": getattr(self, 'current_step', 0),
                "max_steps": getattr(self, 'max_steps', 100),
                "story_outline": getattr(self, 'story_outline', {}),
                "agent_states": self.agent_manager.get_agent_states() if hasattr(self, 'agent_manager') else [],
                "event_history": getattr(self, 'event_history', [])[-10:],
                "progress_percentage": (getattr(self, 'current_step', 0) / getattr(self, 'max_steps', 100)) * 100,
                "scene_data": {
                    "agents": getattr(self, 'agents', []),
                    "scene_structure": getattr(self, 'scene', {}).get("structure", {})
                }
            }
        except Exception as e:
            print(f"获取当前状态失败: {e}")
            return {
                "error": str(e),
                "current_step": 0,
                "max_steps": 100,
                "agent_states": [],
                "scene_data": {"agents": [], "scene_structure": {}}
            }

    def get_map_data(self) -> Dict:
        """获取地图数据用于渲染"""
        return {
            "rooms": self.scene.get("structure", {}).get("rooms", []),
            "agent_positions": [
                {
                    "id": agent["id"],
                    "name": agent["name"],
                    "x": agent["x"],
                    "y": agent["y"],
                    "current_room": agent.get("current_room"),
                    "color": agent.get("color", "#00ffff")
                }
                for agent in self.agents
            ],
            "paths": self._generate_room_paths()
        }
    
    def _generate_room_paths(self) -> List[Dict]:
        """生成房间之间的路径"""
        paths = []
        scene_structure = self.scene.get("structure", {})
        room_relationships = scene_structure.get("room_relationships", [])
        rooms = scene_structure.get("rooms", [])
        
        for relationship in room_relationships:
            from_room = next((r for r in rooms if r.get("id") == relationship.get("from")), None)
            to_room = next((r for r in rooms if r.get("id") == relationship.get("to")), None)
            
            if from_room and to_room:
                paths.append({
                    "from": relationship["from"],
                    "to": relationship["to"],
                    "connection_type": relationship.get("connection_type", "door"),
                    "from_pos": {
                        "x": from_room["x"] + from_room["width"] // 2,
                        "y": from_room["y"] + from_room["height"] // 2
                    },
                    "to_pos": {
                        "x": to_room["x"] + to_room["width"] // 2,
                        "y": to_room["y"] + to_room["height"] // 2
                    }
                })
        
        # 如果没有显式的房间关系，使用连接关系
        if not paths and rooms:
            for room in rooms:
                for connection_id in room.get("connections", []):
                    connected_room = next((r for r in rooms if r.get("id") == connection_id), None)
                    if connected_room:
                        paths.append({
                            "from": room["id"],
                            "to": connection_id,
                            "connection_type": "door",
                            "from_pos": {
                                "x": room["x"] + room["width"] // 2,
                                "y": room["y"] + room["height"] // 2
                            },
                            "to_pos": {
                                "x": connected_room["x"] + connected_room["width"] // 2,
                                "y": connected_room["y"] + connected_room["height"] // 2
                            }
                        })
        
        return paths
    
    def run_full_simulation(self, scene_data: Dict, max_steps: int = 100) -> List[Dict]:
        """运行完整模拟"""
        self.initialize_simulation(scene_data, max_steps)
        
        timeline = []
        while self.current_step < self.max_steps:
            step_result = self.simulate_step()
            timeline.append(step_result)
            
            if step_result.get("status") == "completed":
                break
        
        return timeline

# 保持向后兼容的函数
def run_simulation(scene, agents, steps=12):
    """向后兼容的函数"""
    simulator = Simulator()
    scene_data = {
        "scene": scene,
        "agents": agents,
        "story_name": "legacy_simulation"
    }
    return simulator.run_full_simulation(scene_data, steps)
