from dataclasses import dataclass, field
from typing import List

@dataclass
class CurveData:
    H: List[float] = field(default_factory=list)
    Q: List[float] = field(default_factory=list)
    n: List[float] = field(default_factory=list)
    D: List[float] = field(default_factory=list)
    Q11: List[float] = field(default_factory=list)
    n11: List[float] = field(default_factory=list)
    efficiency: List[float] = field(default_factory=list)
    power: List[float] = field(default_factory=list)



class SingleCurve:
    def __init__(self, selected_values, options, var1, var2):
        self.selected_values = selected_values
        self.options = options
        self.var1 = var1
        self.var2 = var2
        self.data = CurveData()

    def read_hill_chart_values(self):
        try:
            # Setting multiple BEP values directly to the data instance
            #self.data.Q11.extend([0.876, 0.85, 0.83])
            #self.data.n11.extend([127.609, 125.0, 120.0])
            #self.data.efficiency.extend([0.820, 0.810, 0.800])

            self.data.Q11.extend([0.876])
            self.data.n11.extend([127.609])
            self.data.efficiency.extend([0.820])
        except Exception as e:
            print(f"Error reading BEP values: {e}")
            raise

    def calculate_cases(self):
        try:
            self.read_hill_chart_values()

            # Calculate values for each set of BEP values
            for i in range(len(self.data.Q11)):
                if self.selected_values == [1, 2]:  # H, Q provided
                    H = self.var1
                    Q = self.var2
                    D = (Q / (self.data.Q11[i] * (H)**0.5))**0.5
                    n = (H**0.5) * self.data.n11[i] / D
                
                elif self.selected_values == [1, 3]:  # H, n provided
                    H = self.var1
                    n = self.var2
                    D = (H**0.5) * self.data.n11[i] / n
                    Q = D**2 * self.data.Q11[i] * (H**0.5)
                    
                elif self.selected_values == [1, 4]:  # H, D provided
                    H = self.var1
                    D = self.var2
                    n = (H**0.5) * self.data.n11[i] / D
                    Q = D**2 * self.data.Q11[i] * (H**0.5)

                elif self.selected_values == [2, 3]:  # Q, n provided
                    Q = self.var1
                    n = self.var2
                    D = (Q * self.data.n11[i] / (self.data.Q11[i] * n))**(1/3)
                    H = (n * D / self.data.n11[i])**2

                elif self.selected_values == [2, 4]:  # Q, D provided
                    Q = self.var1
                    D = self.var2
                    H = (Q / (self.data.Q11[i] * (D**2)))**2
                    n = (H**0.5) * self.data.n11[i] / D

                elif self.selected_values == [3, 4]:  # n, D provided
                    n = self.var1
                    D = self.var2
                    H = (n * D / self.data.n11[i])**2
                    Q = D**2 * self.data.Q11[i] * (H**0.5)

                else:
                    print("Invalid selected values, no calculation performed.")
                    continue

                self.data.H.append(H)
                self.data.Q.append(Q)
                self.data.n.append(n)
                self.data.D.append(D)
                power = Q * H * 1000 * 9.8 * self.data.efficiency[i]
                self.data.power.append(power)

        except Exception as e:
            print(f"Error in case calculations: {e}")
            raise

    def return_values(self):
        return self.data


