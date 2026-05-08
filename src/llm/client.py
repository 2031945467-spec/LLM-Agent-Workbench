from typing import Dict,List,Optional
from src.config.settings import AppConfig

Message=Dict[str,str]

class LLMClient:
    def __init__(self,config:AppConfig):
        self.config=config
        self.provider=config.llm_provider.lower().strip()
        if self.provider not in ["ollama","openai"]:
            raise ValueError(
                f"不支持的 provider: {self.provider}"
            )
    def chat(
        self,
        user_message:str,
        system_prompt:str="你是一个认真、清晰、善于解释技术概念的 AI 助手。",
        history:Optional[List[Message]]=None,
    )->str:
        messages=self._build_messages(
            user_message=user_message,
            system_prompt=system_prompt,
            history=history,
        )
        if self.provider=="ollama":
            return self._chat_with_ollama(messages)
        if self.provider=="openai":
            return self._chat_with_openai(messages)
        raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _build_messages(
        self,
        user_message:str,
        system_prompt:str,
        history:Optional[List[Message]],
    )->List[Message]:
        messages:List[Message]=[]
        messages.append({
            "role":"system",
            "content":system_prompt,
        })
        if history:
            messages.extend(history)
        messages.append({
            "role":"user",
            "content":user_message,
        })
        return messages
    
    
    def _chat_with_ollama(self,messages:List[Message])->str:
        try:
            import ollama
            response=ollama.chat(
                model=self.config.ollama_model,
                messages=messages,
                options={"temperature":self.config.temperature},
            )
            if isinstance(response,dict):
                return response["message"]["content"]
            return response.message.content
        except ImportError:
            return "错误：你还没有安装 ollama 包，请执行 pip install ollama"
        except Exception as e:
            return f"Ollama 调用失败：{e}"
    
    
    
    def _chat_with_openai(self,messages:List[Message])->str:
        if not self.config.openai_api_key:
            return "错误：没有检测到 OPENAI_API_KEY,请先在 .env 中配置。"
        try:
            from openai import OpenAI
            if self.config.openai_base_url:
                client=OpenAI(
                    api_key=self.config.openai_api_key,
                    base_url=self.config.openai_base_url
                )
            else:
                client=OpenAI(
                    api_key=self.config.openai_api_key
                )
            response=client.chat.completions.create(
                model=self.config.openai_model,
                messages=messages,
                temperature=self.config.temperature
            )
            return response.choices[0].message.content or ""
        except ImportError:
            return "错误：你还没有安装 openai 包，请执行 pip install openai"

        except Exception as e:
            return f"OpenAI 调用失败：{e}"