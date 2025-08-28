from .refrigerants import CoolPropRefrigerant
from typing import Dict
import CoolProp.CoolProp as CP

class VaporCompressionCycle:
    def __init__(self, refrigerant: str, t_evap: float, t_cond: float, expansion_device: str = 'throttle'):
        self.refrigerant = CoolPropRefrigerant(refrigerant)
        self.t_evap = t_evap + 273.15
        self.t_cond = t_cond + 273.15
        self.expansion_device = expansion_device

    def calculate(self) -> Dict:
        p_evap = self.refrigerant.get_pressure(self.t_evap)
        p_cond = self.refrigerant.get_pressure(self.t_cond)

        h1 = self.refrigerant.get_enthalpy(p_evap, quality=1.0)
        s1 = self.refrigerant.get_entropy(p_evap, quality=1.0)

        h2 = CP.PropsSI('H', 'P', p_cond, 'S', s1, self.refrigerant.name)
        t2 = CP.PropsSI('T', 'P', p_cond, 'S', s1, self.refrigerant.name)

        h3 = self.refrigerant.get_enthalpy(p_cond, quality=0.0)
        s3 = self.refrigerant.get_entropy(p_cond, quality=0.0)

        if self.expansion_device == 'throttle':
            h4 = h3
            s4 = CP.PropsSI('S', 'P', p_evap, 'H', h4, self.refrigerant.name)
        else:
            s4 = s3
            h4 = CP.PropsSI('H', 'P', p_evap, 'S', s4, self.refrigerant.name)

        t4 = CP.PropsSI('T', 'P', p_evap, 'H', h4, self.refrigerant.name)
        x4 = CP.PropsSI('Q', 'P', p_evap, 'H', h4, self.refrigerant.name)

        q_evap = h1 - h4
        w_comp = h2 - h1
        w_turb = h3 - h4 if self.expansion_device == 'turbine' else 0
        net_work = w_comp - w_turb
        cop = q_evap / net_work

        return {
            'cop': round(cop, 3),
            'cooling_capacity': round(q_evap / 1000, 2),
            'points': {
                1: {'h': round(h1/1000, 2), 't': round(self.t_evap-273.15, 1), 'p': round(p_evap/1000, 1), 's': round(s1/1000, 3), 'x': 1.0},
                2: {'h': round(h2/1000, 2), 't': round(t2-273.15, 1), 'p': round(p_cond/1000, 1), 's': round(s1/1000, 3)},
                3: {'h': round(h3/1000, 2), 't': round(self.t_cond-273.15, 1), 'p': round(p_cond/1000, 1), 's': round(s3/1000, 3), 'x': 0.0},
                4: {'h': round(h4/1000, 2), 't': round(t4-273.15, 1), 'p': round(p_evap/1000, 1), 's': round(s4/1000, 3), 'x': round(x4, 3)}
            }
        }

class AbsorptionCycle:
    def __init__(self, refrigerant: str, t_evap: float, t_cond: float, t_gen: float, t_abs: float):
        self.refrigerant = CoolPropRefrigerant(refrigerant)
        self.t_evap = t_evap + 273.15
        self.t_cond = t_cond + 273.15
        self.t_gen = t_gen + 273.15
        self.t_abs = t_abs + 273.15

    def calculate(self) -> Dict:
        p_evap = self.refrigerant.get_pressure(self.t_evap)
        p_cond = self.refrigerant.get_pressure(self.t_cond)

        h1 = self.refrigerant.get_enthalpy(p_evap, quality=1.0)
        h2 = self.refrigerant.get_enthalpy(p_cond, quality=0.0)
        h3 = h2

        q_evap = h1 - h3
        q_gen = 1800000
        cop = q_evap / q_gen

        return {
            'cop': round(cop, 3),
            'cooling_capacity': round(q_evap / 1000, 2),
            'points': {
                1: {'h': round(h1/1000, 2), 't': round(self.t_evap-273.15, 1), 'p': round(p_evap/1000, 1)},
                2: {'h': round(h2/1000, 2), 't': round(self.t_cond-273.15, 1), 'p': round(p_cond/1000, 1)},
                3: {'h': round(h3/1000, 2), 't': round(self.t_evap-273.15, 1), 'p': round(p_evap/1000, 1)}
            }
        }
