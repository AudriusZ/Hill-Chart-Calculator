
from HillChart import HillChart  # Ensure HillChart module is available in the environment
import matplotlib.pyplot as plt
import copy
import tkinter as tk
import numpy as np

class HillChartProcessor:
    def __init__(self):
        # Initialize the Tkinter root window (you can hide it if necessary)
        self.root_window = tk.Tk()
        self.root_window.withdraw()  # Hide the root window as it's not needed

    def default_turbine_parameters(self):
        datapath = 'Mogu_D1.65m.csv'        
        selected_values = [1,4] #1 - H, 2 - Q, 3 - n, 4 - D
        var1 = 2.15
        var2 = 1.65        

        self.get_file_path(datapath)
        self.get_turbine_parameters(selected_values,var1,var2)

    def default_plot_parameters(self):
        n_contours = 25
        extrapolation_options_vars = [1,1]
        extrapolation_values_n11 = [60,200,10]
        extrapolation_values_blade_angles = [-6, 9.8, 10]
        
        self.get_plot_parameters(n_contours,extrapolation_options_vars,extrapolation_values_n11,extrapolation_values_blade_angles)

    def default_output_parameters(self):       
        output_vars = [1,1,1,1,1,1]
        self.get_output_parameters(output_vars)

    def get_file_path(self, file_path):
        self.datapath = file_path

    def get_turbine_parameters(self, selected_values, var1, var2):
        self.selected_values = selected_values
        self.var1 = var1
        self.var2 = var2  

    def get_plot_parameters(self,n_contours,extrapolation_options_vars,extrapolation_values_n11,extrapolation_values_blade_angles):
        self.n_contours = n_contours        
        
        
        self.extrapolate_n11 = extrapolation_options_vars[0]
        if self.extrapolate_n11:
            self.n11_min = extrapolation_values_n11[0]
            self.n11_max = extrapolation_values_n11[1]
            self.n_n11 = extrapolation_values_n11[2]

        self.extrapolate_blade = extrapolation_options_vars[1]
        if self.extrapolate_blade:
            self.min_angle = extrapolation_values_blade_angles[0]
            self.max_angle = extrapolation_values_blade_angles[1]
            self.n_angle = extrapolation_values_blade_angles[2]

    def get_output_parameters(self, output_vars):        
        self.output_vars = output_vars

    def prepare_core_data(self):
        BEP_values = HillChart()
        BEP_values.read_hill_chart_values(self.datapath)
        BEP_values.filter_for_maximum_efficiency()
        BEP_values.calculate_cases(self.selected_values, self.var1, self.var2)
        BEP_data = BEP_values.return_values()

        hill_values = HillChart()
        hill_values.read_hill_chart_values(self.datapath)

        if self.extrapolate_n11:
            hill_values.extrapolate_along_n11(min_n11=self.n11_min, max_n11=self.n11_max, n_n11=self.n_n11)

        if self.extrapolate_blade:
            hill_values.extrapolate_along_blade_angles(min_angle=self.min_angle, max_angle=self.max_angle, n_angle=self.n_angle)

        hill_values.prepare_hill_chart_data()

        return BEP_data, hill_values
    
    def generate_outputs(self):        
        BEP_data, hill_values = self.prepare_core_data()

        # Generate the outputs based on user selection
        if self.output_vars[0]:
            self.plot_3d_hill_chart(hill_values)

        if self.output_vars[1]:
            line_coords = hill_values.find_contours_at_angles(list(range(-4, 8.8, 2)))            
            self.plot_hill_chart_contour(hill_values, BEP_data, line_coords=line_coords)
            #self.plot_hill_chart_contour(hill_values, BEP_data)

        if self.output_vars[2]:
            self.plot_curve_slices(hill_values, BEP_data)

        if self.output_vars[3]:
            self.plot_normalized_hill_chart_contour(hill_values, BEP_data)

        if self.output_vars[4]:
            self.plot_normalized_curve_slices(hill_values, BEP_data)

        if self.output_vars[5]:
            self.display_results_in_textbox(BEP_data)
    
    def plot_3d_hill_chart(self, hill_values):
        fig = plt.figure()
        ax1 = fig.add_subplot(111, projection='3d')        
        hill_values.plot_hill_chart(ax=ax1)
        raw_data = HillChart()
        raw_data.read_hill_chart_values(self.datapath)                
        raw_data.plot_3d_scatter(ax=ax1)
        plt.show(block=False)

    def plot_hill_chart_contour(self, hill_values, BEP_data, line_coords=None):
        # Create a deep copy of hill_values
        hill_values_nD = copy.deepcopy(hill_values)

        # Create subplots
        _, ax2 = plt.subplots(1, 2, figsize=(15, 7))
        
        # Plot the first contour plot
        hill_values.plot_hill_chart_contour(ax=ax2[0], n_contours=self.n_contours, data_type='default')

        # Plot the custom lines if provided
        if line_coords is not None:
            if isinstance(line_coords, dict):  # Check if line_coords is a dictionary
                for angle, (x_coords, y_coords) in line_coords.items():
                    # Plot the line in black color
                    ax2[0].plot(x_coords, y_coords, color='black', linestyle=':', linewidth=1)
                    
                    # Annotate the line with the angle value
                    mid_index = len(x_coords) // 2  # Midpoint for annotation
                    ax2[0].annotate(f'{angle}°', 
                                    (x_coords[mid_index], y_coords[mid_index]),
                                    textcoords="offset points",
                                    xytext=(0,0), 
                                    ha='center',
                                    fontsize=8,
                                    color='black')
            else:
                # If line_coords is not a dictionary, plot it as a single line
                x_coords, y_coords = line_coords
                ax2[0].plot(x_coords, y_coords, color='black', linestyle='--', linewidth=2)
                
                # Annotate the line with a default value
                mid_index = len(x_coords) // 2  # Midpoint for annotation
                ax2[0].annotate('Custom Line', 
                                (x_coords[mid_index], y_coords[mid_index]),
                                textcoords="offset points",
                                xytext=(0,10), 
                                ha='center',
                                fontsize=10,
                                color='black')

        # Calculate and plot the second contour plot with new data
        hill_values_nD.calculate_cases([1, 4], BEP_data.H[0], BEP_data.D[0])
        hill_values_nD.plot_hill_chart_contour(ax=ax2[1], n_contours=self.n_contours, data_type='nD')

        # Adjust layout and show plot
        plt.tight_layout()
        plt.show(block=False)

    def plot_normalized_hill_chart_contour(self, hill_values, BEP_data):
        hill_values_norm = copy.deepcopy(hill_values)        
        hill_values_norm.normalize_efficiency(BEP_data.efficiency)
        hill_values_norm.normalize_Q11(BEP_data.Q11)
        hill_values_norm.normalize_n11(BEP_data.n11)
        _, ax2 = plt.subplots(1, 2, figsize=(15, 7))        
        hill_values.plot_hill_chart_contour(ax=ax2[0],n_contours=self.n_contours, data_type='default')                         
        hill_values_norm.plot_hill_chart_contour(ax=ax2[1],n_contours=self.n_contours, data_type='normalized') 
        plt.tight_layout()
        plt.show(block=False)

    def plot_curve_slices(self, hill_values, BEP_data):
        _, ax3 = plt.subplots(2, 2, figsize=(15, 10))  
        q_curve_values = copy.deepcopy(hill_values)        
        q_curve_values.slice_hill_chart_data(selected_n11=BEP_data.n11[0], selected_Q11=None)        
        q_curve_values.calculate_cases([3, 4], BEP_data.n[0], BEP_data.D[0])                    
        q_curve_values.plot_efficiency_vs_Q(ax=ax3[0,0])
        q_curve_values.plot_power_vs_Q(ax=ax3[1,0])

        n_curve_values = copy.deepcopy(hill_values)        
        n_curve_values.slice_hill_chart_data(selected_Q11=BEP_data.Q11[0])        
        n_curve_values.calculate_cases([2, 4], BEP_data.Q[0], BEP_data.D[0])
        n_curve_values.plot_efficiency_vs_n(ax=ax3[0,1])
        n_curve_values.plot_power_vs_n(ax=ax3[1,1])
        
        plt.show(block=False)

    def plot_curve_slices_backup(self, hill_values, BEP_data):
        _, ax3 = plt.subplots(2, 2, figsize=(15, 10))  
        q_curve_values = copy.deepcopy(hill_values)        
        q_curve_values.slice_hill_chart_data(selected_n11=BEP_data.n11[0], selected_Q11=None)        
        q_curve_values.calculate_cases([3, 4], BEP_data.n[0], BEP_data.D[0])                    
        q_curve_values.plot_efficiency_vs_Q(ax=ax3[0,0])
        q_curve_values.plot_power_vs_Q(ax=ax3[1,0])

        n_curve_values = copy.deepcopy(hill_values)        
        n_curve_values.slice_hill_chart_data(selected_n11=None, selected_Q11=BEP_data.Q11[0])        
        n_curve_values.calculate_cases([2, 4], BEP_data.Q[0], BEP_data.D[0])
        n_curve_values.plot_efficiency_vs_n(ax=ax3[0,1])
        n_curve_values.plot_power_vs_n(ax=ax3[1,1])
        
        plt.show(block=False)

    def plot_normalized_curve_slices(self, hill_values, BEP_data):
        _, ax3 = plt.subplots(2, 2, figsize=(15, 10))  
        q_curve_values = copy.deepcopy(hill_values)        
        q_curve_values.slice_hill_chart_data(selected_n11=BEP_data.n11[0], selected_Q11=None)        
        q_curve_values.calculate_cases([3, 4], BEP_data.n[0], BEP_data.D[0])            
        q_curve_values.normalize_efficiency(BEP_data.efficiency)       
        q_curve_values.normalize_Q(BEP_data.Q)               
        q_curve_values.normalize_power(BEP_data.power)
        q_curve_values.plot_efficiency_vs_Q(ax=ax3[0,0], labels='normalized')
        q_curve_values.plot_power_vs_Q(ax=ax3[1,0], labels='normalized')

        n_curve_values = copy.deepcopy(hill_values)        
        n_curve_values.slice_hill_chart_data(selected_n11=None, selected_Q11=BEP_data.Q11[0])        
        n_curve_values.calculate_cases([2, 4], BEP_data.Q[0], BEP_data.D[0])
        n_curve_values.normalize_efficiency(BEP_data.efficiency)               
        n_curve_values.normalize_n(BEP_data.n)       
        n_curve_values.normalize_power(BEP_data.power)
        n_curve_values.plot_efficiency_vs_n(ax=ax3[0,1], labels='normalized')
        n_curve_values.plot_power_vs_n(ax=ax3[1,1], labels='normalized')
        
        plt.show(block=False)

    def prepare_text_results(self, BEP_data):
        num_sets = len(BEP_data.H)
        results = []
        for index in range(num_sets):
            results.append("BEP values:\n")
            for attr in ['H', 'Q', 'n', 'D', 'efficiency', 'power', 'Ns']:
                value = getattr(BEP_data, attr)[index] if getattr(BEP_data, attr) else 'N/A'
                if isinstance(value, float):
                    value_format = f"{value:.2f}"
                else:
                    value_format = str(value)
                results.append(f"{attr} = {value_format}\n")
            results.append("\n")
        return ''.join(results)
    
    def print_results(self, BEP_data):
        prepared_text = self.prepare_text_results(BEP_data)
        print(prepared_text)

    def display_results_in_textbox(self, BEP_data):
        prepared_text = self.prepare_text_results(BEP_data)

        # Create a new top-level window using the hidden root window
        result_window = tk.Toplevel(self.root_window)
        result_window.title("BEP Results")
        result_window.geometry("400x300")

        # Create a Text widget in the new window
        text_widget = tk.Text(result_window, wrap='word')
        text_widget.pack(expand=True, fill='both')

        # Insert the prepared text into the Text widget
        text_widget.insert(tk.END, prepared_text)

        # Make the Text widget read-only
        text_widget.config(state=tk.DISABLED)

        # Ensure the GUI is updated
        self.root_window.mainloop()          

    

test_class = False
if test_class:
    test_instance = HillChartProcessor()
    test_instance.default_turbine_parameters()
    test_instance.default_plot_parameters()
    test_instance.default_output_parameters()
    test_instance.generate_outputs()
    print("done")
