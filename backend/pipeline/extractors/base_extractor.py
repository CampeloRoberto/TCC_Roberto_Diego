from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd
import requests


class BaseExtractor(ABC):
    """Contrato comum a todos os extractors (ANVISA, CMED, RENAME)."""

    @abstractmethod
    def extract(self) -> pd.DataFrame:
        """Retorna um DataFrame já com as colunas renomeadas para o schema interno."""
        raise NotImplementedError

    @staticmethod
    def _download(url: str, dest_path: Path, timeout: int = 60) -> Path:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        dest_path.write_bytes(response.content)
        return dest_path
