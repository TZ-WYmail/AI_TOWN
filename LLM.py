# LLM.py
from google import genai
from openai import OpenAI
import json
import re
from typing import Dict, List, Optional, Tuple
from llm_config import load_llm_config, get_provider_config

class LLMCHAT:
    def __init__(
            self,
            model: str = "kimi-k2-turbo-preview",
            system: str | None = None,
            temperature: float = 0.7,
            stream: bool = True,
    ):
        # 从配置文件加载设置
        self.config = load_llm_config()
        self.model = model
        self.temperature = temperature or self.config.get("temperature", 0.7)
        self.system = system or (
            "你是 Kimi，由 Moonshot AI 提供的人工智能助手，"
            "你更擅长中文和英文的对话。你会为用户提供安全、有帮助、准确的回答。"
            "同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。"
            "Moonshot AI 为专有名词，不可翻译成其他语言。"
        )
        self.quiet = True
        self.default_stream = stream
        
        # 根据模型确定提供商
        self.provider = self._get_provider_by_model(model)
        
        # 初始化客户端
        self._init_client()

    def _get_provider_by_model(self, model: str) -> str:
        """根据模型ID确定提供商"""
        models = self.config.get("models", {})
        for provider, model_list in models.items():
            for m in model_list:
                if m.get("id") == model:
                    return provider
        return "kimi"  # 默认提供商

    def _init_client(self):
        """初始化客户端"""
        provider_config = get_provider_config(self.provider)
        api_key = provider_config.get("api_key", "")
        base_url = provider_config.get("base_url", "")
        
        if self.provider == "kimi":
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        elif self.provider == "openai":
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        elif self.provider == "gemini":
            # Gemini使用不同的客户端
            self.client = None

    def change_model(self, model: str):
        """切换模型"""
        self.model = model
        new_provider = self._get_provider_by_model(model)
        
        # 如果提供商改变，重新初始化客户端
        if new_provider != self.provider:
            self.provider = new_provider
            self._init_client()

    def chat(self, user: str, *, stream: bool | None = None, **kwargs) -> str:
        if stream is None:
            stream = self.default_stream

        buffer: list[str] = []

        if self.provider in ["kimi", "openai"]:
            messages = (
                [{"role": "system", "content": self.system}, {"role": "user", "content": user}]
                if self.provider == "kimi"
                else [{"role": "user", "content": user}]
            )

            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.config.get("max_tokens", 60000),
                timeout=120,
                temperature=kwargs.pop("temperature", self.temperature),
                stream=True,
                **kwargs
            )
            for chunk in resp:
                delta = chunk.choices[0].delta.content
                if delta:
                    buffer.append(delta)
                    if not self.quiet:
                        print(delta, end="", flush=True)
            if not self.quiet:
                print()
            return "".join(buffer)

        elif self.provider == "gemini":
            provider_config = get_provider_config("gemini")
            client = genai.Client(api_key=provider_config.get("api_key", ""))
            response = client.models.generate_content(model=self.model, contents=user)
            if not self.quiet:
                print(response.text, end="", flush=True)
            return response.text

        raise ValueError(f"不支持的模型 {self.model}")

class LLMManager:
    def __init__(self):
        self.config = load_llm_config()
        self.llm = LLMCHAT(model=self.config.get("selected_model", "kimi-k2-turbo-preview"))
        self.current_model = self.config.get("selected_model", "kimi-k2-turbo-preview")
        
    def change_model(self, model: str):
        """切换LLM模型"""
        self.current_model = model
        self.llm.change_model(model)
        # 更新配置
        self.config["selected_model"] = model
        from llm_config import save_llm_config
        save_llm_config(self.config)
    
    def update_config(self, new_config: Dict):
        """更新配置"""
        self.config.update(new_config)
        from llm_config import save_llm_config
        save_llm_config(self.config)
        # 重新初始化LLM
        self.llm = LLMCHAT(model=self.config.get("selected_model", "kimi-k2-turbo-preview"))
    
    def generate_story_outline(self, scene_description: str, agent_count: int) -> Dict:
        """生成故事大纲"""
        prompt = f"""
        请为以下场景生成一个详细的故事大纲，包含多个场景和情节发展：
        
        场景描述：{scene_description}
        角色数量：{agent_count}
        
        请以JSON格式返回，包含以下字段：
        {{
            "title": "故事标题",
            "scenes": [
                {{
                    "id": "scene_1",
                    "name": "场景名称",
                    "description": "场景描述",
                    "map_type": "地图类型（如：town, forest, building, dungeon等）",
                    "rooms": [
                        {{
                            "id": "room_1",
                            "name": "房间名称",
                            "description": "房间描述",
                            "x": 100,
                            "y": 100,
                            "connections": ["room_2"]
                        }}
                    ],
                    "triggers": ["触发条件，如：找到某个物品、对话完成等"]
                }}
            ],
            "plot_progression": [
                {{
                    "scene_id": "scene_1",
                    "events": ["该场景的关键事件"],
                    "transition_condition": "切换到下一个场景的条件"
                }}
            ]
        }}
        """
        
        try:
            response = self.llm.chat(prompt)
            # 提取JSON部分
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"生成故事大纲失败: {e}")
        
        # 返回默认大纲
        return self._generate_default_outline(scene_description, agent_count)
    
    def _generate_default_outline(self, scene_description: str, agent_count: int) -> Dict:
        """生成默认故事大纲"""
        return {
            "title": "神秘小镇冒险",
            "scenes": [
                {
                    "id": "scene_1",
                    "name": "小镇广场",
                    "description": scene_description,
                    "map_type": "town",
                    "rooms": [
                        {"id": "square", "name": "广场", "description": "小镇的中心广场", "x": 400, "y": 300, "connections": ["station", "shop"]},
                        {"id": "station", "name": "火车站", "description": "古老的火车站", "x": 200, "y": 200, "connections": ["square"]},
                        {"id": "shop", "name": "商店", "description": "神秘的商店", "x": 600, "y": 200, "connections": ["square"]}
                    ],
                    "triggers": ["探索所有房间"]
                }
            ],
            "plot_progression": [
                {
                    "scene_id": "scene_1",
                    "events": ["角色相遇", "发现线索"],
                    "transition_condition": "探索完成"
                }
            ]
        }
    
    def generate_agent_action(self, agent: Dict, context: Dict, other_agents: List[Dict]) -> Dict:
        """生成智能体动作"""
        prompt = f"""
        你是角色{agent['name']}，性格特点：{', '.join(agent['personality'])}，目标：{agent['goal']}。
        
        当前情况：
        - 所在位置：{context.get('current_room', '未知')}
        - 场景描述：{context.get('scene_description', '未知')}
        - 周围角色：{', '.join([a['name'] for a in other_agents if a['id'] != agent['id']])}
        - 当前状态：{context.get('current_situation', '探索中')}
        
        请根据你的性格和目标，决定下一步行动。以JSON格式返回：
        {{
            "action": "行动类型（move/talk/interact/think）",
            "target": "目标对象（角色名或物品名）",
            "dialogue": "要说的话（如果action是talk）",
            "destination": {"x": 100, "y": 100},
            "emotion": "当前情绪",
            "reasoning": "行动原因"
        }}
        """
        
        try:
            response = self.llm.chat(prompt)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"生成智能体动作失败: {e}")
        
        # 返回默认动作
        return {
            "action": "move",
            "target": None,
            "dialogue": f"{agent['name']}: 让我继续探索。",
            "destination": {"x": agent.get("x", 400) + 50, "y": agent.get("y", 300) + 50},
            "emotion": "neutral",
            "reasoning": "继续探索"
        }
    
    def generate_scene_transition(self, current_scene: Dict, next_scene: Dict, story_context: str) -> str:
        """生成场景切换描述"""
        prompt = f"""
        当前场景：{current_scene['name']} - {current_scene['description']}
        下一个场景：{next_scene['name']} - {next_scene['description']}
        故事背景：{story_context}
        
        请生成一个场景切换的过渡描述，约50-100字，描述角色如何从一个场景移动到另一个场景。
        """
        
        try:
            response = self.llm.chat(prompt)
            return response.strip()
        except Exception as e:
            print(f"生成场景切换描述失败: {e}")
            return f"角色们离开了{current_scene['name']}，前往{next_scene['name']}..."
