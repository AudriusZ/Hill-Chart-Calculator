from dataclasses import dataclass, field
from typing import List
import csv
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata
import copy



@dataclass
class TurbineData:
    H: List[float] = field(default_factory=list)
    Q: List[float] = field(default_factory=list)
    n: List[float] = field(default_factory=list)
    D: List[float] = field(default_factory=list)
    Q11: List[float] = field(default_factory=list)
    n11: List[float] = field(default_factory=list)
    efficiency: List[float] = field(default_factory=list)
    power: List[float] = field(default_factory=list)



class HillChart:
    def __init__(self):        
        self.data = TurbineData()


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

    def plot_hill_chart(self, ax=None):       
        try:
            if ax is None:
                raise ValueError("An Axes3D object must be provided for plotting.")
            
            # Plot the surface on the provided Axes3D object
            surf = ax.plot_surface(self.data.n11, self.data.Q11, self.data.efficiency, cmap='viridis', edgecolor='none')
            ax.set_xlabel('n11 (unit speed)')
            ax.set_ylabel('Q11 (unit flow)')
            ax.set_zlabel('Efficiency')
            ax.set_title('Hill Chart')
            # Add a color bar to the existing plot
            fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)  
            print("3D hill chart created successfully")
        except Exception as e:
            print(f"Error in plotting 3D hill chart: {e}")

    def plot_3d_scatter(self, ax=None):
        try:
            if ax is None:
                raise ValueError("An Axes3D object must be provided for plotting.")
            
            # Plot the scatter on the provided Axes3D object
            scatter = ax.scatter(self.data.n11, self.data.Q11, self.data.efficiency, c='red', marker='o')
            print("3D scatter plot created successfully")
        except Exception as e:
            print(f"Error in plotting 3D scatter plot: {e}")


    def plot_hill_chart_contour(self, ax=None, data_type='default'):
        try:
            if ax is None:
                fig, ax = plt.subplots()
            else:
                fig = plt.gcf()
                
            # Select the data based on the type
            if data_type == 'default':
                x = np.array(self.data.n11)
                y = np.array(self.data.Q11)
                z = np.array(self.data.efficiency)
                xlabel = 'n11 (unit speed)'
                ylabel = 'Q11 (unit flow)'
                title = 'Hill Chart'
            elif data_type == 'nD':
                x = np.array(self.data.n)
                y = np.array(self.data.Q)
                z = np.array(self.data.efficiency)
                xlabel = 'n [rpm]'
                ylabel = 'Q [$m^3$/s]'
                title = f'Hill Chart for constant H = {self.data.H[0]:.2f} [m], D = {self.data.D[0]:.2f} [m]'
            else:
                raise ValueError("Invalid data_type. Use 'default' or 'nD'.")

            # Filter out invalid values
            valid_mask = ~np.isnan(x) & ~np.isnan(y) & ~np.isnan(z) & ~np.isinf(x) & ~np.isinf(y) & ~np.isinf(z)
            x = x[valid_mask]
            y = y[valid_mask]
            z = z[valid_mask]

            # Create grid coordinates for the contour plot
            x_grid = np.linspace(x.min(), x.max(), num=101)
            y_grid = np.linspace(y.min(), y.max(), num=101)
            x_grid, y_grid = np.meshgrid(x_grid, y_grid)

            # Interpolate unstructured data
            z_grid = griddata((x, y), z, (x_grid, y_grid), method='cubic')

            # Create the contour plot
            levels = np.round(np.linspace(np.nanmin(z_grid), np.nanmax(z_grid), num=30), 3)
            contour = ax.contourf(x_grid, y_grid, z_grid, levels=levels, cmap='viridis')
            contour_lines = ax.contour(x_grid, y_grid, z_grid, levels=levels, colors='k', linewidths=0.5)
            ax.clabel(contour_lines, inline=False, fontsize=8, fmt='%.2f')

            # Add color bar
            cbar = fig.colorbar(contour, ax=ax)
            cbar.set_label('Efficiency')

            # Set labels and title
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.set_title(title)

            plt.show(block=False)
            print("Hill chart contour created successfully")

            return fig, ax

        except Exception as e:
            print(f"Error in plotting hill chart contour: {e}")
          
    


    def plot_efficiency_vs_Q(self, ax=None):
        try:
            if ax is None:
                raise ValueError("An Axes object must be provided for subplots.")
            
            ax.plot(self.data.Q, self.data.efficiency, 'bo-', label='Efficiency vs Q')
            ax.set_xlabel('Q [$m^3$/s]')
            ax.set_ylabel('Efficiency')
            ax.set_title(f'n = {self.data.n[0]:.1f} [rpm], H = {self.data.H[0]:.2f} [m], D = {self.data.D[0]:.2f} [m]')
            ax.grid(True)
            ax.legend()
            
            print("Efficiency vs Q curve created successfully")

        except Exception as e:
            print(f"Error in plotting Efficiency vs Q: {e}")

    def plot_efficiency_vs_n(self, ax=None):
        try:           
            if ax is None:
                raise ValueError("An Axes object must be provided for subplots.")            
            
            ax.plot(self.data.n, self.data.efficiency, 'bo-', label='Efficiency vs n')
            ax.set_xlabel('n [rpm]')
            ax.set_ylabel('Efficiency')
            ax.set_title(f'Q = {self.data.Q[0]:.1f} [$m^3$/s], H = {self.data.H[0]:.2f} [m], D = {self.data.D[0]:.2f}[m]')
            ax.grid(True)

            ax.legend()
            print("Efficiency vs n curve created successfully")
        except Exception as e:
            print(f"Error in plotting Efficiency vs n: {e}")

    def plot_power_vs_Q(self, ax=None):
        try:           
            if ax is None:
                raise ValueError("An Axes object must be provided for subplots.")  
            
            ax.plot(self.data.Q, self.data.power, 'bo-', label='Power vs Q')
            ax.set_xlabel('Q [$m^3$/s]')
            ax.set_ylabel('Power [W]')
            ax.set_title(f'n = {self.data.n[0]:.1f} [rpm], H = {self.data.H[0]:.2f} [m], D = {self.data.D[0]:.2f} [m]')
            ax.grid(True)
            ax.legend()
            
            print("Power vs Q curve created successfully")
        except Exception as e:
            print(f"Error in plotting Power vs Q: {e}")

    def plot_power_vs_n(self, ax=None):
        try:           
            if ax is None:
                raise ValueError("An Axes object must be provided for subplots.")  
            
            ax.plot(self.data.n, self.data.power, 'bo-', label='Power vs n')
            ax.set_xlabel('n [rpm]')
            ax.set_ylabel('Power [W]')
            ax.set_title(f'Q = {self.data.Q[0]:.1f} [$m^3$/s], H = {self.data.H[0]:.2f} [m], D = {self.data.D[0]:.2f} [m]')
            ax.grid(True)
            ax.legend()
            
            print("Power vs n curve created successfully")
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
    
    #legacy code
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


