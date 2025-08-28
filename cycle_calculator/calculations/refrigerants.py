import CoolProp.CoolProp as CP
from .base import RefrigerantInterface
from typing import Optional


class CoolPropRefrigerant(RefrigerantInterface):
    """CoolProp implementation for refrigerant properties"""

    def __init__(self, name: str):
        self.name = name
        try:
            # Test if refrigerant exists in CoolProp
            CP.PropsSI('Tcrit', self.name)
        except Exception as e:
            raise ValueError(f"Refrigerant {name} not found in CoolProp: {e}")

    def get_pressure(self, temperature: float) -> float:
        """Get saturation pressure at temperature (K)"""
        temp_k = temperature + 273.15 if temperature < 200 else temperature
        return CP.PropsSI('P', 'T', temp_k, 'Q', 0, self.name)

    def get_enthalpy(self, pressure: float, quality: Optional[float] = None,
                     temperature: Optional[float] = None) -> float:
        """Get enthalpy (J/kg)"""
        if quality is not None:
            return CP.PropsSI('H', 'P', pressure, 'Q', quality, self.name)
        elif temperature is not None:
            temp_k = temperature + 273.15 if temperature < 200 else temperature
            return CP.PropsSI('H', 'P', pressure, 'T', temp_k, self.name)
        else:
            raise ValueError("Either quality or temperature must be provided")

    def get_entropy(self, pressure: float, quality: Optional[float] = None,
                    temperature: Optional[float] = None) -> float:
        """Get entropy (J/kg.K)"""
        if quality is not None:
            return CP.PropsSI('S', 'P', pressure, 'Q', quality, self.name)
        elif temperature is not None:
            temp_k = temperature + 273.15 if temperature < 200 else temperature
            return CP.PropsSI('S', 'P', pressure, 'T', temp_k, self.name)
        else:
            raise ValueError("Either quality or temperature must be provided")

    def get_temperature(self, pressure: float, quality: float = 0) -> float:
        """Get saturation temperature at pressure"""
        temp_k = CP.PropsSI('T', 'P', pressure, 'Q', quality, self.name)
        return temp_k - 273.15  # Return in Celsius
