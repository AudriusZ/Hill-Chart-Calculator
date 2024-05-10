from dataclasses import dataclass, field
from typing import List
import csv
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata
import copy


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
    def __init__(self):
        '''self.selected_values = selected_values
        self.options = options
        self.var1 = var1
        self.var2 = var2'''
        self.data = CurveData()


    def read_hill_chart_values(self, filename):
        try:
            with open(filename, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                print("CSV Headers:", reader.fieldnames)  # Should now correctly show headers without BOM
                
                self.data.Q11.clear()
                self.data.n11.clear()
                self.data.efficiency.clear()

                for row in reader:
                    self.data.Q11.append(float(row['Q11'].strip()))
                    self.data.n11.append(float(row['n11'].strip()))  # Use strip() to handle any spaces
                    self.data.efficiency.append(float(row['Efficiency'].strip()))

        except Exception as e:
            print(f"Error reading BEP values from CSV: {e}")
            raise       
    def prepare_hill_chart_data(self, selected_n11=None):
        self.hilldata=CurveData()
        x = np.array(self.data.n11)
        y = np.array(self.data.Q11)
        z = np.array(self.data.efficiency)

        # Create grid coordinates for the surface
        x_grid = np.linspace(x.min(), x.max(), num=100)
        y_grid = np.linspace(y.min(), y.max(), num=100)
        self.hilldata.n11, self.hilldata.Q11 = np.meshgrid(x_grid, y_grid)

        # Interpolate unstructured D-dimensional data
        self.hilldata.efficiency = griddata((x, y), z, (self.hilldata.n11, self.hilldata.Q11), method='cubic')

        # Check if a specific n11 value is requested for slicing
        if selected_n11 is not None:
            # Filter Q11 and efficiency values based on selected_n11
            indices = np.where(x == selected_n11)[0]

            filtered_Q11 = y[indices]
            filtered_efficiency = z[indices]
            # Repeat the selected n11 value to match the length of filtered Q11
            filtered_n11 = np.full(filtered_Q11.shape, selected_n11)

            # Convert arrays to lists
            self.hilldata.Q11 = filtered_Q11.tolist()
            self.hilldata.efficiency = filtered_efficiency.tolist()
            self.hilldata.n11 = filtered_n11.tolist()

            return self.hilldata.Q11, self.hilldata.efficiency

        return self.hilldata.n11, self.hilldata.Q11, self.hilldata.efficiency
    
    def overwrite_with_slice(self):
        self.data = copy.deepcopy(self.hilldata)

    def plot_hill_chart(self):       

        try:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            surf = ax.plot_surface(self.hilldata.n11, self.hilldata.Q11, self.hilldata.efficiency, cmap='viridis', edgecolor='none')
            ax.set_xlabel('n11 (Rotational Speed)')
            ax.set_ylabel('Q11 (Flow Rate)')
            ax.set_zlabel('Efficiency')
            ax.set_title('Hill Chart')
            fig.colorbar(surf, shrink=0.5, aspect=5)  # Add a color bar
            plt.show(block=False)
        except Exception as e:
            print(f"Error in plotting hill chart: {e}")        

    def plot_efficiency_vs_Q(self):
        try:           

            plt.figure(figsize=(10, 6))
            plt.plot(self.data.Q, self.data.efficiency, 'bo-', label='Efficiency vs Q')
            plt.xlabel('Q (Flow Rate)')
            plt.ylabel('Efficiency')
            plt.title(f'n = {self.data.n[0]:.1f}, H = {self.data.H[0]:.2f}, D = {self.data.D[0]:.2f}')
            plt.grid(True)
            plt.legend()
            plt.show()
        except Exception as e:
            print(f"Error in plotting Efficiency vs Q11: {e}")

    def filter_for_maximum_efficiency(self):
        try:
            # Check if efficiency list is not empty
            if not self.data.efficiency:
                print("No efficiency data available.")
                return

            # Find the index of the maximum efficiency
            max_eff_index = self.data.efficiency.index(max(self.data.efficiency))
            
            # Retrieve the values from each list at the index of the maximum efficiency
            max_Q11 = self.data.Q11[max_eff_index]
            max_n11 = self.data.n11[max_eff_index]
            max_efficiency = self.data.efficiency[max_eff_index]

            # Clear existing lists and append only the max values
            self.data.Q11 = [max_Q11]
            self.data.n11 = [max_n11]
            self.data.efficiency = [max_efficiency]

            print("Filtered to maximum efficiency data.")
        except Exception as e:
            print(f"Error filtering data for maximum efficiency: {e}")
            raise


    def calculate_cases(self, selected_values, options, var1, var2):
        try:
            #self.read_hill_chart_values()
            if not self.data:
                print("No data available.")
                return

            # Calculate values for each set of BEP values
            for i in range(len(self.data.Q11)):
                if selected_values == [1, 2]:  # H, Q provided
                    H = var1
                    Q = var2
                    D = (Q / (self.data.Q11[i] * (H)**0.5))**0.5
                    n = (H**0.5) * self.data.n11[i] / D
                
                elif selected_values == [1, 3]:  # H, n provided
                    H = var1
                    n = var2
                    D = (H**0.5) * self.data.n11[i] / n
                    Q = D**2 * self.data.Q11[i] * (H**0.5)
                    
                elif selected_values == [1, 4]:  # H, D provided
                    H = var1
                    D = var2
                    n = (H**0.5) * self.data.n11[i] / D
                    Q = D**2 * self.data.Q11[i] * (H**0.5)

                elif selected_values == [2, 3]:  # Q, n provided
                    Q = var1
                    n = var2
                    D = (Q * self.data.n11[i] / (self.data.Q11[i] * n))**(1/3)
                    H = (n * D / self.data.n11[i])**2

                elif selected_values == [2, 4]:  # Q, D provided
                    Q = var1
                    D = var2
                    H = (Q / (self.data.Q11[i] * (D**2)))**2
                    n = (H**0.5) * self.data.n11[i] / D

                elif selected_values == [3, 4]:  # n, D provided
                    n = var1
                    D = var2
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


