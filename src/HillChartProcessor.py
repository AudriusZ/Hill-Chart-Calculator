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

    
    
    def plot_individual_hill_chart_contour(self, data_type='default', plot_blade_angles=True, show_standalone=True, ax=None):
        """
        Generalized function to plot individual hill chart contours.

        Parameters:
            data_type (str): 'default' for the first contour, 'nD' for the second, 'normalized' for the third.
            plot_blade_angles (bool): Whether to plot blade angle contour lines.
            show_standalone (bool): Whether to show the plot or return the figure.
            ax (matplotlib.axes.Axes): Axis to plot on (used for subplots).

        Returns:
            fig, ax (if show_standalone=False)
        """
        hill_values = copy.deepcopy(self.hill_values)  # Make a copy to avoid modifying original data
        BEP_data = self.BEP_data

        if data_type == 'nD':  # Case for nD
            hill_values.calculate_cases([1, 4], BEP_data.H[0], BEP_data.D[0])
        
        elif data_type == 'normalized':  # Case for Normalized
            hill_values.normalize('efficiency', BEP_data.efficiency)
            hill_values.normalize('Q11', BEP_data.Q11)
            hill_values.normalize('n11', BEP_data.n11)

        # Create a figure and axis only if none is provided
        if ax is None:
            fig, ax = plt.subplots(figsize=(7.5, 7))
        else:
            fig = ax.figure  # Use the figure from the provided axis

        # Plot the contour plot based on the specified data_type
        hill_values.plot_hill_chart_contour(ax=ax, n_contours=self.n_contours, data_type=data_type)

        if plot_blade_angles:
            line_coords = hill_values.find_contours_at_angles(case=data_type if data_type == 'nD' else None)
            if line_coords is not None:
                hill_values.plot_contour_lines(ax, line_coords)

        # Show or return the figure
        if show_standalone:
            plt.tight_layout()
            plt.show(block=False)
        else:
            return fig, ax


    def plot_hill_chart_contour(self, plot_blade_angles=True, show_standalone=True):
        # Create a single figure with two subplots
        fig, ax2 = plt.subplots(1, 2, figsize=(15, 7))

        # Use the generalized plot_contour function for both subplots
        self.plot_individual_hill_chart_contour(data_type='default', plot_blade_angles=plot_blade_angles, show_standalone=False, ax=ax2[0])
        self.plot_individual_hill_chart_contour(data_type='nD', plot_blade_angles=plot_blade_angles, show_standalone=False, ax=ax2[1])

        # Adjust layout and show or return the figure
        plt.tight_layout()
        if show_standalone:
            plt.show(block=False)
        else:
            return fig


    def plot_normalized_hill_chart_contour(self, plot_blade_angles=True, show_standalone=True):
        """
        Creates a figure with two subplots: one with the default hill chart,
        and another with the normalized hill chart.
        """
        # Create a single figure with two subplots
        fig, ax2 = plt.subplots(1, 2, figsize=(15, 7))

        # Use the generalized function for both subplots
        self.plot_individual_hill_chart_contour(data_type='default', plot_blade_angles=plot_blade_angles, show_standalone=False, ax=ax2[0])
        self.plot_individual_hill_chart_contour(data_type='normalized', plot_blade_angles=plot_blade_angles, show_standalone=False, ax=ax2[1])

        # Adjust layout and show or return
        plt.tight_layout()
        if show_standalone:
            plt.show(block=False)
        else:
            return fig

    def plot_individual_slice(self, x_var, y_var, slice_type, normalize=False, save_data=False, show_standalone=True, ax=None):
        """
        Generalized function to plot individual slices (curve, blade, or constant n).

        Parameters:
            x_var (str): The x-axis variable ('Q', 'n', or 'H').
            y_var (str): The y-axis variable ('efficiency', 'power', or 'Q').
            slice_type (str): The type of slicing ('curve', 'blade', 'const_n').
            normalize (bool): Whether to normalize the data.
            save_data (bool): Whether to save the plotted data.
            show_standalone (bool): Whether to show the plot as a standalone figure.
            ax (matplotlib.axes.Axes): Axis to plot on (used for subplots).

        Returns:
            fig, ax (if show_standalone=False)
        """
        hill_values = self.hill_values
        BEP_data = self.BEP_data

        # Create a new figure only if no axis is provided
        if ax is None:
            fig, ax = plt.subplots(figsize=(7.5, 5))
        else:
            fig = ax.figure

        # Make a deep copy of hill values
        slice_values = copy.deepcopy(hill_values)
        slice_values = PerformanceCurve(slice_values)

        # Determine slicing method
        if slice_type == 'n':            
            slice_values.slice_hill_chart_data(selected_n11=BEP_data.n11[0])
            slice_values.calculate_cases([3, 4], BEP_data.n[0], BEP_data.D[0])
        elif slice_type == 'Q':
            slice_values.slice_hill_chart_data(selected_Q11=BEP_data.Q11[0])
            slice_values.calculate_cases([2, 4], BEP_data.Q[0], BEP_data.D[0])
        elif slice_type == 'blade':
            slice_values.slice_hill_chart_data(selected_blade_angle=BEP_data.blade_angle[0])
            slice_values.calculate_cases([1, 4], BEP_data.H[0], BEP_data.D[0])
        elif slice_type == 'const_n':
            slice_values.slice_hill_chart_data(selected_blade_angle=BEP_data.blade_angle[0])
            slice_values.calculate_cases([3, 4], BEP_data.n[0], BEP_data.D[0])
        else:
            raise ValueError(f"Invalid slice_type: {slice_type}. Must be 'Q', 'n', 'blade', or 'const_n'.")

        # Normalize if required
        if normalize:
            slice_values.normalize(x_var, getattr(BEP_data, x_var))
            slice_values.normalize(y_var, getattr(BEP_data, y_var))

        # Determine title type
        title_type = 'const_blade' if slice_type == 'blade' else 'const_n' if slice_type == 'const_n' else 'default'        

        # Plot the chart
        slice_values.plot_and_save_chart(x_var, y_var, ax, title_type=title_type, label_type='normalized' if normalize else 'default', save_data=save_data)

        # Show or return
        if show_standalone:
            plt.show(block=False)
        else:
            return fig, ax


    def plot_curve_slices(self, normalize=False, save_data=False, show_standalone=True):
        """
        Combines all four plots into a single figure with 2x2 subplots.

        Parameters:
            normalize (bool): Whether to normalize the data.
            save_data (bool): Whether to save the plotted data.
            show_standalone (bool): Whether to show the plot as a standalone figure.

        Returns:
            fig (if show_standalone=False)
        """
        fig, ax3 = plt.subplots(2, 2, figsize=(15, 10))

        # Use the generalized function to create all four plots
        self.plot_individual_slice('Q', 'efficiency', slice_type='n', normalize=normalize, save_data=save_data, show_standalone=False, ax=ax3[0, 0])
        self.plot_individual_slice('Q', 'power', slice_type='n', normalize=normalize, save_data=save_data, show_standalone=False, ax=ax3[1, 0])
        self.plot_individual_slice('n', 'efficiency', slice_type='Q', normalize=normalize, save_data=save_data, show_standalone=False, ax=ax3[0, 1])
        self.plot_individual_slice('n', 'power', slice_type='Q', normalize=normalize, save_data=save_data, show_standalone=False, ax=ax3[1, 1])

        # Show or return
        if show_standalone:
            plt.show(block=False)
        else:
            return fig
      
    


    def plot_blade_slices(self, normalize=False, save_data=False, show_standalone=True):
        """
        Combines all four blade slices into a single figure with 2x2 subplots.

        Parameters:
            normalize (bool): Whether to normalize the data.
            save_data (bool): Whether to save the plotted data.
            show_standalone (bool): Whether to show the plot as a standalone figure.

        Returns:
            fig (if show_standalone=False)
        """
        fig, ax3 = plt.subplots(2, 2, figsize=(15, 10))

        # Use the generalized function to create all four plots
        self.plot_individual_slice('Q', 'efficiency', slice_type='blade', normalize=normalize, save_data=save_data, show_standalone=False, ax=ax3[0, 0])
        self.plot_individual_slice('Q', 'power', slice_type='blade', normalize=normalize, save_data=save_data, show_standalone=False, ax=ax3[1, 0])
        self.plot_individual_slice('n', 'efficiency', slice_type='blade', normalize=normalize, save_data=save_data, show_standalone=False, ax=ax3[0, 1])
        self.plot_individual_slice('n', 'power', slice_type='blade', normalize=normalize, save_data=save_data, show_standalone=False, ax=ax3[1, 1])

        # Show or return
        if show_standalone:
            plt.show(block=False)
        else:
            return fig

    
    def plot_blade_slices_const_n(self, normalize=False, save_data=False, show_standalone=True):
        """
        Combines all four constant n blade slices into a single figure with 2x2 subplots.

        Parameters:
            normalize (bool): Whether to normalize the data.
            save_data (bool): Whether to save the plotted data.
            show_standalone (bool): Whether to show the plot as a standalone figure.

        Returns:
            fig (if show_standalone=False)
        """
        fig, ax3 = plt.subplots(2, 2, figsize=(15, 10))

        # Use the generalized function to create all four plots        
        self.plot_individual_slice('H', 'Q', slice_type='const_n', normalize=normalize, save_data=save_data, show_standalone=False, ax=ax3[0, 0])
        self.plot_individual_slice('H', 'efficiency', slice_type='const_n', normalize=normalize, save_data=save_data, show_standalone=False, ax=ax3[0, 1])
        self.plot_individual_slice('H', 'power', slice_type='const_n', normalize=normalize, save_data=save_data, show_standalone=False, ax=ax3[1, 0])
        self.plot_individual_slice('Q', 'efficiency', slice_type='const_n', normalize=normalize, save_data=save_data, show_standalone=False, ax=ax3[1, 1])

        # Show or return
        if show_standalone:
            plt.show(block=False)
        else:
            return fig

    def plot_individual_const_efficiency(self, x_var, y_var, normalize=False, save_data=False, show_standalone=True, ax=None):
        """
        Generalized function to plot individual blade slices for constant efficiency.

        Parameters:
            x_var (str): The x-axis variable ('H' or 'Q').
            y_var (str): The y-axis variable ('Q', 'n', or 'power').
            normalize (bool): Whether to normalize the data.
            save_data (bool): Whether to save the plotted data.
            show_standalone (bool): Whether to show the plot as a standalone figure.
            ax (matplotlib.axes.Axes): Axis to plot on (used for subplots).

        Returns:
            fig, ax (if show_standalone=False)
        """
        raw_data = self.raw_data
        BEP_data = self.BEP_data 

        # Create a new figure only if no axis is provided
        if ax is None:
            fig, ax = plt.subplots(figsize=(7.5, 5))
        else:
            fig = ax.figure

        # Make a deep copy of raw data
        fixed_hillchart_point = copy.deepcopy(raw_data)
        fixed_hillchart_point = PerformanceCurve(fixed_hillchart_point) 

        # Filter for maximum efficiency
        fixed_hillchart_point.filter_for_maximum_efficiency()

        # Define range for H variation
        H_nom = BEP_data.H[0]        
        H_min = H_nom * 0.2
        H_max = H_nom * 3
        H_step = H_nom * 0.2
        H_var = list(np.arange(H_min, H_max, H_step))                        

        # Iterate over H variations and calculate cases
        for i in H_var:
            fixed_hillchart_point.calculate_cases([1, 4], i, BEP_data.D[0])

        # Normalize if required
        if normalize:
            fixed_hillchart_point.normalize(x_var, getattr(BEP_data, x_var))
            fixed_hillchart_point.normalize(y_var, getattr(BEP_data, y_var))

        # Plot the chart
        fixed_hillchart_point.plot_and_save_chart(x_var, y_var, ax, title_type='const_efficiency', label_type='normalized' if normalize else 'default', save_data=save_data)

        # Show or return
        if show_standalone:
            plt.show(block=False)
        else:
            return fig, ax


    def plot_blade_slices_const_efficiency(self, normalize=False, save_data=False, show_standalone=True):
        """
        Combines all four constant efficiency blade slices into a single figure with 2x2 subplots.

        Parameters:
            normalize (bool): Whether to normalize the data.
            save_data (bool): Whether to save the plotted data.
            show_standalone (bool): Whether to show the plot as a standalone figure.

        Returns:
            fig (if show_standalone=False)
        """
        fig, ax4 = plt.subplots(2, 2, figsize=(15, 10))

        # Use the generalized function to create all four plots
        self.plot_individual_const_efficiency('H', 'Q', normalize=normalize, save_data=save_data, show_standalone=False, ax=ax4[0, 0])
        self.plot_individual_const_efficiency('H', 'n', normalize=normalize, save_data=save_data, show_standalone=False, ax=ax4[1, 0])
        self.plot_individual_const_efficiency('H', 'power', normalize=normalize, save_data=save_data, show_standalone=False, ax=ax4[0, 1])
        self.plot_individual_const_efficiency('Q', 'power', normalize=normalize, save_data=save_data, show_standalone=False, ax=ax4[1, 1])

        # Show or return
        if show_standalone:
            plt.show(block=False)
        else:
            return fig

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

          