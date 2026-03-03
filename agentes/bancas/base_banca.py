from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseBanca(ABC):
    """
    Interface base para todas as bancas avaliadoras de startups e soluções.
    Cada banca (RedBull, YCombinator, etc.) deve implementar seus próprios 
    frameworks de pontuação e critérios.
    """

    @abstractmethod
    def carregar_contexto(self, dados: List[Dict[str, Any]]):
        """Carrega os dados (artigos, startups ou problemas) para avaliação."""
        pass

    @abstractmethod
    def avaliar(self, limite: Optional[int] = None) -> List[Dict[str, Any]]:
        """Executa a avaliação lógica (LLM ou heurística) para os itens carregados."""
        pass

    @abstractmethod
    def rankear(self) -> List[Dict[str, Any]]:
        """Ordena os itens avaliados com base nos critérios da banca."""
        pass

    @abstractmethod
    def exportar(self, output_path: str) -> str:
        """Exporta o resultado final em um formato específico (CSV/JSON)."""
        pass

    @property
    @abstractmethod
    def framework_info(self) -> Dict[str, Any]:
        """Retorna metadados sobre o framework de avaliação desta banca."""
        pass
