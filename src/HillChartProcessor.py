from HillChart import HillChart
from PerformanceCurve import PerformanceCurve 
import matplotlib.pyplot as plt
import copy
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QTextEdit

class HillChartProcessor:
    def __init__(self):
        # Initialize the Tkinter root window (you can hide it if necessary)
        self.root_window = tk.Tk()
        self.root_window.withdraw()  # Hide the root window as it's not needed

        # Attributes to hold core data
        self.BEP_data = None
        self.hill_values = None
        self.raw_data = None
        
        #other attributes
        self.datapath = None
        self.extrapolate_blade = None
        self.extrapolate_n11 = None



    def set_file_path(self, file_path):
        self.datapath = file_path

    def set_turbine_parameters(self, selected_values, var1, var2):
        self.selected_values = selected_values
        self.var1 = var1
        self.var2 = var2  

    def set_plot_parameters(self, n_contours, extrapolation_options_vars,extrapolation_values_n11,extrapolation_values_blade_angles, min_efficiency_limit = 0.5):
        self.n_contours = n_contours        
        self.min_efficiency_limit = min_efficiency_limit
        
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

    def set_surface_fit_parameters(self, params):
        """
        Set surface fit parameters from a dictionary.

        Args:
            params (dict): Dictionary containing surface fit parameters.
        """
        # Set common parameters
        self.min_efficiency_limit = params.get("min_efficiency_limit", 0.5)

        # Handle n11 extrapolation
        self.extrapolate_n11 = params.get("checkBox_extrapolate_n11", False)
        if self.extrapolate_n11:
            self.n11_min = params.get("n11_min", 3)
            self.n11_max = params.get("n11_max", 26)
            self.n_n11 = params.get("n11_pts", 10)

        # Handle blade angle extrapolation
        self.extrapolate_blade = params.get("checkBox_extrapolate_blade_angle", False)
        if self.extrapolate_blade:
            self.min_angle = params.get("blade_angle_min", 60)
            self.max_angle = params.get("blade_angle_max", 180)
            self.n_angle = params.get("blade_angle_pts", 10)



    def set_output_parameters(self, output_options, output_suboptions, settings_options):        
        self.output_options = output_options   
        self.output_suboptions = output_suboptions
        self.settings_options = settings_options

    def get_BEP_data(self):
        return self.BEP_data

    def read_raw_data(self):
        raw_data = HillChart()        
        raw_data.read_hill_chart_values(self.datapath)
        self.raw_data = raw_data
        return raw_data
    
    def prepare_BEP_data(self):        
        BEP_values = copy.deepcopy(self.raw_data)
        BEP_values.filter_for_maximum_efficiency()
        BEP_values.calculate_cases(self.selected_values, self.var1, self.var2)
        BEP_data = BEP_values.return_values()
        self.BEP_data = BEP_data
        return BEP_data
    
    def prepare_core_data(self):
        self.read_raw_data()
        self.prepare_BEP_data()
        hill_values = copy.deepcopy(self.raw_data)

        if self.extrapolate_n11:
            hill_values.extrapolate_along_n11(min_n11=self.n11_min, max_n11=self.n11_max, n_n11=self.n_n11)

        if self.extrapolate_blade:
            hill_values.extrapolate_along_blade_angles(min_angle=self.min_angle, max_angle=self.max_angle, n_angle=self.n_angle)

        hill_values.prepare_hill_chart_data(min_efficiency_limit = self.min_efficiency_limit)
        
        self.hill_values = hill_values        

        return hill_values

    
    
    def generate_outputs(self, show_standalone=True):        
        """
        Generate the outputs based on the user's selection.

        Args:
            show_standalone (bool): Whether to display the 3D Hill Chart as a standalone plot or return for embedding.
        
        Returns:
            tuple: (BEP_data, hill_values, raw_data)
        """
        self.prepare_core_data()

        if self.output_options.get("Best efficiency point summary"):
            self.display_results_in_textbox()
        
        # Generate the outputs based on user selection
        if self.output_options.get("3D Hill Chart"):
            # Handle 3D Hill Chart separately
            fig = self.plot_3d_hill_chart(show_standalone=show_standalone)            

        # Check if normalize setting is enabled
        normalize = self.settings_options.get("Normalize")                    
        save_data = self.settings_options.get("Save 2D Chart Data")                    

        if self.output_options.get("Hill Chart Contour"):            
            suboptions = self.output_suboptions.get("Hill Chart Contour", {})
            plot_blade_angles = not suboptions.get("Hide Blade Angle Lines")  
            if normalize:              
                self.plot_normalized_hill_chart_contour(plot_blade_angles=plot_blade_angles)
            else:
                self.plot_hill_chart_contour(plot_blade_angles=plot_blade_angles)            

        if self.output_options.get("2D Curve Slices"):
            self.plot_curve_slices(normalize=normalize, save_data=save_data)        

        if self.output_options.get("2D Curve Slices - const.blade"):
            suboptions = self.output_suboptions.get("2D Curve Slices - const.blade", {})

            # Now check the sub-options within "2D Curve Slices - const.blade"
            if suboptions.get("Const. Head"):                
                self.plot_blade_slices(normalize=normalize, save_data=save_data)

            if suboptions.get("Const. n"):
                self.plot_blade_slices_const_n(normalize=normalize, save_data=save_data)

            if suboptions.get("Const. efficiency"): 
                self.plot_blade_slices_const_efficiency(normalize=normalize, save_data=save_data)        


        return self.BEP_data, self.hill_values, self.raw_data, fig
      

        
    
    def plot_3d_hill_chart(self, show_standalone=True):
        """
        Plot a 3D Hill Chart using the given hill_values.

        Args:
            hill_values: An object containing data for the 3D Hill Chart.
            show_standalone (bool): Whether to display the chart as a standalone window.
        
        Returns:
            matplotlib.figure.Figure: The created Matplotlib figure (if show_standalone=False).
        """
        

        hill_values = self.hill_values
        # Create the figure and axis
        fig = plt.figure()
        ax1 = fig.add_subplot(111, projection='3d')

        # Plot the hill chart
        hill_values.plot_hill_chart(ax=ax1)

        # Read and overlay raw data as a scatter plot
        raw_data = HillChart()
        raw_data.read_hill_chart_values(self.datapath)
        raw_data.plot_3d_scatter(ax=ax1)

        # Show standalone if requested, otherwise return the figure
        if show_standalone:
            plt.show(block=False)
        else:
            return fig

    
    
    def plot_first_contour(self, plot_blade_angles=True, show_standalone=True, ax=None):
        hill_values = self.hill_values

        # Create a figure and axis only if none is provided
        if ax is None:
            fig, ax = plt.subplots(figsize=(7.5, 7))
        else:
            fig = ax.figure  # Use the figure from the provided axis

        # Plot the first contour plot
        contour = hill_values.plot_hill_chart_contour(ax=ax, n_contours=self.n_contours, data_type='default')

        if plot_blade_angles:
            # Plot the angle contour lines
            line_coords = hill_values.find_contours_at_angles()
            if line_coords is not None:
                hill_values.plot_contour_lines(ax, line_coords)

        # Show or return the figure
        if show_standalone:
            plt.tight_layout()
            plt.show(block=False)
        else:
            return fig, ax


    def plot_second_contour(self, plot_blade_angles=True, show_standalone=True, ax=None):
        hill_values_nD = copy.deepcopy(self.hill_values)
        BEP_data = self.BEP_data

        # Create a figure and axis only if none is provided
        if ax is None:
            fig, ax = plt.subplots(figsize=(7.5, 7))
        else:
            fig = ax.figure  # Use the figure from the provided axis

        # Calculate cases for the second contour plot
        hill_values_nD.calculate_cases([1, 4], BEP_data.H[0], BEP_data.D[0])

        # Plot the second contour plot
        contour = hill_values_nD.plot_hill_chart_contour(ax=ax, n_contours=self.n_contours, data_type='nD')

        if plot_blade_angles:
            # Plot the angle contour lines
            line_coords2 = hill_values_nD.find_contours_at_angles(case='nD')
            if line_coords2 is not None:
                hill_values_nD.plot_contour_lines(ax, line_coords2)

        # Show or return the figure
        if show_standalone:
            plt.tight_layout()
            plt.show(block=False)
        else:
            return fig, ax


    def plot_hill_chart_contour(self, plot_blade_angles=True, show_standalone=True):
        # Create a single figure with two subplots
        fig, ax2 = plt.subplots(1, 2, figsize=(15, 7))

        # Use the first and second contour functions, passing the subplot axes
        self.plot_first_contour(plot_blade_angles=plot_blade_angles, show_standalone=False, ax=ax2[0])
        self.plot_second_contour(plot_blade_angles=plot_blade_angles, show_standalone=False, ax=ax2[1])

        # Adjust layout and show or return the figure
        plt.tight_layout()
        if show_standalone:
            plt.show(block=False)
        else:
            return fig


    def plot_normalized_hill_chart_contour(self, plot_blade_angles = True):
        hill_values = self.hill_values
        BEP_data = self.BEP_data

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

    def plot_curve_slices(self, normalize = False, save_data = False, show_standalone=True):
        hill_values = self.hill_values
        BEP_data = self.BEP_data
        
        fig, ax3 = plt.subplots(2, 2, figsize=(15, 10))  
        
        q_curve_values = copy.deepcopy(hill_values)      
        q_curve_values = PerformanceCurve(q_curve_values)  
        q_curve_values.slice_hill_chart_data(selected_n11=BEP_data.n11[0], selected_Q11=None)        
        q_curve_values.calculate_cases([3, 4], BEP_data.n[0], BEP_data.D[0])    
        if normalize:
            q_curve_values.normalize('efficiency', BEP_data.efficiency)       
            q_curve_values.normalize('Q', BEP_data.Q)               
            q_curve_values.normalize('power', BEP_data.power)                           
            labels = 'normalized'
        else:
            labels = 'default'
        q_curve_values.plot_and_save_chart('Q', 'efficiency', ax3[0, 0], label_type=labels, save_data=save_data)
        q_curve_values.plot_and_save_chart('Q', 'power', ax3[1, 0], label_type=labels, save_data=save_data)               

        n_curve_values = copy.deepcopy(hill_values)
        n_curve_values = PerformanceCurve(n_curve_values)        
        n_curve_values.slice_hill_chart_data(selected_Q11=BEP_data.Q11[0])        
        n_curve_values.calculate_cases([2, 4], BEP_data.Q[0], BEP_data.D[0])   
        if normalize:
            n_curve_values.normalize('efficiency', BEP_data.efficiency)       
            n_curve_values.normalize('Q', BEP_data.Q)               
            n_curve_values.normalize('power', BEP_data.power)                           
            labels = 'normalized'
        else:
            labels = 'default'        
        n_curve_values.plot_and_save_chart('n', 'efficiency',ax=ax3[0,1], label_type = labels, save_data=save_data)      
        n_curve_values.plot_and_save_chart('n', 'power',ax=ax3[1,1], label_type = labels, save_data=save_data)      
        
        # Show standalone if requested, otherwise return the figure
        if show_standalone:
            plt.show(block=False)
        else:
            return fig
        
    def plot_blade_slices(self, normalize = False, save_data = False):
        hill_values = self.hill_values
        BEP_data = self.BEP_data
        
        _, ax3 = plt.subplots(2, 2, figsize=(15, 10))  
        blade_slice_values = copy.deepcopy(hill_values)
        blade_slice_values = PerformanceCurve(blade_slice_values)
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
       
        blade_slice_values.plot_and_save_chart('Q', 'efficiency', ax3[0, 0], title_type='const_blade', label_type = labels, save_data=save_data)
        blade_slice_values.plot_and_save_chart('Q', 'power', ax3[1, 0], title_type='const_blade', label_type = labels, save_data=save_data)
        blade_slice_values.plot_and_save_chart('n', 'efficiency', ax3[0, 1], title_type='const_blade', label_type = labels, save_data=save_data)
        blade_slice_values.plot_and_save_chart('n', 'power', ax3[1, 1], title_type='const_blade', label_type = labels, save_data=save_data)       
        
        
        plt.show(block=False)    

    def plot_blade_slices_const_n(self, normalize = False, save_data = False):
        hill_values = self.hill_values
        BEP_data = self.BEP_data

        _, ax3 = plt.subplots(2, 2, figsize=(15, 10))  
        blade_slice_values = copy.deepcopy(hill_values)
        blade_slice_values = PerformanceCurve(blade_slice_values)                
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

        blade_slice_values.plot_and_save_chart('H','Q',ax=ax3[0,0],title_type = 'const_n',label_type = labels, save_data=save_data)
        blade_slice_values.plot_and_save_chart('H','efficiency', ax=ax3[0,1],title_type = 'const_n',label_type = labels, save_data=save_data)
        blade_slice_values.plot_and_save_chart('H','power', ax=ax3[1,0],title_type = 'const_n',label_type = labels, save_data=save_data)
        blade_slice_values.plot_and_save_chart('Q','efficiency', ax=ax3[1,1],title_type = 'const_n',label_type = labels, save_data=save_data)
        
        
        plt.show(block=False)    

    def plot_blade_slices_const_efficiency(self, normalize = False, save_data = False):
        raw_data = self.raw_data
        BEP_data = self.BEP_data 
                
        _, ax4 = plt.subplots(2, 2, figsize=(15, 10))                  
        
        fixed_hillchart_point = copy.deepcopy(raw_data)
        fixed_hillchart_point = PerformanceCurve(fixed_hillchart_point) 
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
         
        fixed_hillchart_point.plot_and_save_chart('H','Q',ax=ax4[0,0],title_type = 'const_efficiency',label_type = labels, save_data=save_data)
        fixed_hillchart_point.plot_and_save_chart('H','n',ax=ax4[1,0],title_type = 'const_efficiency',label_type = labels, save_data=save_data)
        fixed_hillchart_point.plot_and_save_chart('H','power',ax=ax4[0,1],title_type = 'const_efficiency',label_type = labels, save_data=save_data)
        fixed_hillchart_point.plot_and_save_chart('Q','power',ax=ax4[1,1],title_type = 'const_efficiency',label_type = labels, save_data=save_data)
        
        
        plt.show(block=False) 

    def prepare_text_results(self):
        BEP_data = self.BEP_data
        num_sets = len(BEP_data.H)
        results = []

        # Dictionary for units
        units = {
            'H': '[m]',
            'Q': '[m³/s]',
            'n': '[rpm]',
            'D': '[m]',
            'efficiency': '[-]',
            'power': '[W]',
            'Ns': '[rpm]'
        }

        # Dictionary for varying decimal points
        decimals = {
            'H': 2,
            'Q': 2,
            'n': 1,
            'D': 2,
            'efficiency': 2,
            'power': 0,
            'Ns': 1
        }

        # Prepare the output
        for index in range(num_sets):
            results.append("Best Efficiency Point (BEP) values:\n")
            for attr in ['H', 'Q', 'n', 'D', 'efficiency', 'power', 'Ns']:
                value = getattr(BEP_data, attr)[index] if getattr(BEP_data, attr) else 'N/A'
                if isinstance(value, float):
                    # Format value with varying decimals
                    num_decimals = decimals.get(attr, 2)
                    value_format = f"{value:.{num_decimals}f}"
                else:
                    value_format = str(value)
                unit = units.get(attr, "")  # Fetch the unit for the attribute
                results.append(f"{attr} = {value_format} {unit}\n")
            results.append("\n")
        return ''.join(results)


    def display_results_in_textbox(self, show_standalone = True):        
        prepared_text = self.prepare_text_results()

        # Create a new top-level window
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

        # Show standalone if requested, otherwise return the figure
        if show_standalone:
            plt.show(block=False)
        else:
            return text_widget
        
    def display_results_in_PyQt6_textbox(self, show_standalone = True):
        """
        Create a QTextEdit widget with prepared results text.

        Returns:
            QTextEdit: A PyQt6 text widget containing the results.
        """
        prepared_text = self.prepare_text_results()  # Prepare the text content

        # Create a QTextEdit widget
        text_widget = QTextEdit()
        text_widget.setReadOnly(True)  # Make the widget read-only
        text_widget.setPlainText(prepared_text)  # Insert the prepared text

        return text_widget

          