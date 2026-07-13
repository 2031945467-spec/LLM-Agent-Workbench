"""
Document Loader

作用：
1. 读取项目目录中的文本文件
2. 把不同类型的文件统一转换为 Document
3. 支持加载单个文件或整个目录
4. 为后续文本切块和向量化做准备
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Document:
    """
    统一的文档数据结构。

    source:
        文档来源路径

    content:
        文档完整文本内容

    metadata:
        文件名、后缀、大小等附加信息
    """

    source: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


class DocumentLoader:
    """
    文档加载器。

    当前支持：
    - .txt
    - .md
    - .py
    - .json
    """

    ALLOWED_EXTENSIONS = {
        ".txt",
        ".md",
        ".py",
        ".json",
    }

    def __init__(self, base_dir: str = ".") -> None:
        """
        base_dir 表示允许读取的项目根目录。
        """

        self.base_dir = Path(base_dir).resolve()

    def load_file(self, file_path: str) -> Document:
        """
        加载单个文件。
        """

        path = self._resolve_safe_path(file_path)
        self._validate_file(path)

        content = path.read_text(encoding="utf-8")

        metadata = {
            "file_name": path.name,
            "extension": path.suffix.lower(),
            "size": path.stat().st_size,
            "relative_path": str(path.relative_to(self.base_dir)),
        }

        return Document(
            source=str(path),
            content=content,
            metadata=metadata,
        )

    def load_directory(
        self,
        directory_path: str,
        recursive: bool = True,
    ) -> list[Document]:
        """
        加载目录中的全部支持文件。

        recursive=True：
            递归读取子目录

        recursive=False：
            只读取当前目录
        """

        directory = self._resolve_safe_path(directory_path)

        if not directory.exists():
            raise FileNotFoundError(f"目录不存在：{directory}")

        if not directory.is_dir():
            raise ValueError(f"目标不是目录：{directory}")

        if recursive:
            paths = directory.rglob("*")
        else:
            paths = directory.glob("*")

        documents: list[Document] = []

        for path in sorted(paths):
            if not path.is_file():
                continue

            if path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
                continue

            document = self.load_file(str(path))
            documents.append(document)

        return documents

    def _resolve_safe_path(self, file_path: str) -> Path:
        """
        把输入路径转换成绝对路径，
        并防止读取项目目录之外的文件。
        """

        path = (self.base_dir / file_path).resolve()

        try:
            path.relative_to(self.base_dir)
        except ValueError as e:
            raise ValueError("不允许读取项目目录之外的文件。") from e

        return path

    def _validate_file(self, path: Path) -> None:
        """
        检查文件是否合法。
        """

        if not path.exists():
            raise FileNotFoundError(f"文件不存在：{path}")

        if not path.is_file():
            raise ValueError(f"目标不是文件：{path}")

        extension = path.suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"不支持的文件类型：{extension}，"
                f"当前支持：{sorted(self.ALLOWED_EXTENSIONS)}"
            )