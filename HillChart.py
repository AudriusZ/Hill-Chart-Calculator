from dataclasses import dataclass, field
from typing import List
import csv
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata
import copy
from scipy.interpolate import CubicSpline



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



class HillChart:
    def __init__(self):        
        self.data = TurbineData()    

    def read_hill_chart_values(self, filename):
        try:
            with open(filename, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                #print("CSV Headers:", reader.fieldnames)  # Should now correctly show headers without BOM
                
                self.data.blade_angle.clear()
                self.data.Q11.clear()
                self.data.n11.clear()
                self.data.efficiency.clear()
                

                for row in reader:
                    self.data.blade_angle.append(float(row['Blade Angle'].strip()))
                    self.data.Q11.append(float(row['Q11'].strip()))
                    self.data.n11.append(float(row['n11'].strip()))  # Use strip() to handle any spaces
                    self.data.efficiency.append(float(row['Efficiency'].strip()))

        except Exception as e:
            print(f"Error reading BEP values from CSV: {e}")
            raise       
    def extrapolate_along_n11(self, min_n11 = None, max_n11 = None, n_n11 = 10):
        # Convert lists to numpy arrays for easier manipulation
        blade_angles = np.array(self.data.blade_angle)
        n11 = np.array(self.data.n11)
        Q11 = np.array(self.data.Q11)
        efficiency = np.array(self.data.efficiency)

        new_blade_angle = []
        new_n11 = []
        new_Q11 = []
        new_efficiency = []

        # Get unique blade angles
        unique_blade_angles = np.unique(blade_angles)

        for angle in unique_blade_angles:
            # Filter data by current blade angle
            mask = blade_angles == angle
            n11_subset = n11[mask]
            Q11_subset = Q11[mask]
            efficiency_subset = efficiency[mask]

            # Sort the subsets based on n11 to ensure proper interpolation
            sorted_indices = np.argsort(n11_subset)
            n11_subset = n11_subset[sorted_indices]
            Q11_subset = Q11_subset[sorted_indices]
            efficiency_subset = efficiency_subset[sorted_indices]

            # Generate 10 evenly spaced new n11 values within the range of the original data
            #new_n11_values = np.linspace(n11_subset.min(), n11_subset.max(), num=10)

            if min_n11 is None:
                min_n11 = n11_subset.min()
            if max_n11 is None:
                max_n11 = n11_subset.max()
            
            # Generate 10 evenly spac   ed new blade_angle values within the range of the original data
            new_n11_values = np.linspace(min_n11, max_n11, n_n11)            

            # Perform cubic interpolation for Q11 and efficiency
            Q11_interpolator = CubicSpline(n11_subset, Q11_subset)
            efficiency_interpolator = CubicSpline(n11_subset, efficiency_subset)

            new_Q11_values = Q11_interpolator(new_n11_values)
            new_efficiency_values = efficiency_interpolator(new_n11_values)

            # Append new values to the lists
            new_blade_angle.extend([angle] * len(new_n11_values))
            new_n11.extend(new_n11_values)
            new_Q11.extend(new_Q11_values)
            new_efficiency.extend(new_efficiency_values)

        # Update the data with the new interpolated points
        self.data.blade_angle = new_blade_angle
        self.data.n11 = new_n11
        self.data.Q11 = new_Q11
        self.data.efficiency = new_efficiency

    def extrapolate_along_blade_angles(self, min_angle = None, max_angle = None, n_angle = 10):
        # Convert lists to numpy arrays for easier manipulation
        blade_angles = np.array(self.data.blade_angle)
        n11 = np.array(self.data.n11)
        Q11 = np.array(self.data.Q11)
        efficiency = np.array(self.data.efficiency)

        new_blade_angle = []
        new_n11 = []
        new_Q11 = []
        new_efficiency = []

        # Get unique n11 values
        unique_n11_values = np.unique(n11)

        for n in unique_n11_values:
            # Filter data by current n11 value
            mask = n11 == n
            blade_angles_subset = blade_angles[mask]
            Q11_subset = Q11[mask]
            efficiency_subset = efficiency[mask]

            # Ensure that n11 values are identical for each blade angle
            if len(np.unique(n11[mask])) != 1:
                print(f"Inconsistent n11 values found for n11={n}")
                continue

            # Sort the subsets based on blade_angle to ensure proper interpolation
            sorted_indices = np.argsort(blade_angles_subset)
            blade_angles_subset = blade_angles_subset[sorted_indices]
            Q11_subset = Q11_subset[sorted_indices]
            efficiency_subset = efficiency_subset[sorted_indices]

            if min_angle is None:
                min_angle = blade_angles_subset.min()
            if max_angle is None:
                max_angle = blade_angles_subset.max()
            
            # Generate 10 evenly spac   ed new blade_angle values within the range of the original data
            new_blade_angle_values = np.linspace(min_angle, max_angle, n_angle)
            

            # Perform cubic interpolation for Q11 and efficiency
            Q11_interpolator = CubicSpline(blade_angles_subset, Q11_subset)
            efficiency_interpolator = CubicSpline(blade_angles_subset, efficiency_subset)

            new_Q11_values = Q11_interpolator(new_blade_angle_values)
            new_efficiency_values = efficiency_interpolator(new_blade_angle_values)

            # Append new values to the lists
            new_blade_angle.extend(new_blade_angle_values)
            new_n11.extend([n] * len(new_blade_angle_values))
            new_Q11.extend(new_Q11_values)
            new_efficiency.extend(new_efficiency_values)

        # Combine original data with new interpolated data
        self.data.blade_angle.extend(new_blade_angle)
        self.data.n11.extend(new_n11)
        self.data.Q11.extend(new_Q11)
        self.data.efficiency.extend(new_efficiency)
        
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

    def plot_hill_chart(self, ax=None, alpha=0.8):       
        try:
            if ax is None:
                raise ValueError("An Axes3D object must be provided for plotting.")
            
            # Plot the surface on the provided Axes3D object
            surf = ax.plot_surface(self.data.n11, self.data.Q11, self.data.efficiency, cmap='viridis', edgecolor='none', alpha=alpha)
            ax.set_xlabel('n11 (unit speed)')
            ax.set_ylabel('Q11 (unit flow)')
            ax.set_zlabel('Efficiency')
            ax.set_title('Hill Chart')
            # Add a color bar to the existing plot            
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


    def plot_hill_chart_contour(self, ax=None, n_contours=35, data_type='default'):
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
            elif data_type == 'normalized':
                x = np.array(self.data.n11)
                y = np.array(self.data.Q11)
                z = np.array(self.data.efficiency)
                xlabel = 'n11 (unit speed) - normalized to BEP'
                ylabel = 'Q11 (unit flow) - normalized to BEP'
                title = 'Hill Chart - normalized to BEP'
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
            levels = np.round(np.linspace(np.nanmin(z_grid), np.nanmax(z_grid), num=n_contours), 3)
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
          
    


    def plot_efficiency_vs_Q(self, ax=None, labels = 'default'):
        try:
            if ax is None:
                raise ValueError("An Axes object must be provided for subplots.")
            
            ax.plot(self.data.Q, self.data.efficiency, 'bo-', label='Efficiency vs Q')

            # Define labels and titles for different options            
            if labels == 'default':                
                x_label = 'Q [$m^3$/s]'
                y_label = 'Efficiency'                
            
            elif labels == 'normalized':                
                x_label = 'Normalized Q'
                y_label = 'Normalized Efficiency'                            
            else:
                raise ValueError(f"labels '{labels}' is not recognized. Available labels: 'default', 'normalized'.")
            title = f'n = {self.data.n[0]:.1f} [rpm], H = {self.data.H[0]:.2f} [m], D = {self.data.D[0]:.2f} [m]'                        
            
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            ax.set_title(title)
            ax.grid(True)
            ax.legend()
            
            print("Efficiency vs Q curve created successfully")

        except Exception as e:
            print(f"Error in plotting Efficiency vs Q: {e}")

    def plot_efficiency_vs_n(self, ax=None, labels = 'default'):
        try:           
            if ax is None:
                raise ValueError("An Axes object must be provided for subplots.")            
            
            ax.plot(self.data.n, self.data.efficiency, 'bo-', label='Efficiency vs n')       

            # Define labels and titles for different options            
            if labels == 'default':                
                x_label = 'n [rpm]'
                y_label = 'Efficiency'                
            
            elif labels == 'normalized':                
                x_label = 'Normalized n'
                y_label = 'Normalized Efficiency'                            
            else:
                raise ValueError(f"labels '{labels}' is not recognized. Available labels: 'default', 'normalized'.")
            title = f'Q = {self.data.Q[0]:.1f} [$m^3$/s], H = {self.data.H[0]:.2f} [m], D = {self.data.D[0]:.2f}[m]'                        
            
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            ax.set_title(title)
            ax.grid(True)

            ax.legend()
            print("Efficiency vs n curve created successfully")
        except Exception as e:
            print(f"Error in plotting Efficiency vs n: {e}")

    def plot_power_vs_Q(self, ax=None, labels='default'):
        try:           
            if ax is None:
                raise ValueError("An Axes object must be provided for subplots.")  
            
            ax.plot(self.data.Q, self.data.power, 'bo-', label='Power vs Q')
            
            # Define labels and titles for different options            
            if labels == 'default':                
                x_label = 'Q [$m^3$/s]'
                y_label = 'Power [W]'                
            
            elif labels == 'normalized':                
                x_label = 'Normalized Q'
                y_label = 'Normalized Power'                            
            else:
                raise ValueError(f"labels '{labels}' is not recognized. Available labels: 'default', 'normalized'.")
            title = f'n = {self.data.n[0]:.1f} [rpm], H = {self.data.H[0]:.2f} [m], D = {self.data.D[0]:.2f} [m]'            
            
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            ax.set_title(title)
            ax.grid(True)
            ax.legend()
            
            print("Power vs Q curve created successfully")
        except Exception as e:
            print(f"Error in plotting Power vs Q: {e}")

    def plot_power_vs_n(self, ax=None, labels='default'):
        try:
            if ax is None:
                raise ValueError("An Axes object must be provided for subplots.")                     
            
            n_data = self.data.n
            power_data = self.data.power

            # Define labels and titles for different options
            if labels == 'default':                
                x_label = 'n [rpm]'
                y_label = 'Power [W]'                
            
            elif labels == 'normalized':                
                x_label = 'Normalized n'
                y_label = 'Normalized Power'                            
            else:
                raise ValueError(f"labels '{labels}' is not recognized. Available labels: 'default', 'normalized'.")
            title = f'Q = {self.data.Q[0]:.1f} [$m^3$/s], H = {self.data.H[0]:.2f} [m], D = {self.data.D[0]:.2f} [m]'

            ax.plot(n_data, power_data, 'bo-', label='Power vs n')
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            ax.set_title(title)
            ax.grid(True)
            ax.legend()
            
            print(f"Power vs n curve created successfully with labels '{labels}'")
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
                Ns = (n*Q**0.5)/H**0.75
                self.data.Ns.append(Ns)

        except Exception as e:
            print(f"Error in case calculations: {e}")
            raise
    def normalize_efficiency(self, efficiency_norm):
        efficiency_norm = np.array(efficiency_norm)
        self.data.efficiency = self.data.efficiency/efficiency_norm

    def normalize_power(self, power_norm):
        power_norm = np.array(power_norm)
        self.data.power = self.data.power/power_norm

    def normalize_Q11(self, Q11_norm):
        Q11_norm = np.array(Q11_norm)
        self.data.Q11 = self.data.Q11/Q11_norm

    def normalize_n11(self, n11_norm):
        n11_norm = np.array(n11_norm)
        self.data.n11 = self.data.n11/n11_norm

    def normalize_Q(self, Q_norm):
        Q_norm = np.array(Q_norm)
        self.data.Q = self.data.Q/Q_norm

    def normalize_n(self, n_norm):
        n_norm = np.array(n_norm)
        self.data.n = self.data.n/n_norm

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


