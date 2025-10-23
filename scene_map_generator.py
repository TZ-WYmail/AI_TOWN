# scene_map_generator.py
import random
import math
from typing import Dict, List, Tuple

class SceneMapGenerator:
    def __init__(self):
        self.room_templates = {
            "town": [
                {"name": "广场", "base_color": "#8B7355"},
                {"name": "商店", "base_color": "#CD853F"},
                {"name": "酒馆", "base_color": "#8B4513"},
                {"name": "教堂", "base_color": "#F5DEB3"},
                {"name": "市场", "base_color": "#DEB887"},
                {"name": "铁匠铺", "base_color": "#696969"},
                {"name": "药草店", "base_color": "#228B22"},
                {"name": "图书馆", "base_color": "#4682B4"}
            ],
            "forest": [
                {"name": "林间空地", "base_color": "#228B22"},
                {"name": "小木屋", "base_color": "#8B4513"},
                {"name": "神庙", "base_color": "#DAA520"},
                {"name": "洞穴入口", "base_color": "#2F4F4F"},
                {"name": "瀑布", "base_color": "#4682B4"},
                {"name": "古树", "base_color": "#8B4513"},
                {"name": "蘑菇圈", "base_color": "#FF6347"},
                {"name": "石阵", "base_color": "#708090"}
            ],
            "building": [
                {"name": "大厅", "base_color": "#F5F5DC"},
                {"name": "卧室", "base_color": "#FFE4B5"},
                {"name": "厨房", "base_color": "#FFDEAD"},
                {"name": "书房", "base_color": "#F0E68C"},
                {"name": "地下室", "base_color": "#696969"},
                {"name": "阁楼", "base_color": "#D2691E"},
                {"name": "阳台", "base_color": "#87CEEB"},
                {"name": "储藏室", "base_color": "#A0522D"}
            ],
            "dungeon": [
                {"name": "入口大厅", "base_color": "#2F4F4F"},
                {"name": "守卫室", "base_color": "#696969"},
                {"name": "宝库", "base_color": "#FFD700"},
                {"name": "监狱", "base_color": "#483D8B"},
                {"name": "祭坛", "base_color": "#8B008B"},
                {"name": "密室", "base_color": "#4B0082"},
                {"name": "陷阱房", "base_color": "#8B0000"},
                {"name": "Boss房间", "base_color": "#DC143C"}
            ]
        }
    
    def generate_scene_map(self, scene_data: Dict) -> Dict:
        """根据场景数据生成地图"""
        map_type = scene_data.get("map_type", "town")
        rooms_data = scene_data.get("rooms", [])
        
        if not rooms_data:
            rooms_data = self._generate_default_rooms(map_type)
        
        # 生成地图布局
        map_layout = self._create_map_layout(rooms_data, map_type)
        
        # 添加装饰和细节
        decorated_map = self._add_decorations(map_layout, map_type)
        
        return {
            "scene_id": scene_data.get("id", "scene_1"),
            "scene_name": scene_data.get("name", "未知场景"),
            "scene_description": scene_data.get("description", ""),
            "map_type": map_type,
            "rooms": rooms_data,
            "map_layout": decorated_map,
            "background_color": self._get_background_color(map_type),
            "ambient_effects": self._get_ambient_effects(map_type)
        }
    
    def _generate_default_rooms(self, map_type: str) -> List[Dict]:
        """生成默认房间配置"""
        templates = self.room_templates.get(map_type, self.room_templates["town"])
        rooms = []
        
        # 选择3-5个房间
        selected_templates = random.sample(templates, min(random.randint(3, 5), len(templates)))
        
        for i, template in enumerate(selected_templates):
            room = {
                "id": f"room_{i+1}",
                "name": template["name"],
                "description": f"一个{template['name']}",
                "x": 150 + (i % 3) * 200,
                "y": 150 + (i // 3) * 200,
                "width": 120,
                "height": 120,
                "color": template["base_color"],
                "connections": []
            }
            rooms.append(room)
        
        # 创建房间连接
        for i in range(len(rooms) - 1):
            rooms[i]["connections"].append(rooms[i + 1]["id"])
            rooms[i + 1]["connections"].append(rooms[i]["id"])
        
        return rooms
    
    def _create_map_layout(self, rooms_data: List[Dict], map_type: str) -> Dict:
        """创建地图布局"""
        layout = {
            "width": 800,
            "height": 600,
            "rooms": [],
            "paths": [],
            "landmarks": []
        }
        
        # 处理房间数据
        for room in rooms_data:
            room_layout = {
                "id": room["id"],
                "name": room["name"],
                "x": room.get("x", 100),
                "y": room.get("y", 100),
                "width": room.get("width", 120),
                "height": room.get("height", 120),
                "color": room.get("color", "#8B7355"),
                "connections": room.get("connections", [])
            }
            layout["rooms"].append(room_layout)
        
        # 生成路径
        for room in layout["rooms"]:
            for connection_id in room["connections"]:
                connected_room = next((r for r in layout["rooms"] if r["id"] == connection_id), None)
                if connected_room:
                    path = {
                        "from": room["id"],
                        "to": connection_id,
                        "x1": room["x"] + room["width"] // 2,
                        "y1": room["y"] + room["height"] // 2,
                        "x2": connected_room["x"] + connected_room["width"] // 2,
                        "y2": connected_room["y"] + connected_room["height"] // 2
                    }
                    layout["paths"].append(path)
        
        return layout
    
    def _add_decorations(self, layout: Dict, map_type: str) -> Dict:
        """添加装饰元素"""
        decorations = {
            "trees": [],
            "rocks": [],
            "water": [],
            "special_objects": []
        }
        
        if map_type == "town":
            # 添加树木
            for _ in range(random.randint(5, 10)):
                decorations["trees"].append({
                    "x": random.randint(50, 750),
                    "y": random.randint(50, 550),
                    "size": random.randint(20, 40)
                })
            
            # 添加喷泉
            decorations["water"].append({
                "type": "fountain",
                "x": 400,
                "y": 300,
                "radius": 30
            })
        
        elif map_type == "forest":
            # 添加更多树木
            for _ in range(random.randint(15, 25)):
                decorations["trees"].append({
                    "x": random.randint(50, 750),
                    "y": random.randint(50, 550),
                    "size": random.randint(30, 60)
                })
            
            # 添加岩石
            for _ in range(random.randint(3, 8)):
                decorations["rocks"].append({
                    "x": random.randint(50, 750),
                    "y": random.randint(50, 550),
                    "size": random.randint(15, 30)
                })
        
        elif map_type == "dungeon":
            # 添加火把
            for room in layout["rooms"]:
                decorations["special_objects"].append({
                    "type": "torch",
                    "x": room["x"] + 10,
                    "y": room["y"] + 10,
                    "light_radius": 50
                })
        
        layout["decorations"] = decorations
        return layout
    
    
    def _get_background_color(self, map_type: str) -> str:
        """获取背景颜色"""
        backgrounds = {
            "town": "#87CEEB",
            "forest": "#228B22",
            "building": "#F5DEB3",
            "dungeon": "#2F4F4F"
        }
        return backgrounds.get(map_type, "#87CEEB")
    
    def _get_ambient_effects(self, map_type: str) -> List[str]:
        """获取环境效果"""
        effects = {
            "town": ["birds_chirping", "wind_breeze"],
            "forest": ["leaves_rustling", "owl_hoots"],
            "building": ["clock_ticking", "fire_crackling"],
            "dungeon": ["water_dripping", "echoes"]
        }
        return effects.get(map_type, ["wind_breeze"])
