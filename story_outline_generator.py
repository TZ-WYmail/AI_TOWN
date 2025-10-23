# story_outline_generator.py
import json
import re
from typing import Dict, List
from LLM import LLMManager

class StoryOutlineGenerator:
    def __init__(self):
        self.llm_manager = LLMManager()
    
    def generate_comprehensive_outline(self, scene_description: str, agent_count: int, max_steps: int = 100) -> Dict:
        """生成完整的故事大纲，包括100步内的事件"""
        prompt = f"""
        请为以下场景生成一个详细的故事大纲，包含100步内的所有重要事件：
        
        场景描述：{scene_description}
        角色数量：{agent_count}
        最大步数：{max_steps}
        
        请以JSON格式返回，包含以下字段：
        {{
            "title": "故事标题",
            "theme": "故事主题",
            "main_conflict": "主要冲突",
            "key_events": [
                {{
                    "step": 1,
                    "event_type": "encounter/dialogue/discovery/conflict/resolution",
                    "description": "事件描述",
                    "participants": ["角色1", "角色2"],
                    "location": "具体位置",
                    "impact": "对故事的影响",
                    "next_step_trigger": "触发下一步的条件"
                }}
            ],
            "scene_structure": {{
                "map_type": "地图类型（town/forest/building/dungeon）",
                "rooms": [
                    {{
                        "id": "room_1",
                        "name": "房间名称",
                        "description": "房间详细描述",
                        "width": 200,
                        "height": 150,
                        "x": 100,
                        "y": 100,
                        "connections": ["room_2", "room_3"],
                        "special_features": ["特殊特征1", "特殊特征2"],
                        "initial_occupants": ["角色1"],
                        "key_items": ["重要物品"]
                    }}
                ],
                "room_relationships": [
                    {{
                        "from": "room_1",
                        "to": "room_2",
                        "connection_type": "door/secret_passage/stairs",
                        "access_requirement": "访问条件"
                    }}
                ]
            }},
            "character_arcs": [
                {{
                    "character": "角色名",
                    "initial_state": "初始状态",
                    "development_steps": [5, 15, 30, 60, 90],
                    "final_state": "最终状态"
                }}
            ],
            "plot_milestones": [
                {{
                    "step": 10,
                    "milestone": "重要情节节点",
                    "consequences": "后果"
                }}
            ]
        }}
        
        注意：
        1. 事件应该有逻辑性和连贯性
        2. 每个事件都应该推动故事发展
        3. 角色发展应该有明确轨迹
        4. 地图设计应该支持故事发展
        5. 考虑角色之间的互动和关系变化
        """
        
        try:
            response = self.llm_manager.llm.chat(prompt)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                outline = json.loads(json_match.group())
                return self._validate_and_fix_outline(outline, scene_description, agent_count, max_steps)
        except Exception as e:
            print(f"LLM生成大纲失败: {e}")
        
        return self._generate_default_outline(scene_description, agent_count, max_steps)
    
    def _validate_and_fix_outline(self, outline: Dict, scene_description: str, agent_count: int, max_steps: int) -> Dict:
        """验证并修复大纲"""
        # 确保所有必要字段存在
        if "key_events" not in outline:
            outline["key_events"] = []
        
        if "scene_structure" not in outline:
            outline["scene_structure"] = self._generate_default_scene_structure()
        
        # 限制事件数量
        if len(outline["key_events"]) > max_steps:
            outline["key_events"] = outline["key_events"][:max_steps]
        
        # 确保房间连接正确
        rooms = outline["scene_structure"]["rooms"]
        for room in rooms:
            if "connections" not in room:
                room["connections"] = []
            # 验证连接的房间是否存在
            valid_connections = []
            for conn in room["connections"]:
                if any(r["id"] == conn for r in rooms):
                    valid_connections.append(conn)
            room["connections"] = valid_connections
        
        return outline
    
    def _generate_default_outline(self, scene_description: str, agent_count: int, max_steps: int) -> Dict:
        """生成默认大纲"""
        return {
            "title": "神秘小镇冒险",
            "theme": "探索与发现",
            "main_conflict": "寻找失落的神器",
            "key_events": [
                {
                    "step": 1,
                    "event_type": "encounter",
                    "description": "角色们在小镇广场相遇",
                    "participants": ["所有角色"],
                    "location": "广场",
                    "impact": "故事开始",
                    "next_step_trigger": "角色介绍完成"
                }
            ],
            "scene_structure": self._generate_default_scene_structure(),
            "character_arcs": [],
            "plot_milestones": []
        }
    
    def _generate_default_scene_structure(self) -> Dict:
        """生成默认场景结构"""
        return {
            "map_type": "town",
            "rooms": [
                {
                    "id": "square",
                    "name": "小镇广场",
                    "description": "小镇的中心广场，有一个古老的喷泉",
                    "width": 300,
                    "height": 200,
                    "x": 250,
                    "y": 200,
                    "connections": ["shop", "tavern", "station"],
                    "special_features": ["喷泉", "公告板"],
                    "initial_occupants": [],
                    "key_items": ["地图碎片"]
                },
                {
                    "id": "shop",
                    "name": "神秘商店",
                    "description": "出售各种神秘物品的商店",
                    "width": 150,
                    "height": 120,
                    "x": 100,
                    "y": 100,
                    "connections": ["square"],
                    "special_features": ["魔法物品"],
                    "initial_occupants": [],
                    "key_items": ["神秘药水"]
                },
                {
                    "id": "tavern",
                    "name": "酒馆",
                    "description": "旅行者们聚集的地方",
                    "width": 180,
                    "height": 140,
                    "x": 600,
                    "y": 150,
                    "connections": ["square"],
                    "special_features": ["酒桶", "壁炉"],
                    "initial_occupants": [],
                    "key_items": ["传闻"]
                },
                {
                    "id": "station",
                    "name": "火车站",
                    "description": "废弃的火车站，据说有秘密通道",
                    "width": 200,
                    "height": 160,
                    "x": 300,
                    "y": 450,
                    "connections": ["square"],
                    "special_features": ["秘密通道"],
                    "initial_occupants": [],
                    "key_items": ["车票"]
                }
            ],
            "room_relationships": []
        }
