# scene_generator.py
import re
import random
import json
from typing import Dict, List, Tuple, Optional
from LLM import LLMManager
from story_outline_generator import StoryOutlineGenerator

PLACE_KEYWORDS = ["town", "city", "village", "forest", "beach", "mountain", "station", "mall", "market", "school"]
DEFAULT_NAMES = ["Avery", "Riley", "Jordan", "Taylor", "Morgan", "Casey", "Quinn", "Emery"]

class SceneGenerator:
    def __init__(self):
        self.llm_manager = LLMManager()
        self.outline_generator = StoryOutlineGenerator()
    
    def extract_elements(self, text):
        names = re.findall(r'\b[A-Z][a-z]{1,}\b', text)
        names = [n for n in names if n.lower() not in ["The","And","In","On","At","A","An"]]
        places = [w for w in PLACE_KEYWORDS if w in text.lower()]
        verbs = re.findall(r'\b[a-z]{3,}ing\b|\b[a-z]{3,}ed\b', text.lower())
        return {
            "names": list(dict.fromkeys(names)) or [],
            "places": list(dict.fromkeys(places)) or [],
            "verbs": list(dict.fromkeys(verbs)) or []
        }

    def generate_comprehensive_scene(self, scene_description: str, agent_count: int, use_llm: bool = False, max_steps: int = 100) -> Dict:
        """生成完整的场景，包括大纲和地图"""
        
        if use_llm:
            outline = self.outline_generator.generate_comprehensive_outline(
                scene_description, agent_count, max_steps
            )
            scene = self._generate_scene_with_llm(outline)
            agents = self._generate_agents_with_outline(outline, agent_count, use_llm=True)
            
            return {
                "outline": outline,
                "scene": scene,
                "agents": agents,
                "use_llm": True
            }
        else:
            elements = self.extract_elements(scene_description)
            scene = self._generate_default_scene(elements)
            agents = self._generate_default_agents(elements, agent_count)
            outline = self.outline_generator._generate_default_outline(
                scene_description, agent_count, max_steps
            )
            
            return {
                "outline": outline,
                "scene": scene,
                "agents": agents,
                "use_llm": False
            }
    
    def _generate_scene_with_llm(self, outline: Dict) -> Dict:
        """基于大纲生成场景"""
        scene_structure = outline.get("scene_structure", {})
        
        return {
            "type": scene_structure.get("map_type", "town"),
            "description": f"{outline.get('title', '神秘故事')} - {outline.get('theme', '探索主题')}",
            "structure": scene_structure,
            "generated_by": "LLM"
        }
    
    def _generate_default_scene(self, elements):
        typ = elements["places"][0] if elements["places"] else random.choice(PLACE_KEYWORDS)
        desc_templates = [
            "A quiet {typ} bathed in late afternoon light.",
            "A bustling {typ} filled with whispered rumors.",
            "A foggy {typ} where shadows seem to move on their own.",
            "An ordinary {typ} with secrets beneath its surface."
        ]
        description = random.choice(desc_templates).format(typ=typ)
        
        outline_generator = StoryOutlineGenerator()
        scene_structure = outline_generator._generate_default_scene_structure()
        
        return {
            "type": typ,
            "description": description,
            "structure": scene_structure,
            "generated_by": "default"
        }

    def _generate_agents_with_outline(self, outline: Dict, agent_count: int, use_llm: bool = False) -> List[Dict]:
        """基于大纲生成智能体"""
        agents = []
        character_arcs = outline.get("character_arcs", [])
        scene_structure = outline.get("scene_structure", {})
        rooms = scene_structure.get("rooms", [])
        for i in range(agent_count):
            if i < len(character_arcs):
                arc = character_arcs[i]
                name = arc.get("character", f"Character_{i+1}")
                
                if use_llm:
                    personality, goal = self._generate_character_with_llm(name, arc)
                else:
                    personality = self._random_personality()
                    goal = arc.get("initial_state", "探索未知")
            else:
                name = random.choice(DEFAULT_NAMES) + str(i+1)
                personality = self._random_personality()
                goal = self._random_goal()
            
            # 为智能体分配初始位置
            if rooms:
                initial_room = random.choice(rooms)
                initial_x = initial_room.get("x", 100) + initial_room.get("width", 120) // 2
                initial_y = initial_room.get("y", 100) + initial_room.get("height", 120) // 2
            else:
                initial_x = random.randint(50, 750)
                initial_y = random.randint(50, 450)
            
            agent = {
                "id": i,
                "name": name,
                "personality": personality,
                "goal": goal,
                "energy": random.uniform(0.8, 1.0),
                "color": "#{:06x}".format(random.randint(0x444444, 0xFFFFFF)),
                "llm_enabled": use_llm,
                "character_arc": arc if i < len(character_arcs) else None,
                "x": initial_x,  # 添加坐标
                "y": initial_y,
                "current_room": initial_room.get("id") if rooms else None
            }
            
            agents.append(agent)
        
        return agents
    
    def _generate_character_with_llm(self, name: str, arc: Dict) -> Tuple[List[str], str]:
        """使用LLM生成角色性格和目标"""
        prompt = f"""
        为角色{name}生成性格特点和目标，基于以下角色弧光：
        - 初始状态：{arc.get('initial_state', '')}
        - 最终状态：{arc.get('final_state', '')}
        - 发展节点：{arc.get('development_steps', [])}
        
        请以JSON格式返回:
        {{
            "personality": ["性格1", "性格2"],
            "goal": "目标描述"
        }}
        """
        
        try:
            response = self.llm_manager.llm.chat(prompt)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data.get("personality", self._random_personality()), data.get("goal", self._random_goal())
        except Exception as e:
            print(f"LLM生成角色失败: {e}")
        
        return self._random_personality(), self._random_goal()

    def _random_personality(self):
        traits = ["curious","brave","cautious","greedy","optimistic","skeptical","playful","melancholic"]
        return random.sample(traits, 2)

    def _random_goal(self):
        goals = [
            "find a lost item","make a new friend","solve a mystery",
            "reach the town hall","win an argument","protect someone"
        ]
        return random.choice(goals)

    def _generate_default_agents(self, elements, num):
        names = elements["names"] if elements["names"] else random.sample(DEFAULT_NAMES, num)
        agents = []
        for i in range(num):
            name = names[i] if i < len(names) else random.choice(DEFAULT_NAMES) + str(i+1)
            personality = self._random_personality()
            goal = self._random_goal()
            agents.append({
                "id": i,
                "name": name,
                "personality": personality,
                "goal": goal,
                "energy": random.uniform(0.8, 1.0),
                "color": "#{:06x}".format(random.randint(0x444444, 0xFFFFFF)),
                "llm_enabled": False,
                "character_arc": None
            })
        return agents
