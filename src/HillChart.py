from TurbineData import TurbineData
import csv
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata
from scipy.interpolate import PchipInterpolator
from matplotlib import path as mpath


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
            #Q11_interpolator = Polynomial.fit(n11_subset, Q11_subset, 2)
            #efficiency_interpolator = Polynomial.fit(n11_subset, efficiency_subset, 2)
            Q11_interpolator = PchipInterpolator(n11_subset, Q11_subset)
            efficiency_interpolator = PchipInterpolator(n11_subset, efficiency_subset)

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

    def extrapolate_along_blade_angles(self, min_angle = None, max_angle = None, n_angle = 2):
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
            
            # Generate evenly spaced new blade_angle values within the range of the original data
            new_blade_angle_values = np.linspace(min_angle, max_angle, n_angle)
            

            # Perform cubic interpolation for Q11 and efficiency
            #Q11_interpolator = Polynomial.fit(blade_angles_subset, Q11_subset, 2)
            #efficiency_interpolator = Polynomial.fit(blade_angles_subset, efficiency_subset, 2)
            Q11_interpolator = PchipInterpolator(blade_angles_subset, Q11_subset)
            efficiency_interpolator = PchipInterpolator(blade_angles_subset, efficiency_subset)

            new_Q11_values = Q11_interpolator(new_blade_angle_values)
            new_efficiency_values = efficiency_interpolator(new_blade_angle_values)

            # Append new values to the lists
            new_blade_angle.extend(new_blade_angle_values)
            new_n11.extend([n] * len(new_blade_angle_values))
            new_Q11.extend(new_Q11_values)
            new_efficiency.extend(new_efficiency_values)

        # Combine original data with new interpolated data
        self.data.blade_angle = new_blade_angle
        self.data.n11 = new_n11
        self.data.Q11 = new_Q11
        self.data.efficiency = new_efficiency

        return new_blade_angle, new_n11, new_Q11, new_efficiency
        
    def fit_efficiency(self,x,y,z):               

        # Create grid coordinates for the surface
        x_grid = np.linspace(x.min(), x.max(), num=101)
        y_grid = np.linspace(y.min(), y.max(), num=101)
        self.data.n11, self.data.Q11 = np.meshgrid(x_grid, y_grid)

        # Interpolate unstructured 3-dimensional data
        self.data.efficiency = griddata((x, y), z, (self.data.n11, self.data.Q11), method='cubic')

        # Apply threshold filtering after interpolation
        threshold = 0.5
        self.data.efficiency[self.data.efficiency < threshold] = np.nan

        return self.data.n11, self.data.Q11, self.data.efficiency
    
    def fit_blade_angle(self,x,y,z):        
        x_grid = np.linspace(x.min(), x.max(), num=101)
        y_grid = np.linspace(y.min(), y.max(), num=101)
        self.data.n11, self.data.Q11 = np.meshgrid(x_grid, y_grid)

        # Interpolate unstructured 3-dimensional data
        self.data.blade_angle = griddata((x, y), z, (self.data.n11, self.data.Q11), method='cubic')        

        return self.data.n11, self.data.Q11, self.data.blade_angle
    
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
            max_blade_angle = self.data.blade_angle[max_eff_index] 

            # Clear existing lists and append only the max values
            self.data.clear_data()

            self.data.Q11 = [max_Q11]
            self.data.n11 = [max_n11]
            self.data.efficiency = [max_efficiency]
            self.data.blade_angle = [max_blade_angle]

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
    
    def normalize(self, attribute_name, norm_value):
        norm_value = np.array(norm_value)
        setattr(self.data, attribute_name, getattr(self.data, attribute_name) / norm_value)

    def return_values(self):
        return self.data 
    
    def prepare_hill_chart_data(self):
        x = np.array(self.data.n11)
        y = np.array(self.data.Q11)
        z_efficiency = np.array(self.data.efficiency)
        z_blade_angle = np.array(self.data.blade_angle)
        
        self.fit_efficiency(x,y,z_efficiency)
        self.fit_blade_angle(x,y,z_blade_angle)    
    
    def find_contours_at_angles(self, target_angles=None, case = None):      
        # Extract relevant data
        if not case:               
            n = self.data.n11
            Q = self.data.Q11
        elif case == 'nD':
            n = self.data.n
            Q = self.data.Q
        else:
            raise ValueError("Undefined case: {}".format(case))
            

        blade_angle = np.array(self.data.blade_angle)  # Ensure blade_angle is a numpy array
        
        # Determine target angles if not provided
        if target_angles is None:
            step = 2
            min_angle = np.nanmin(blade_angle)
            min_angle_int = int(min_angle - (min_angle % step)) + step
            max_angle = np.nanmax(blade_angle)
            max_angle_int = int(max_angle) + 1 if max_angle >= 0 else int(max_angle)
            target_angles = list(range(min_angle_int, max_angle_int, step))        
        else:
            target_angles = [target_angles]
        # Create a new figure and axis for 2D contour plotting
        fig, ax = plt.subplots()  # Use plt.subplots() to create figure and axis

        # Plot contours on the new 2D axis
        contour = ax.contour(n, Q, blade_angle, levels=target_angles)

        # Initialize dictionary to store contour coordinates for each target angle
        contours_dict = {angle: ([], []) for angle in target_angles}

        # Extract paths from each contour collection
        for collection, level in zip(contour.collections, contour.levels):
            for path in collection.get_paths():
                if isinstance(path, mpath.Path):
                    vertices = path.vertices
                    # Determine which level (angle) this path corresponds to
                    for angle in target_angles:
                        if np.isclose(level, angle):
                            contours_dict[angle][0].extend(vertices[:, 0])
                            contours_dict[angle][1].extend(vertices[:, 1])

        # Close the figure to avoid displaying it
        plt.close(fig)

        # Return a dictionary with contour coordinates for each target angle
        return {angle: (np.array(n11_contour), np.array(Q11_contour)) 
                for angle, (n11_contour, Q11_contour) in contours_dict.items()}
    
    
    def plot_contour_lines(self, ax, line_coords):
        """Plot contour lines and annotate them on the given axis."""
        if isinstance(line_coords, dict):  # Check if line_coords is a dictionary
            for angle, (x_coords, y_coords) in line_coords.items():
                # Plot the line in black color
                ax.plot(x_coords, y_coords, color='black', linestyle=':', linewidth=1)
                
                # Annotate the line with the angle value
                mid_index = len(x_coords) // 2  # Midpoint for annotation
                ax.annotate(f'{angle}°', 
                            (x_coords[mid_index], y_coords[mid_index]),
                            textcoords="offset points",
                            xytext=(0,0), 
                            ha='center',
                            fontsize=8,
                            color='black')
        else:
            # If line_coords is not a dictionary, plot it as a single line
            x_coords, y_coords = line_coords
            ax.plot(x_coords, y_coords, color='black', linestyle='--', linewidth=2)
            
            # Annotate the line with a default value
            mid_index = len(x_coords) // 2  # Midpoint for annotation
            ax.annotate('Custom Line', 
                        (x_coords[mid_index], y_coords[mid_index]),
                        textcoords="offset points",
                        xytext=(0,10), 
                        ha='center',
                        fontsize=10,
                        color='black')

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
   
    

    
    
       
   


