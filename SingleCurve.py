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
                #print("CSV Headers:", reader.fieldnames)  # Should now correctly show headers without BOM
                
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
    def prepare_hill_chart_data(self):        
        x = np.array(self.data.n11)
        y = np.array(self.data.Q11)
        z = np.array(self.data.efficiency)

        # Create grid coordinates for the surface
        x_grid = np.linspace(x.min(), x.max(), num=101)
        y_grid = np.linspace(y.min(), y.max(), num=101)
        self.data.n11, self.data.Q11 = np.meshgrid(x_grid, y_grid)

        # Interpolate unstructured 3-dimensional data
        self.data.efficiency = griddata((x, y), z, (self.data.n11, self.data.Q11), method='cubic')

        return self.data.n11, self.data.Q11, self.data.efficiency
    
    def slice_hill_chart_data(self, selected_n11=None, selected_Q11=None):
        if selected_n11 is not None:
            # Find the index of the closest value in n11 grid
            idx = (np.abs(self.data.n11[0, :] - selected_n11)).argmin()
            
            # Extract the slice along n11
            n11_slice = self.data.n11[:, idx]
            Q11_slice = self.data.Q11[:, idx]
            efficiency_slice = self.data.efficiency[:, idx]

            # Update self.data to only contain the sliced values
            self.data.n11 = n11_slice
            self.data.Q11 = Q11_slice
            self.data.efficiency = efficiency_slice

            return n11_slice, Q11_slice, efficiency_slice
        
        elif selected_Q11 is not None:
            # Find the index of the closest value in Q11 grid
            idx = (np.abs(self.data.Q11[:, 0] - selected_Q11)).argmin()
            
            # Extract the slice along Q11
            n11_slice = self.data.n11[idx, :]
            Q11_slice = self.data.Q11[idx, :]
            efficiency_slice = self.data.efficiency[idx, :]

            # Update self.data to only contain the sliced values
            self.data.n11 = n11_slice
            self.data.Q11 = Q11_slice
            self.data.efficiency = efficiency_slice

            return n11_slice, Q11_slice, efficiency_slice
        
        else:
            raise ValueError("Either selected_n11 or selected_Q11 must be provided")

        
    
    def overwrite_with_slice(self):
        self.data = copy.deepcopy(self.data)

    def plot_hill_chart(self):       

        try:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            surf = ax.plot_surface(self.data.n11, self.data.Q11, self.data.efficiency, cmap='viridis', edgecolor='none')
            ax.set_xlabel('n11 (unit speed)')
            ax.set_ylabel('Q11 (unit flow)')
            ax.set_zlabel('Efficiency')
            ax.set_title('Hill Chart')
            fig.colorbar(surf, shrink=0.5, aspect=5)  # Add a color bar
            plt.show(block=False)
            print("Hill Chart Created")
        except Exception as e:
            print(f"Error in plotting hill chart: {e}")        

    def plot_hill_chart_contour(self):
        try:
            # Ensure the data does not contain NaN or infinite values
            n11 = np.array(self.data.n11)
            Q11 = np.array(self.data.Q11)
            efficiency = np.array(self.data.efficiency)

            # Filter out invalid values
            valid_mask = ~np.isnan(n11) & ~np.isnan(Q11) & ~np.isnan(efficiency) & ~np.isinf(n11) & ~np.isinf(Q11) & ~np.isinf(efficiency)
            n11 = n11[valid_mask]
            Q11 = Q11[valid_mask]
            efficiency = efficiency[valid_mask]

            # Create grid coordinates for the surface
            n11_grid = np.linspace(n11.min(), n11.max(), num=101)
            Q11_grid = np.linspace(Q11.min(), Q11.max(), num=101)
            n11_grid, Q11_grid = np.meshgrid(n11_grid, Q11_grid)

            # Interpolate unstructured D-dimensional data
            efficiency_grid = griddata((n11, Q11), efficiency, (n11_grid, Q11_grid), method='cubic')

            fig, ax = plt.subplots()

            # Create the contour plot
            levels = np.round(np.linspace(np.nanmin(efficiency_grid), np.nanmax(efficiency_grid), num=30), 3)
            contour = ax.contourf(n11_grid, Q11_grid, efficiency_grid, levels=levels, cmap='viridis')

            # Add contour lines
            contour_lines = ax.contour(n11_grid, Q11_grid, efficiency_grid, levels=levels, colors='k', linewidths=0.5)

            # Add labels to the contour lines
            ax.clabel(contour_lines, inline=False, fontsize=8, fmt='%.2f')

            # Add color bar
            cbar = fig.colorbar(contour)
            cbar.set_label('Efficiency')

            # Labels and title
            ax.set_xlabel('n11 (unit speed)')
            ax.set_ylabel('Q11 (unit flow)')
            ax.set_title('Hill Chart')

            plt.show(block=False)

            print("Hill Chart Created")
        except Exception as e:
            print(f"Error in plotting hill chart: {e}")
    
    def plot_hill_chart_contour_nD(self):
        try:
            # Ensure the data does not contain NaN or infinite values
            n = np.array(self.data.n)
            Q = np.array(self.data.Q)
            efficiency = np.array(self.data.efficiency)

            # Filter out invalid values
            valid_mask = ~np.isnan(n) & ~np.isnan(Q) & ~np.isnan(efficiency) & ~np.isinf(n) & ~np.isinf(Q) & ~np.isinf(efficiency)
            n = n[valid_mask]
            Q = Q[valid_mask]
            efficiency = efficiency[valid_mask]

            # Create grid coordinates for the surface
            n_grid = np.linspace(n.min(), n.max(), num=101)
            Q_grid = np.linspace(Q.min(), Q.max(), num=101)
            n_grid, Q_grid = np.meshgrid(n_grid, Q_grid)

            # Interpolate unstructured D-dimensional data
            efficiency_grid = griddata((n, Q), efficiency, (n_grid, Q_grid), method='cubic')

            fig, ax = plt.subplots()

            # Create the contour plot
            levels = np.round(np.linspace(np.nanmin(efficiency_grid), np.nanmax(efficiency_grid), num=30), 3)
            contour = ax.contourf(n_grid, Q_grid, efficiency_grid, levels=levels, cmap='viridis')

            # Add contour lines
            contour_lines = ax.contour(n_grid, Q_grid, efficiency_grid, levels=levels, colors='k', linewidths=0.5)

            # Add labels to the contour lines
            ax.clabel(contour_lines, inline=False, fontsize=8, fmt='%.2f')

            # Add color bar
            cbar = fig.colorbar(contour)
            cbar.set_label('Efficiency')

            # Labels and title
            ax.set_xlabel('n [rpm]')
            ax.set_ylabel('Q [$m^3$/s]')
            ax.set_title(f'Hill Chart for constant H = {self.data.H[0]:.2f} [m], D = {self.data.D[0]:.2f} [m]')

            plt.show(block=False)

            print("Hill Chart Created")
        except Exception as e:
            print(f"Error in plotting hill chart: {e}")

    def plot_hill_chart_nD(self):       

        try:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            surf = ax.plot_surface(self.data.n, self.data.Q, self.data.efficiency, cmap='viridis', edgecolor='none')
            ax.set_xlabel('n [rpm]')
            ax.set_ylabel('Q [$m^3$/s]')
            ax.set_zlabel('Efficiency')
            ax.set_title(f'Hill Chart for constant H = {self.data.H[0]:.2f} [m], D = {self.data.D[0]:.2f} [m]')
            fig.colorbar(surf, shrink=0.5, aspect=5)  # Add a color bar
            plt.show(block=False)
            print("Hill Chart Created")
        except Exception as e:
            print(f"Error in plotting hill chart: {e}")        


    def plot_efficiency_vs_Q(self):
        try:           

            plt.figure(figsize=(10, 6))
            plt.plot(self.data.Q, self.data.efficiency, 'bo-', label='Efficiency vs Q')
            plt.xlabel('Q [$m^3$/s]')
            plt.ylabel('Efficiency')
            plt.title(f'n = {self.data.n[0]:.1f} [rpm], H = {self.data.H[0]:.2f} [m], D = {self.data.D[0]:.2f} [m]')
            plt.grid(True)
            plt.legend()
            plt.show(block=False)
            print("Efficiency Curve Created")
        except Exception as e:
            print(f"Error in plotting Efficiency vs Q: {e}")

    def plot_efficiency_vs_n(self):
        try:           

            plt.figure(figsize=(10, 6))
            plt.plot(self.data.n, self.data.efficiency, 'bo-', label='Efficiency vs n')
            plt.xlabel('n (rpm)')
            plt.ylabel('Efficiency')
            plt.title(f'Q = {self.data.Q[0]:.1f} [$m^3$/s], H = {self.data.H[0]:.2f} [m], D = {self.data.D[0]:.2f}[m]')
            plt.grid(True)
            plt.legend()
            plt.show(block=False)
            print("Efficiency Curve Created")
        except Exception as e:
            print(f"Error in plotting Efficiency vs n: {e}")

    def plot_power_vs_Q(self):
        try:           

            plt.figure(figsize=(10, 6))
            plt.plot(self.data.Q, self.data.power, 'bo-', label='Power vs Q')
            plt.xlabel('Q [$m^3$/s]')
            plt.ylabel('Power [W]')
            plt.title(f'n = {self.data.n[0]:.1f} [rpm], H = {self.data.H[0]:.2f} [m], D = {self.data.D[0]:.2f} [m]')
            plt.grid(True)
            plt.legend()
            plt.show(block=False)
            print("Power Curve Created")
        except Exception as e:
            print(f"Error in plotting Power vs Q: {e}")

    def plot_power_vs_n(self):
        try:           

            plt.figure(figsize=(10, 6))
            plt.plot(self.data.n, self.data.power, 'bo-', label='Power vs n')
            plt.xlabel('n [rpm]')
            plt.ylabel('Power [W]')
            plt.title(f'Q = {self.data.Q[0]:.1f} [$m^3$/s], H = {self.data.H[0]:.2f} [m], D = {self.data.D[0]:.2f} [m]')
            plt.grid(True)
            plt.legend()
            plt.show(block=False)
            print("Power Curve Created")
        except Exception as e:
            print(f"Error in plotting Power vs n: {e}")

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

            #print("Filtered to maximum efficiency data.")
        except Exception as e:
            print(f"Error filtering data for maximum efficiency: {e}")
            raise


    def calculate_cases(self, selected_values, var1, var2):
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


