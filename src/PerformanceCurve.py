from HillChart import HillChart
import numpy as np
import csv
from datetime import datetime

class PerformanceCurve(HillChart):
    def __init__(self, hill_values):
        # Initialize using the existing HillChart instance
        super().__init__()
        self.data = hill_values.data  # Use the data from the passed HillChart instance

    def slice_hill_chart_data(self, selected_n11=None, selected_Q11=None, selected_blade_angle = None):
        if selected_n11 is not None:
            # Find the index of the closest value in n11 grid
            idx = (np.abs(self.data.n11[0, :] - selected_n11)).argmin()
            
            # Extract the slice along n11
            n11_slice = self.data.n11[:, idx]
            Q11_slice = self.data.Q11[:, idx]
            efficiency_slice = self.data.efficiency[:, idx]
            blade_angle_slice = self.data.blade_angle[:, idx]
        
        elif selected_Q11 is not None:
            # Find the index of the closest value in Q11 grid
            idx = (np.abs(self.data.Q11[:, 0] - selected_Q11)).argmin()
            
            # Extract the slice along Q11
            n11_slice = self.data.n11[idx, :]
            Q11_slice = self.data.Q11[idx, :]
            efficiency_slice = self.data.efficiency[idx, :]
            blade_angle_slice = self.data.blade_angle[:, idx]
        
        elif selected_blade_angle is not None:
            line_coords = self.find_contours_at_angles(target_angles=selected_blade_angle)       
            n11_coords = line_coords[selected_blade_angle][0]     
            Q11_coords = line_coords[selected_blade_angle][1]
            n11_slice, Q11_slice, efficiency_slice = self.custom_slice_hill_chart_data(n11_coords, Q11_coords)
            blade_angle_slice = [selected_blade_angle] * len(n11_slice)
        
        else:
            raise ValueError("Either selected_n11 or selected_Q11 must be provided")
        
                    # Update self.data to only contain the sliced values
        self.data.clear_data()
        self.data.n11 = n11_slice
        self.data.Q11 = Q11_slice
        self.data.efficiency = efficiency_slice
        self.data.blade_angle = blade_angle_slice

        return n11_slice, Q11_slice, efficiency_slice, blade_angle_slice         
        

    def custom_slice_hill_chart_data(self, n11_array, Q11_array):
        if n11_array is not None and Q11_array is not None:
            # Ensure n11_array and Q11_array are the same length
            if len(n11_array) != len(Q11_array):
                raise ValueError("n11_array and Q11_array must have the same length")

            # Prepare arrays to store interpolated values
            interpolated_efficiency = []

            # Iterate over the custom path
            for n11_val, Q11_val in zip(n11_array, Q11_array):
                # Find indices around the target n11 value for interpolation
                n11_indices = np.searchsorted(self.data.n11[0, :], n11_val) - 1
                Q11_indices = np.searchsorted(self.data.Q11[:, 0], Q11_val) - 1

                # Ensure indices are within bounds
                n11_indices = np.clip(n11_indices, 0, self.data.n11.shape[1] - 2)
                Q11_indices = np.clip(Q11_indices, 0, self.data.Q11.shape[0] - 2)

                # Get the four surrounding points for bilinear interpolation
                x1, x2 = self.data.n11[0, n11_indices], self.data.n11[0, n11_indices + 1]
                y1, y2 = self.data.Q11[Q11_indices, 0], self.data.Q11[Q11_indices + 1, 0]
                Q11_values = self.data.Q11[Q11_indices:Q11_indices+2, n11_indices:n11_indices+2]
                efficiency_values = self.data.efficiency[Q11_indices:Q11_indices+2, n11_indices:n11_indices+2]

                # Perform bilinear interpolation for efficiency
                if (x2 - x1) == 0 or (y2 - y1) == 0:
                    interp_efficiency = efficiency_values.mean()  # Handle edge cases where division by zero could occur
                else:
                    # Linear interpolation in n11 direction
                    f1 = (x2 - n11_val) / (x2 - x1) * efficiency_values[0, 0] + (n11_val - x1) / (x2 - x1) * efficiency_values[0, 1]
                    f2 = (x2 - n11_val) / (x2 - x1) * efficiency_values[1, 0] + (n11_val - x1) / (x2 - x1) * efficiency_values[1, 1]

                    # Linear interpolation in Q11 direction
                    interp_efficiency = (y2 - Q11_val) / (y2 - y1) * f1 + (Q11_val - y1) / (y2 - y1) * f2

                interpolated_efficiency.append(interp_efficiency)

            n11_slice = np.array(n11_array)
            Q11_slice = np.array(Q11_array)
            efficiency_slice = np.array(interpolated_efficiency)

            # Update self.data to only contain the sliced values
            self.data.clear_data()
            self.data.n11 = n11_slice
            self.data.Q11 = Q11_slice
            self.data.efficiency = efficiency_slice
            
            return n11_slice, Q11_slice, efficiency_slice

        else:
            raise ValueError("Both n11_array and Q11_array must be provided")
    
    def plot_2D_chart(self, x_var, y_var, ax=None, title_type = 'default', label_type = 'default'):
               
        try:
            if ax is None:
                raise ValueError("An Axes object must be provided for subplots.")
            
            # Ensure x_var and y_var exist in self.data
            if not hasattr(self.data, x_var) or not hasattr(self.data, y_var):
                raise ValueError(f"Invalid variables '{x_var}' or '{y_var}' in data.")
            
            # Map variables to data    
            x_data = getattr(self.data, x_var)
            y_data = getattr(self.data, y_var)                   
                        
            ax.plot(x_data, y_data, 'b-', label=f"{y_var} vs {x_var}")   

            # Define the formatting for each variable
            format_dict = {
                'blade_angle': '.1f',
                'n': '.1f',
                'Q': '.1f',
                'H': '.2f',
                'D': '.2f',
                'efficiency': '.2f'
            }

            # Construct the title_dict using the specified format for each variable
            title_dict = {
                key: f'{self.data.nomenclature_dict()[key]} = {getattr(self.data, key)[0]:{format_dict[key]}} {self.data.units_dict()[key]}'
                if getattr(self.data, key) is not None and len(getattr(self.data, key)) > 0 else ''
                for key in ['blade_angle', 'n', 'Q', 'H', 'D', 'efficiency']
            }

            # Identify variables with non-constant values
            excluded_vars = {
                key for key in format_dict.keys()
                if getattr(self.data, key) is not None and len(set(getattr(self.data, key))) > 1
            }

            """
            # Define a mapping from title_type to sets of excluded variables
            excluded_vars_map = {
                'default': {x_var, y_var, 'blade_angle', 'efficiency'},
                'const_blade': {'n', 'Q', 'efficiency'},
                'const_n': {'efficiency', 'Q', 'H'},
                'const_efficiency': {'n', 'Q', 'H'}
            }
            

            # Get the excluded variables based on the title_type
            excluded_vars = excluded_vars_map.get(title_type)
            if excluded_vars is None:
                raise ValueError(f"title_type '{title_type}' is not recognized. Available labels: 'default', 'const_blade', 'const_n', 'const_efficiency'.")
            """
            # Construct the title by excluding the specified variables
            included_titles = [title for key, title in title_dict.items() if key not in excluded_vars]
            title = ', '.join(included_titles)

            
            if label_type == 'default':
                x_label = f'{self.data.nomenclature_dict()[x_var]} {self.data.units_dict()[x_var]}'
                y_label = f'{self.data.nomenclature_dict()[y_var]} {self.data.units_dict()[y_var]}'
            elif label_type == 'normalized':
                x_label = f'Normalized {self.data.nomenclature_dict()[x_var]}'
                y_label = f'Normalized {self.data.nomenclature_dict()[y_var]}'
            else:
                raise ValueError(f"Label type '{label_type}' is not recognized.")

            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            ax.set_title(title)
            ax.grid(True)
            ax.legend()

            print(f"{f'{y_var} vs {x_var}'} curve created successfully")

        except Exception as e:
            print(f"Error in plotting {y_var} vs {x_var}: {e}")



    def save_2D_chart_to_csv(self, x_var, y_var, file_name=None, title_type='default', label_type='default'):
        try:
            # Ensure x_var and y_var exist in self.data
            if not hasattr(self.data, x_var) or not hasattr(self.data, y_var):
                raise ValueError(f"Invalid variables '{x_var}' or '{y_var}' in data.")
            
            # Map variables to data    
            x_data = getattr(self.data, x_var)
            y_data = getattr(self.data, y_var)

            # Define the formatting for each variable
            format_dict = {
                'blade_angle': '.1f',
                'n': '.1f',
                'Q': '.1f',
                'H': '.2f',
                'D': '.2f',
                'efficiency': '.2f'
            }

            # Construct the title_dict using the specified format for each variable
            title_dict = {
                key: f'{self.data.nomenclature_dict()[key]} = {getattr(self.data, key)[0]:{format_dict[key]}} {self.data.units_dict()[key]}'
                if getattr(self.data, key) is not None and len(getattr(self.data, key)) > 0 else ''
                for key in ['blade_angle', 'n', 'Q', 'H', 'D', 'efficiency']
            }

            # Define a mapping from title_type to sets of excluded variables
            excluded_vars_map = {
                'default': {x_var, y_var, 'blade_angle', 'efficiency'},
                'const_blade': {'n', 'Q', 'efficiency'},
                'const_n': {'efficiency', 'Q', 'H'},
                'const_efficiency': {'n', 'Q', 'H'}
            }

            # Get the excluded variables based on the title_type
            excluded_vars = excluded_vars_map.get(title_type)
            if excluded_vars is None:
                raise ValueError(f"title_type '{title_type}' is not recognized. Available labels: 'default', 'const_blade', 'const_n', 'const_efficiency'.")

            # Construct the title by excluding the specified variables
            included_titles = [title for key, title in title_dict.items() if key not in excluded_vars]

            # Split the title lines for separate output
            title_lines = "\n".join(included_titles)

            # Generate x and y labels based on label_type
            if label_type == 'default':
                x_label = f'{self.data.nomenclature_dict()[x_var]} {self.data.units_dict()[x_var]}'
                y_label = f'{self.data.nomenclature_dict()[y_var]} {self.data.units_dict()[y_var]}'
            elif label_type == 'normalized':
                x_label = f'Normalized {self.data.nomenclature_dict()[x_var]}'
                y_label = f'Normalized {self.data.nomenclature_dict()[y_var]}'
            else:
                raise ValueError(f"Label type '{label_type}' is not recognized.")

            # If no file name is provided, create a dynamic one
            if not file_name:
                # Get the current date and time
                current_time = datetime.now().strftime('%Y%m%d-%H%M%S')
                # Construct the file name dynamically
                file_name = f"{current_time}-{x_var}-{y_var}-{title_type}_{label_type}.csv"

            # Open the CSV file and manually write the title, labels, and data
            with open(file_name, mode='w', newline='') as file:
                # Manually write the title lines with one variable per line
                file.write(f"{title_lines}\n\n")  # Add an extra new line between the title and data
                file.write(f"{x_label},{y_label}\n")
                
                # Use the CSV writer for the data rows
                writer = csv.writer(file)
                # Write the data rows                
                for x, y in zip(x_data, y_data):
                    writer.writerow([x, y])

            print(f"Data saved successfully to {file_name}")

        except Exception as e:
            print(f"Error saving {y_var} vs {x_var} data to CSV: {e}")

    def plot_and_save_chart(self, x_var, y_var, ax, title_type='default', label_type='default', save_data = True):
        
        #Helper function to plot and save the 2D chart data to CSV.
        try:
            # Plot the 2D chart
            self.plot_2D_chart(x_var, y_var, ax=ax, title_type=title_type, label_type=label_type)

            if save_data:
                # Construct the file name using the prefix and x_var, y_var
                current_time = datetime.now().strftime('%Y%m%d-%H%M%S')
                file_name = f"{current_time}-{x_var}-{y_var}-{title_type}_{label_type}.csv"

                # Save the chart data to CSV
                self.save_2D_chart_to_csv(x_var, y_var, file_name=file_name, title_type=title_type, label_type=label_type)

                print(f"Plot and save operation for {x_var} vs {y_var} completed successfully.")
            
        except Exception as e:
            print(f"Error during plot and save operation for {x_var} vs {y_var}: {e}")
