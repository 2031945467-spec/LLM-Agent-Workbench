from pathlib import Path
from typing import Optional
from src.tools.calculator import ToolResult

class FileReaderTool:
    name="file_reader"
    description="用于读取项目目录内的文本文件，支持 .txt、.md、.json、.py。"
    
    ALLOWED_EXTENSIONS={".txt",".md",".json",".py"}
    MAX_FILE_SIZE=1024*1024
    
    def __init__(self,base_dir:str=".")->None:
        self.base_dir=Path(base_dir).resolve()
        
    def run(self,file_path:str)->ToolResult:
        file_path=file_path.strip()
        
        if not file_path:
            return ToolResult(
                success=False,
                error="文件路径不能为空"
            )
        try:
            target_path=self._resolve_safe_path(file_path)
            self._validate_file(target_path)
            content=target_path.read_text(encoding="utf-8")
            
            return ToolResult(
                success=True,
                result={
                    "path":str(target_path),
                    "content":content,
                    "size":target_path.stat().st_size
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )
            
    def _resolve_safe_path(self,file_path)->Path:
        target_path=(self.base_dir/file_path).resolve()
        
        try:
            target_path.relative_to(self.base_dir)
        except ValueError:
            raise ValueError("不允许读取项目目录之外的文件")
        
        return target_path
    
    def _validate_file(self,path:Path)->None:
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")
        
        if not path.is_file():
            raise ValueError(f"路径不是文件: {path}")
        
        if path.suffix not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"不支持的文件类型: {path.suffix}"
                f"仅支持: {sorted(self.ALLOWED_EXTENSIONS)}"
            )
            
        file_size=path.stat().st_size
        
        if file_size>self.MAX_FILE_SIZE:
            raise ValueError(
                f"文件太大:{file_size}bytes",
                f"最大允许:{self.MAX_FILE_SIZE}bytes"
            )
            
    def info(self)->str:
        return f"{self.name}:{self.description}"
    

def demo()->None:
    tool=FileReaderTool(base_dir=".")
    
    test_files = [
        "README.md",
        "docs/learning_log.md",
        "requirements.txt",
        "../secret.txt",
        "not_exist.md",
    ]
    
    for file_path in test_files:
        print(f"\n读取文件: {file_path}")
        
        result=tool.run(file_path)
        
        if result.success:
            data = result.result
            content = data["content"]

            print(f"文件路径: {data['path']}")
            print(f"文件大小: {data['size']} bytes")
            print("文件前 300 字符:")
            print(content[:300])
        else:
            print(f"读取失败: {result.error}")


if __name__ == "__main__":
    demo()