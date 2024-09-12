import os
from HillChart import HillChart 
import matplotlib.pyplot as plt
import copy
import tkinter as tk
import numpy as np

class HillChartProcessor:
    def __init__(self):
        # Initialize the Tkinter root window (you can hide it if necessary)
        self.root_window = tk.Tk()
        self.root_window.withdraw()  # Hide the root window as it's not needed

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

    def get_output_parameters(self, output_options, output_suboptions):        
        self.output_options = output_options   
        self.output_suboptions = output_suboptions   

    def prepare_core_data(self):
        
        BEP_values = HillChart()
        BEP_values.read_hill_chart_values(self.datapath)
        BEP_values.filter_for_maximum_efficiency()
        BEP_values.calculate_cases(self.selected_values, self.var1, self.var2)
        BEP_data = BEP_values.return_values()

        Raw_data = HillChart()        
        Raw_data.read_hill_chart_values(self.datapath)

        hill_values = copy.deepcopy(Raw_data)

        if self.extrapolate_n11:
            hill_values.extrapolate_along_n11(min_n11=self.n11_min, max_n11=self.n11_max, n_n11=self.n_n11)

        if self.extrapolate_blade:
            hill_values.extrapolate_along_blade_angles(min_angle=self.min_angle, max_angle=self.max_angle, n_angle=self.n_angle)

        hill_values.prepare_hill_chart_data()

        return BEP_data, hill_values, Raw_data
    
    def generate_outputs(self):        
        BEP_data, hill_values, raw_data = self.prepare_core_data()

        # Generate the outputs based on user selection
        if self.output_options.get("3D Hill Chart"):
            self.plot_3d_hill_chart(hill_values)

        if self.output_options.get("Hill Chart Contour"):            
            suboptions = self.output_suboptions.get("Hill Chart Contour", {})
            plot_blade_angles = not suboptions.get("Hide Blade Angle Lines")                
            self.plot_hill_chart_contour(hill_values, BEP_data, plot_blade_angles=plot_blade_angles)            

        if self.output_options.get("2D Curve Slices"):
            self.plot_curve_slices(hill_values, BEP_data)

        # Check if the main option "2D Curve Slices - const.blade" exists and is enabled
        if self.output_options.get("2D Curve Slices - const.blade"):
            suboptions = self.output_suboptions.get("2D Curve Slices - const.blade", {})

            # Now check the sub-options within "2D Curve Slices - const.blade"
            if suboptions.get("Const. Head"):
                self.plot_blade_slices(hill_values, BEP_data)

            if suboptions.get("Const. n"):
                self.plot_blade_slices_const_n(hill_values, BEP_data)

            if suboptions.get("Const. efficiency"): 
                self.plot_blade_slices_const_efficiency(raw_data,BEP_data)                

        if self.output_options.get("Normalized Hill Chart Contour"):
            suboptions = self.output_suboptions.get("Normalized Hill Chart Contour", {})
            plot_blade_angles = not suboptions.get("Hide Blade Angle Lines")        
            self.plot_normalized_hill_chart_contour(hill_values, BEP_data, plot_blade_angles = plot_blade_angles)

        if self.output_options.get("Normalized 2D Curve Slices"):
            self.plot_curve_slices(hill_values, BEP_data, normalize = True)

        if self.output_options.get("Normalized 2D Curve Slices - const.blade"):           

            suboptions = self.output_suboptions.get("Normalized 2D Curve Slices - const.blade", {})

            # Now check the sub-options within "2D Curve Slices - const.blade"
            if suboptions.get("Const. Head"):
                self.plot_blade_slices(hill_values, BEP_data, normalize = True)

            if suboptions.get("Const. n"):
                self.plot_blade_slices_const_n(hill_values, BEP_data, normalize = True)

            if suboptions.get("Const. efficiency"): 
                self.plot_blade_slices_const_efficiency(raw_data, BEP_data, normalize = True)     

        if self.output_options.get("Best efficiency point summary"):
            self.display_results_in_textbox(BEP_data)
    
    def plot_3d_hill_chart(self, hill_values):
        fig = plt.figure()
        ax1 = fig.add_subplot(111, projection='3d')        
        hill_values.plot_hill_chart(ax=ax1)
        raw_data = HillChart()
        raw_data.read_hill_chart_values(self.datapath)                
        raw_data.plot_3d_scatter(ax=ax1)
        plt.show(block=False)
    
    def plot_hill_chart_contour(self, hill_values, BEP_data, plot_blade_angles = True):
        # Create a deep copy of hill_values
        hill_values_nD = copy.deepcopy(hill_values)

        # Create subplots
        _, ax2 = plt.subplots(1, 2, figsize=(15, 7))
        
        # Plot the first contour plot
        hill_values.plot_hill_chart_contour(ax=ax2[0], n_contours=self.n_contours, data_type='default')

        
        if plot_blade_angles:
            # Plot the angle contour lines
            line_coords = hill_values.find_contours_at_angles()            
            if line_coords is not None:
                hill_values.plot_contour_lines(ax2[0], line_coords)

        # Calculate the second contour plot
        hill_values_nD.calculate_cases([1, 4], BEP_data.H[0], BEP_data.D[0])        
        
        # Plot the second contour plot
        hill_values_nD.plot_hill_chart_contour(ax=ax2[1], n_contours=self.n_contours, data_type='nD')

        if plot_blade_angles:
            # Plot the angle contour lines
            line_coords2 = hill_values_nD.find_contours_at_angles(case ='nD')            
            if line_coords is not None:
                hill_values_nD.plot_contour_lines(ax2[1], line_coords2)

        # Adjust layout and show plot
        plt.tight_layout()
        plt.show(block=False)

    def plot_normalized_hill_chart_contour(self, hill_values, BEP_data, plot_blade_angles = True):
        hill_values_norm = copy.deepcopy(hill_values)        
        

        # Create subplots
        _, ax2 = plt.subplots(1, 2, figsize=(15, 7))        
        
        # Plot the first contour plot
        hill_values.plot_hill_chart_contour(ax=ax2[0],n_contours=self.n_contours, data_type='default')                         

        if plot_blade_angles:
            # Plot the blade contour lines
            line_coords = hill_values.find_contours_at_angles()            
            if line_coords is not None:
                hill_values.plot_contour_lines(ax2[0], line_coords)

        
        # Calculate the second contour
        
        hill_values_norm.normalize('efficiency', BEP_data.efficiency)
        hill_values_norm.normalize('Q11', BEP_data.Q11)
        hill_values_norm.normalize('n11', BEP_data.n11)
        
        
        hill_values_norm.plot_hill_chart_contour(ax=ax2[1],n_contours=self.n_contours, data_type='normalized') 

        if plot_blade_angles:
            # Plot the contour lines
            line_coords2 = hill_values_norm.find_contours_at_angles()            
            if line_coords is not None:
                hill_values_norm.plot_contour_lines(ax2[1], line_coords2)
            
        
        # Adjust layout and show plot
        plt.tight_layout()
        plt.show(block=False)

    def plot_curve_slices(self, hill_values, BEP_data, normalize = False):
        _, ax3 = plt.subplots(2, 2, figsize=(15, 10))  
        
        q_curve_values = copy.deepcopy(hill_values)        
        q_curve_values.slice_hill_chart_data(selected_n11=BEP_data.n11[0], selected_Q11=None)        
        q_curve_values.calculate_cases([3, 4], BEP_data.n[0], BEP_data.D[0])    
        if normalize:
            q_curve_values.normalize('efficiency', BEP_data.efficiency)       
            q_curve_values.normalize('Q', BEP_data.Q)               
            q_curve_values.normalize('power', BEP_data.power)                           
            labels = 'normalized'
        else:
            labels = 'default'
        q_curve_values.plot('Q', 'efficiency',ax=ax3[0,0], label_type = labels)      
        q_curve_values.plot('Q', 'power',ax=ax3[1,0], label_type = labels)      

        n_curve_values = copy.deepcopy(hill_values)        
        n_curve_values.slice_hill_chart_data(selected_Q11=BEP_data.Q11[0])        
        n_curve_values.calculate_cases([2, 4], BEP_data.Q[0], BEP_data.D[0])   
        if normalize:
            n_curve_values.normalize('efficiency', BEP_data.efficiency)       
            n_curve_values.normalize('Q', BEP_data.Q)               
            n_curve_values.normalize('power', BEP_data.power)                           
            labels = 'normalized'
        else:
            labels = 'default'        
        n_curve_values.plot('n', 'efficiency',ax=ax3[0,1], label_type = labels)      
        n_curve_values.plot('n', 'power',ax=ax3[1,1], label_type = labels)      
        
        plt.show(block=False)
        
    def plot_blade_slices(self, hill_values, BEP_data, normalize = False):
        _, ax3 = plt.subplots(2, 2, figsize=(15, 10))  
        blade_slice_values = copy.deepcopy(hill_values)                
        blade_slice_values.slice_hill_chart_data(selected_blade_angle = BEP_data.blade_angle[0])                
        blade_slice_values.calculate_cases([1, 4], BEP_data.H[0], BEP_data.D[0])  
        if normalize:
            blade_slice_values.normalize('efficiency', BEP_data.efficiency)       
            blade_slice_values.normalize('Q', BEP_data.Q)               
            blade_slice_values.normalize('power', BEP_data.power)                              
            blade_slice_values.normalize('n', BEP_data.n)                              
            labels = 'normalized'
        else:
            labels = 'default'
       
        blade_slice_values.plot('Q','efficiency', ax=ax3[0,0],title_type = 'const_blade', label_type = labels)
        blade_slice_values.plot('Q','power', ax=ax3[1,0],title_type = 'const_blade', label_type = labels)
        blade_slice_values.plot('n','efficiency', ax=ax3[0,1],title_type = 'const_blade', label_type = labels)
        blade_slice_values.plot('n','power', ax=ax3[1,1],title_type = 'const_blade', label_type = labels)
        
        plt.show(block=False)    

    def plot_blade_slices_const_n(self, hill_values, BEP_data, normalize = False):
        _, ax3 = plt.subplots(2, 2, figsize=(15, 10))  
        blade_slice_values = copy.deepcopy(hill_values)                
        blade_slice_values.slice_hill_chart_data(selected_blade_angle = BEP_data.blade_angle[0])        
        blade_slice_values.calculate_cases([3, 4], BEP_data.n[0], BEP_data.D[0])                
        if normalize:
            blade_slice_values.normalize('efficiency', BEP_data.efficiency)       
            blade_slice_values.normalize('power', BEP_data.power)       
            blade_slice_values.normalize('Q', BEP_data.Q)               
            blade_slice_values.normalize('H', BEP_data.H)    
            labels = 'normalized'
        else:
            labels = 'default'        

        blade_slice_values.plot('H','Q',ax=ax3[0,0],title_type = 'const_n',label_type = labels)
        blade_slice_values.plot('H','efficiency', ax=ax3[0,1],title_type = 'const_n',label_type = labels)
        blade_slice_values.plot('H','power', ax=ax3[1,0],title_type = 'const_n',label_type = labels)
        blade_slice_values.plot('Q','efficiency', ax=ax3[1,1],title_type = 'const_n',label_type = labels)
        
        plt.show(block=False)    

    def plot_blade_slices_const_efficiency(self, raw_data, BEP_data, normalize = False):
                
        _, ax4 = plt.subplots(1, 2, figsize=(15, 5))                  
        
        fixed_hillchart_point = copy.deepcopy(raw_data) 
        fixed_hillchart_point.filter_for_maximum_efficiency()                                
        H_nom = BEP_data.H[0]        
        H_min = H_nom * 0.2
        H_max = H_nom * 3
        H_step = H_nom * 0.2
        H_var = list(np.arange(H_min, H_max, H_step))                        
        
        for i in H_var:
            fixed_hillchart_point.calculate_cases([1, 4], i, BEP_data.D[0])              
        if normalize:            
            fixed_hillchart_point.normalize('Q', BEP_data.Q)
            fixed_hillchart_point.normalize('H', BEP_data.H)
            fixed_hillchart_point.normalize('power', BEP_data.power)  
            labels = 'normalized'
        else:
            labels = 'default'
         
        fixed_hillchart_point.plot('H','Q',ax=ax4[0],title_type = 'const_efficiency',label_type = labels)
        fixed_hillchart_point.plot('H','power',ax=ax4[1],title_type = 'const_efficiency',label_type = labels)
        
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