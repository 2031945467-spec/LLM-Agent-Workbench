import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

@dataclass
class AppConfig:
    app_env:str="dev"
    debug:bool=True
    llm_provider:str="ollama"
    ollama_model:str="qwen3.5:4b"
    openai_model:str="gpt-4o-mini"
    openai_api_key:Optional[str]=None
    openai_base_url:Optional[str]=None
    temperature:float=0.7
    
    def validate(self)->None:
        allowed_providers=["ollama","openai"]
        if self.llm_provider not in allowed_providers:
            raise ValueError(
                f"不支持的 LLM_PROVIDER: {self.llm_provider}，"
                f"目前只支持: {allowed_providers}"
            )
        if not 0<=self.temperature<=2:
            raise ValueError(
                f"LLM_TEMPERATURE 应该在 0 到 2 之间，当前值是: {self.temperature}"
            )
        if self.llm_provider=="openai" and not self.openai_api_key:
            raise ValueError(
                "当前 LLM_PROVIDER=openai,但是没有配置 OPENAI_API_KEY。"
            )
            
    def safe_dict(self)->dict:
        return{
            "app_env": self.app_env,
            "debug": self.debug,
            "llm_provider": self.llm_provider,
            "ollama_model": self.ollama_model,
            "openai_model": self.openai_model,
            "openai_api_key": self._mask_secret(self.openai_api_key),
            "openai_base_url": self.openai_base_url,
            "temperature": self.temperature,
        }
        
    @staticmethod
    def _mask_secret(secret:Optional[str])->Optional[str]:
        if not secret:
            return None
        if len(secret)<=8:
            return "********"
        return secret[:4]+"*"*(len(secret)-8)+secret[-4:]
    
def str_to_bool(value:Optional[str],default:bool=False)->bool:
    if value is None:
        return default
    value=value.strip().lower()
    return value in ["true","1","yes","y","on"]

def load_app_config()->AppConfig:
    load_dotenv()
    config=AppConfig(
        app_env=os.getenv("APP_ENV", "dev"),
        debug=str_to_bool(os.getenv("DEBUG"), default=True),
        llm_provider=os.getenv("LLM_PROVIDER", "ollama").lower().strip(),
        ollama_model=os.getenv("OLLAMA_MODEL", "qwen3.5:4b"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        openai_base_url=os.getenv("OPENAI_BASE_URL") or None,
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
    )
    config.validate()
    return config

def print_config(config:AppConfig)->None:
    print("\n========== 当前项目配置 ==========")
    safe_config = config.safe_dict()
    for key, value in safe_config.items():
        print(f"{key}: {value}")
        
def demo_use_config(config:AppConfig)->None:
    print("\n========== 配置使用示例 ==========")
    
    if config.llm_provider == "ollama":
        print(f"当前使用本地模型: {config.ollama_model}")
        print("后续会调用 ollama.chat(...)")
        
    elif config.llm_provider == "openai":
        print(f"当前使用云端模型: {config.openai_model}")
        print("后续会调用 OpenAI API")

    print(f"temperature: {config.temperature}")

    if config.debug:
        print("当前处于 debug 模式，会输出更多调试信息。")
    else:
        print("当前关闭 debug 模式。")
        
def main() -> None:
    config = load_app_config()

    print_config(config)
    demo_use_config(config)
    
if __name__ == "__main__":
    main()
