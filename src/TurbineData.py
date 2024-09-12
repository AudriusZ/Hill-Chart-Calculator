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
            'Q': '[$m^3$/s]',
            'H': '[m]',
            'D': '[m]',
            'blade_angle': '[°]',
            'Q11': '[$m^3$/s]',
            'n11': '[rpm]',
            'efficiency': '[-]',
            'power': '[W]',
            'Ns': '[rpm]'
        }
    
    def clear_data(self):
        #Clears all data by resetting each attribute to an empty list.
        for attr in vars(self):
            setattr(self, attr, [])