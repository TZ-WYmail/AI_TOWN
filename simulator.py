# simulator.py
import random
import time
from typing import Dict, List, Optional
from agent_state_manager import AgentStateManager
from story_outline_generator import StoryOutlineGenerator

class Simulator:
    # 类变量，存储每个故事的模拟器实例（单例模式）
    _instances = {}
    
    def __init__(self):
        self.agent_manager = AgentStateManager()
        self.outline_generator = StoryOutlineGenerator()
        self.current_step = 0
        self.story_outline = None
        self.event_history = []
        self.story_name = None  # 添加故事名标识
        
    @classmethod
    def get_instance(cls, story_name: str):
        """获取或创建指定故事的模拟器实例"""
        if story_name not in cls._instances:
            cls._instances[story_name] = Simulator()
        return cls._instances[story_name]
    
    def initialize_simulation(self, scene_data: Dict, max_steps: int = 100):
        """初始化模拟"""
        self.story_name = scene_data.get("story_name", "default")
        self.story_outline = scene_data.get("outline", {})
        self.scene = scene_data.get("scene", {})
        self.agents = scene_data.get("agents", [])
        self.max_steps = max_steps
        self.current_step = 0
        self.event_history.clear()
        
        # 确保智能体有位置信息
        self._ensure_agent_positions()
        
        # 初始化智能体状态管理器
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
    
    def simulate_step(self) -> Dict:
        """模拟单步"""
        if self.current_step >= self.max_steps:
            return {"status": "completed", "reason": "达到最大步数"}
        
        agent_ids = list(self.agent_manager.agents.keys())
        if not agent_ids:
            return {"status": "error", "reason": "没有智能体"}
        
        selected_agent_id = agent_ids[self.current_step % len(agent_ids)]
        
        context = {
            "scene_description": self.scene.get("description", ""),
            "scene_structure": self.scene.get("structure", {}),
            "current_step": self.current_step,
            "available_items": self._get_available_items(),
            "other_agents": self.agent_manager.get_agent_states()
        }
        
        agent_update = self.agent_manager.update_single_agent(selected_agent_id, context)
        triggered_event = self._check_story_events(selected_agent_id, agent_update)
        
        # 更新原始智能体数据中的位置
        self._update_agent_data(selected_agent_id, agent_update)
        
        event_record = {
            "step": self.current_step,
            "agent_update": agent_update,
            "triggered_event": triggered_event,
            "timestamp": time.time()
        }
        self.event_history.append(event_record)
        
        self.current_step += 1
        
        return {
            "status": "running",
            "step": self.current_step,
            "agent_update": agent_update,
            "triggered_event": triggered_event,
            "all_agent_states": self.agent_manager.get_agent_states(),
            "scene_data": {
                "agents": self.agents,  # 包含更新后的智能体数据
                "scene_structure": self.scene.get("structure", {})
            }
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
        return {
            "current_step": self.current_step,
            "max_steps": self.max_steps,
            "story_outline": self.story_outline,
            "agent_states": self.agent_manager.get_agent_states(),
            "event_history": self.event_history[-10:],
            "progress_percentage": (self.current_step / self.max_steps) * 100,
            "scene_data": {
                "agents": self.agents,  # 包含最新的智能体数据
                "scene_structure": self.scene.get("structure", {})
            }
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
