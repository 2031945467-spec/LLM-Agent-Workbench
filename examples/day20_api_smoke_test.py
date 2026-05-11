import os
import requests

BASE_URL=os.getenv("API_BASE_URL","http://127.0.0.1:8000")
SESSION_ID = "day20_test"

def print_title(title:str)->None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    
def test_health()->None:
    print_title("1. 测试 /health")
    url=f"{BASE_URL}/health"
    response=requests.get(url,timeout=30)
    print("status_code:",response.status_code)
    print("response:",response.json())
    
    response.raise_for_status()
    
def test_chat(message:str)->None:
    print_title("2. 测试 /chat")
    url=f"{BASE_URL}/chat"
    payload={
        "message":message,
        "session_id":SESSION_ID,
        "max_history":6,
    }
    response=requests.post(url,json=payload,timeout=120)
    
    print("status_code:",response.status_code)
    data=response.json()
    print("answer:",data.get("answer"))
    print("history_count:",data.get("history_count"))
    print("summary:",data.get("summary"))
    
    response.raise_for_status()
    
def test_history()->None:
    print_title("3. 测试 /sessions/{session_id}/history")
    
    url=f"{BASE_URL}/sessions/{SESSION_ID}/history"
    response=requests.get(url,params={"limit":10},timeout=30)
    print("status_code:",response.status_code)
    data=response.json()
    print("session_id:",data.get("session_id"))
    print("count:",data.get("count"))
    
    for index,message in enumerate(data.get("messages",[]),start=1):
        print(f"{index}.[{message.get('role')}]{message.get('content')}")
        
    response.raise_for_status()
    
def test_summary()->None:
    print_title("4. 测试 /sessions/{session_id}/summary")
    
    url=f"{BASE_URL}/sessions/{SESSION_ID}/summary"
    response=requests.get(url,timeout=30)
    
    print("status_code:",response.status_code)
    print("response:",response.json())
    
    response.raise_for_status()
    
    
def test_clear()->None:
    print_title("5. 测试 /sessions/{session_id}/clear")
    
    url=f"{BASE_URL}/sessions/{SESSION_ID}/clear"
    response=requests.post(url,timeout=30)
    print("status_code:",response.status_code)
    print("response:",response.json())
    
    response.raise_for_status()
    
def main() -> None:
    test_health()

    test_chat("我正在学习大模型 Agent,请记住我的目标是暑假找大模型相关实习。")
    test_chat("我现在做到 Day20 了，请你简单鼓励我一下。")

    test_history()
    test_summary()

    test_clear()
    test_history()

    print_title("Day20 API Smoke Test 完成")
    print("所有接口测试已完成。")


if __name__ == "__main__":
    main()
    