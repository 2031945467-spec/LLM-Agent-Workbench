import os
from dataclasses import dataclass
from typing import List,Optional,Dict
from dotenv import load_dotenv

Message =Dict[str,str]

@dataclass
class LLMConfig:
    provider:str="ollama"
    ollama_model:str="qwen3.5:4b"
    openai_model:str="gpt-4o-mini"
    openai_api_key:Optional[str]=None
    openai_base_url:Optional[str]=None
    temperature:float=0.7

class LLMClient:
    def __init__(self,config:LLMConfig):
        self.config=config
        self.provider=config.provider.lower().strip()
        if self.provider not in ["ollama","openai"]:
            raise ValueError(f"Unsupported provider:{self.provider}")
        
    def chat(
        self,
        user_message:str,
        system_prompt:str="你是一个认真,清晰,善于解释技术概念的AI助手。",
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
        
        raise ValueError(f"Unsupported provider:{self.provider}")
    
    def _build_messages(
            self,
            user_message:str,
            system_prompt:str,
            history:Optional[List[Message]]=None,
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
            return "Ollama SDK is not installed. Please install it with 'pip install ollama'."
        except Exception as e:
            return f"Error while chatting with Ollama: {e}"
        
    def _chat_with_openai(self,messages:List[Message])->str:
        if not self.config.openai_api_key:
            return "OpenAI API key is not configured. Please set it in the .env file."
            
        try:
            from openai import OpenAI
            if self.config.openai_base_url:
                client=OpenAI(
                    api_key=self.config.openai_api_key,
                    base_url=self.config.openai_base_url,
                )
            else:
                client=OpenAI(api_key=self.config.openai_api_key)

            response=client.chat.completions.create(
                model=self.config.openai_model,
                messages=messages,
                temperature=self.config.temperature,
            )
            return response.choices[0].message.content
        except ImportError:
            return "OpenAI SDK is not installed. Please install it with 'pip install openai'."
        except Exception as e:
            return f"Error while chatting with OpenAI: {e}"
        
def load_config()->LLMConfig:
    load_dotenv()
    return LLMConfig(
        provider=os.getenv("LLM_PROVIDER","ollama"),
        ollama_model=os.getenv("OLLAMA_MODEL","qwen3.5:4b"),
        openai_model=os.getenv("OPENAI_MODEL","gpt-4o-mini"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_base_url=os.getenv("OPENAI_BASE_URL"),
        temperature=float(os.getenv("LLM_TEMPERATURE",0.7)),
    )

def demo_single_chat(client:LLMClient)->None:
    print("\n=== Single Chat Demo ===")
    question="用三句话解释什么是大模型Agent"
    answer=client.chat(question)
    print(f"user:{question}")
    print(f"ai:{answer}")

def demo_multi_turn_chat(client:LLMClient)->None:
    print("\n=== Multi-turn Chat Demo ===")
    history:List[Message]=[]

    user_1="我现在在学习大模型 Agent,先用一句话解释 Agent。"
    assistant_1=client.chat(user_1,history=history)
    history.append({"role":"user","content":user_1})
    history.append({"role":"assistant","content":assistant_1})

    user_2="那它和普通聊天机器人有什么区别"
    assistant_2=client.chat(user_2,history=history)

    print(f"user:{user_1}")
    print(f"ai:{assistant_1}")

    print(f"\nuser:{user_2}")
    print(f"ai:{assistant_2}")

def demo_interactive_chat(client:LLMClient)->None:
    print("\n=== Interactive Chat Demo ===")
    print("Type 'q' to quit.Type 'clear' to clear history.")
    history:List[Message]=[]

    while True:
        user_input=input("\nYou:").strip()
        if user_input.lower()=="q":
            print("Exiting chat")
            break
        if user_input.lower()=="clear":
            history.clear()
            print("Chat history cleared")
            continue

        answer=client.chat(user_input,history=history)
        print(f"AI:{answer}")

        history.append({"role":"user","content":user_input})
        history.append({"role":"assistant","content":answer})

def main()->None:
    config=load_config()
    print("当前模型配置:")
    print(f"provider:{config.provider}")
    print(f"ollama_model:{config.ollama_model}")
    print(f"openai_model:{config.openai_model}")
    print(f"temperature:{config.temperature}")

    client=LLMClient(config)
    demo_single_chat(client)
    demo_multi_turn_chat(client)
    demo_interactive_chat(client)

if __name__=="__main__":
    main()
