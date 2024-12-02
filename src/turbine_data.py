from dataclasses import dataclass, field
from typing import List

@dataclass
class TurbineData:
    H: List[float] = field(default_factory=list)
    Q: List[float] = field(default_factory=list)
    n: List[float] = field(default_factory=list)
    D: List[float] = field(default_factory=list)
    blade_angle: List[float] = field(default_factory=list)
    Q11: List[float] = field(default_factory=list)
    n11: List[float] = field(default_factory=list)
    efficiency: List[float] = field(default_factory=list)
    power: List[float] = field(default_factory=list)
    Ns: List[float] = field(default_factory=list)
    

    def __str__(self):
        return (f"TurbineData(H={self.H:.2f}, Q={self.Q:.2f}, n={self.n:.2f}, D={self.D:.2f}, "
                f"blade_angle={self.blade_angle:.2f}, Q11={self.Q11:.2f}, n11={self.n11:.2f}, "
                f"efficiency={float(self.efficiency):.2f}, power={self.power:.2f}, Ns={self.Ns})")
    
    def nomenclature_dict(self):
        return {
            'n': 'n',
            'Q': 'Q',
            'H': 'H',
            'D': 'D',
            'blade_angle': 'Blade Angle',
            'Q11': 'Q11',
            'n11': 'n11',
            'efficiency': 'Efficiency',
            'power': 'Power',
            'Ns': 'Ns'
        }

    def units_dict(self):
        return {
            'n': '[rpm]',
            'Q': '[m^3/s]',
            'H': '[m]',
            'D': '[m]',
            'blade_angle': '[degree]',
            'Q11': '[m^3/s]',
            'n11': '[rpm]',
            'efficiency': '[-]',
            'power': '[W]',
            'Ns': '[rpm]'
        }
    
    def clear_data(self):
        #Clears all data by resetting each attribute to an empty list.
        for attr in vars(self):
            setattr(self, attr, [])