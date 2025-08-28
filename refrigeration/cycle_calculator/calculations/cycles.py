from .base import CycleInterface, RefrigerantInterface
from typing import Dict
import CoolProp.CoolProp as CP


class VaporCompressionCycle(CycleInterface):
    """Basic vapor compression refrigeration cycle"""

    def __init__(self, refrigerant: RefrigerantInterface, t_evap: float, t_cond: float, mass_flow: float,
                 efficiency: float = 0.8):
        self.refrigerant = refrigerant
        self.t_evap = t_evap
        self.t_cond = t_cond
        self.mass_flow = mass_flow
        self.efficiency = efficiency

    def calculate(self) -> Dict:
        """Calculate cycle performance"""
        try:
            # State points pressures
            p_evap = self.refrigerant.get_pressure(self.t_evap)
            p_cond = self.refrigerant.get_pressure(self.t_cond)

            # State 1: Saturated vapor leaving evaporator
            h1 = self.refrigerant.get_enthalpy(p_evap, quality=1.0)
            s1 = self.refrigerant.get_entropy(p_evap, quality=1.0)

            # State 2: After compression (isentropic ideal)
            h2s = self._get_isentropic_enthalpy(p_cond, s1)
            h2 = h1 + (h2s - h1) / self.efficiency  # Actual with efficiency

            # State 3: Saturated liquid leaving condenser
            h3 = self.refrigerant.get_enthalpy(p_cond, quality=0.0)

            # State 4: After expansion (isenthalpic)
            h4 = h3

            # Calculate cycle parameters
            q_evap = h1 - h4  # Cooling effect
            w_comp = h2 - h1  # Compressor work
            q_cond = h2 - h3  # Heat rejection

            # Performance metrics
            cop_ideal = q_evap / (h2s - h1)
            cop_actual = q_evap / w_comp
            cooling_capacity = self.mass_flow * q_evap / 1000  # kW
            power_input = self.mass_flow * w_comp / 1000  # kW

            return {
                'cop_ideal': round(cop_ideal, 3),
                'cop_actual': round(cop_actual, 3),
                'cooling_capacity': round(cooling_capacity, 2),
                'power_input': round(power_input, 2),
                'heat_rejection': round(self.mass_flow * q_cond / 1000, 2),
                'points': {
                    'h1': round(h1 / 1000, 2),  # Convert to kJ/kg
                    'h2': round(h2 / 1000, 2),
                    'h3': round(h3 / 1000, 2),
                    'h4': round(h4 / 1000, 2)
                },
                'pressures': {
                    'p_evap': round(p_evap / 1000, 2),  # Convert to kPa
                    'p_cond': round(p_cond / 1000, 2)
                },
                'temperatures': {
                    't_evap': self.t_evap,
                    't_cond': self.t_cond
                }
            }
        except Exception as e:
            raise ValueError(f"Calculation error: {str(e)}")

    def _get_isentropic_enthalpy(self, pressure: float, entropy: float) -> float:
        """Calculate enthalpy at given pressure and entropy"""
        return CP.PropsSI('H', 'P', pressure, 'S', entropy, self.refrigerant.name)
