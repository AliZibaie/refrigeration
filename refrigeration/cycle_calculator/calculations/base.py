from abc import ABC, abstractmethod
from typing import Dict, Optional


class RefrigerantInterface(ABC):
    """Interface for refrigerant properties"""

    @abstractmethod
    def get_pressure(self, temperature: float) -> float:
        """Get saturation pressure at given temperature"""
        pass

    @abstractmethod
    def get_enthalpy(self, pressure: float, quality: Optional[float] = None,
                     temperature: Optional[float] = None) -> float:
        """Get enthalpy at given conditions"""
        pass

    @abstractmethod
    def get_entropy(self, pressure: float, quality: Optional[float] = None,
                    temperature: Optional[float] = None) -> float:
        """Get entropy at given conditions"""
        pass


class CycleInterface(ABC):
    """Interface for thermodynamic cycle calculations"""

    @abstractmethod
    def calculate(self) -> Dict:
        """Calculate cycle performance"""
        pass


class DiagramInterface(ABC):
    """Interface for diagram generation"""

    @abstractmethod
    def create_ph_diagram(self, data: Dict) -> str:
        """Create P-h diagram"""
        pass
