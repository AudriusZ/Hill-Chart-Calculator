from PyQt6.QtWidgets import (QFileDialog, QMessageBox)

from HillChartProcessor import HillChartProcessor  # Processing logic
from control_processor import ControlProcessor
from maximised_output_processor import MaximisedOutputProcessor
from itertools import product

import os

class MainProcessor():

    def __init__(self):
        # Initialize the processors
        self.processor = HillChartProcessor()
        self.control_processor = ControlProcessor()
        self.maximised_output_processor = MaximisedOutputProcessor()

              
        # Initialize simulation state
        self.simulation_initialized = False        

        # Optional callback for message handling
        self.message_callback = None

        #Figures are standalone if not called from GUI that embeds them
        self.standalone_figures = True

        # Initialise empty BEP data
        self.BEP_data = None
        

    def set_message_callback(self, callback):
        """Pass the callback to all processors."""
        self.message_callback = callback
        self.maximised_output_processor.set_message_callback(callback)
        self.processor.set_message_callback(callback)


    def emit_message(self, message):
        """
        Emit a message using the callback if provided, or print to console.
        """
        if self.message_callback:
            self.message_callback(message)
        else:
            print(message)  # Default behavior for standalone mode

    def load_data(self, datapath):
        #datapath = os.path.join(os.path.dirname(__file__), 'Mogu_D1.65m.csv')  # Adjust path as needed
        self.processor.set_file_path(datapath)
    
    def set_file_path(self,path):
        self.processor.set_file_path(path)    
    
    def get_BEP_data(self):
        """
        Returns:
            BEP data
        """        
        return self.BEP_data  
    
    def set_turbine_size_parameters(self, parameters):                
        var1 = parameters["input_1"]
        var2 = parameters["input_2"]
        selected_values = parameters["selected_values"]
        self.processor.set_turbine_parameters(selected_values, var1, var2)
        self.processor.read_raw_data()
        self.BEP_data = self.processor.prepare_BEP_data()
        text_widget = self.processor.display_results_in_PyQt6_textbox(show_standalone=False)
        return text_widget
    
    def set_surface_fitting_parameters(self, parameters):
        self.processor.set_surface_fit_parameters(parameters)
        self.hill_values = self.processor.prepare_core_data()
        fig = self.processor.plot_3d_hill_chart(show_standalone=False) 
        return fig
    
    def create_contour_plot(self):        
        fig = {}
        fig[1],_ = self.processor.plot_individual_hill_chart_contour(data_type='default',plot_blade_angles=True, show_standalone=False)            
        fig[2],_ = self.processor.plot_individual_hill_chart_contour(data_type='nD', plot_blade_angles=True, show_standalone=False)            
        fig[3],_ = self.processor.plot_individual_hill_chart_contour(data_type='normalized', plot_blade_angles=True, show_standalone=False)                    
        return fig
    
    def create_plot_curve_slices(self, mode = 'Default', normalize = False):
        fig = {}
        
        
        # Define the matrix of possible values for each parameter position
        if mode == 'Default':
            preset_combinations = [
            ('n', 'efficiency', 'blade_angle', 'H', 'D'),
            ('n', 'power', 'blade_angle', 'H', 'D'),

            ('Q', 'efficiency', 'n11', 'H', 'D'),
            ('Q', 'power', 'n11', 'H', 'D'),
            ('blade_angle', 'efficiency', 'n11', 'H', 'D'),
            ('blade_angle', 'power', 'n11', 'H', 'D'),

            ('n', 'efficiency', 'Q11', 'H', 'D'),
            ('n', 'power', 'Q11', 'H', 'D'),

            ('blade_angle', 'efficiency', 'Q11', 'H', 'D'),
            ('blade_angle', 'power', 'Q11', 'H', 'D')
        ]
        elif mode == 'All':
            param_matrix = {
                'x_var': ['n', 'Q', 'blade_angle', 'H','D'],
                'y_var': ['efficiency', 'Q'],
                'slice_by': ['n11', 'Q11', 'blade_angle'],            
                'const_1': ['n','H'],
                'const_2': ['Q','D']
            }

            # Generate all possible parameter combinations dynamically
            preset_combinations = list(product(
                param_matrix['x_var'],
                param_matrix['y_var'],
                param_matrix['slice_by'],
                param_matrix['const_1'],
                param_matrix['const_2']
            ))
        else:
            preset_combinations = [
            ('n', 'efficiency', 'blade_angle', 'H', 'D')
            ]

        

        # Loop through generated combinations and run plot_slice_projection
        for i, params in enumerate(preset_combinations):
            fig[i], _ = self.processor.plot_slice_projection(*params, normalize=normalize, show_standalone=False)

        """
        # Handle constant efficiency cases separately
        const_efficiency_matrix = {
            'x_var': ['H', 'Q'],
            'y_var': ['Q', 'n', 'power']
        }

        const_efficiency_combinations = list(product(
            const_efficiency_matrix['x_var'],
            const_efficiency_matrix['y_var']
        ))

        for i, params in enumerate(const_efficiency_combinations, start=len(preset_combinations)):
            fig[i], _ = self.processor.plot_individual_const_efficiency(*params, normalize=normalize, show_standalone=False)
        
        """
        """
        fig[0],_ = self.processor.plot_slice_projection('Q', 'efficiency', 'n11', 'n', 'D', normalize=normalize, show_standalone=False)        
        fig[1],_ = self.processor.plot_slice_projection('Q', 'power', 'n11', 'n', 'D', normalize=normalize, show_standalone=False)
        fig[2],_ = self.processor.plot_slice_projection('n', 'efficiency', 'Q11', 'Q', 'D', normalize=normalize, show_standalone=False)
        fig[3],_ = self.processor.plot_slice_projection('n', 'power', 'Q11', 'Q', 'D', normalize=normalize, show_standalone=False)
        
        fig[4],_ = self.processor.plot_slice_projection('Q', 'efficiency', 'blade_angle', 'H', 'D', normalize=normalize, show_standalone=False)
        fig[5],_ = self.processor.plot_slice_projection('Q', 'power', 'blade_angle', 'H', 'D', normalize=normalize, show_standalone=False)
        fig[6],_ = self.processor.plot_slice_projection('n', 'efficiency', 'blade_angle', 'H', 'D', normalize=normalize, show_standalone=False)
        fig[7],_ = self.processor.plot_slice_projection('n', 'power', 'blade_angle', 'H', 'D', normalize=normalize, show_standalone=False)

        fig[8],_ = self.processor.plot_slice_projection('H', 'Q', 'blade_angle', 'n', 'D', normalize=normalize, show_standalone=False)
        fig[9],_ = self.processor.plot_slice_projection('H', 'efficiency', 'blade_angle', 'n', 'D', normalize=normalize, show_standalone=False)
        fig[10],_ = self.processor.plot_slice_projection('H', 'power', 'blade_angle', 'n', 'D', normalize=normalize, show_standalone=False)
        fig[11],_ = self.processor.plot_slice_projection('Q', 'efficiency', 'blade_angle', 'n', 'D', normalize=normalize, show_standalone=False)             
        
        fig[12],_ = self.processor.plot_individual_const_efficiency('H', 'Q', normalize=normalize, show_standalone=False)
        fig[13],_ = self.processor.plot_individual_const_efficiency('H', 'n', normalize=normalize, show_standalone=False)
        fig[14],_ = self.processor.plot_individual_const_efficiency('H', 'power', normalize=normalize, show_standalone=False)
        fig[15],_ = self.processor.plot_individual_const_efficiency('Q', 'power', normalize=normalize, show_standalone=False)

        fig[16],_ = self.processor.plot_slice_projection('blade_angle', 'efficiency', 'n11', 'n', 'D', normalize=normalize, show_standalone=False)
        fig[17],_ = self.processor.plot_slice_projection('blade_angle', 'power', 'n11', 'n', 'D', normalize=normalize, show_standalone=False)
        """
        
        return fig

    def maximise_output_action(self, ranges):        
        
        self.maximised_output_processor.maximised_output(self.hill_values.data, self.BEP_data, ranges=ranges)                
        plots = self.maximised_output_processor.generate_plots()

        return plots

    def initialize_simulation(self):
        """
        Initialize the simulation and return the figure and axes for plotting.
        Returns:
            tuple: (fig, axs) for embedding in the GUI.
        """
        try:
            if not self.simulation_initialized:
                # Initialize the simulation with BEP data
                self.control_processor.initialize_simulation(self.hill_values.data, self.BEP_data)

                # Initialize the plots
                fig, axs = self.control_processor.initialize_plot()
                self.simulation_initialized = True
                self.emit_message("Simulation initialized successfully.")
                return fig, axs  # Return the figure and axes for embedding
            else:
                raise RuntimeError("Simulation is already initialized.")
        except Exception as e:
            self.emit_message(f"Error during simulation initialization: {str(e)}")
            raise

    def stop_simulation(self):
        """Stop the simulation through the control processor."""
        self.control_processor.stop_simulation()

    def reset_simulation(self):
        # Initialize simulation state
        self.control_processor = ControlProcessor()
        self.simulation_initialized = False        
        self.control_processor.continue_simulation = False        

    def run_simulation(self, control_parameters, axs, log_callback=None):
        """
        Run the simulation loop with live plot updates.
        Args:
            control_parameters (dict): Parameters for the simulation.
            axs: Plot axes for updating live plots.
            log_callback (callable, optional): Callback for logging status messages.
        """
        try:
            
            self.control_processor.run_simulation(
                control_parameters,                
                axs=axs,  # Pass the plot axes for updates
                log_callback=log_callback
            )
            self.emit_message("Stopped. Press Start to Continue")
        except RuntimeError as e:
            self.emit_message(f"Error during simulation: {str(e)}")
            raise
    
    


    """
    Development mode methods start here
    """

    def default_turbine_hydraulics_action(self):
        """
        Generate and embed the 3D Hill Chart into a new tab.
        """
        try:
            # Set default turbine and plot parameters
            if not self.processor.datapath:
                self.default_pathname()
            self.default_turbine_parameters()
            self.default_plot_parameters()
            self.default_output_parameters()

            # Generate the outputs and get the processed data
            result = self.processor.generate_outputs(show_standalone=self.standalone_figures)

            # Unpack the result (includes fig if embedded)
            self.BEP_data, self.hill_values, _, fig = result                

            #self.emit_message("3D Hill Chart generated successfully.")
            return fig  # Return the result, including 'fig'            
            
        except Exception as e:
            self.emit_message(f"Error during Turbine Hydraulics action: {str(e)}")
            raise  

    def default_pathname(self):
        datapath = os.path.join(os.path.dirname(__file__), 'Mogu_Ns_114_rpm_extended_dataset.csv')  # Adjust path as needed
        self.processor.set_file_path(datapath)
    
    def default_turbine_parameters(self):
        """Set default turbine parameters as in the test."""
        
        selected_values = [1, 4]  # 1 - H, 2 - Q, 3 - n, 4 - D
        var1 = 2.15
        var2 = 1.65        
        self.processor.set_turbine_parameters(selected_values, var1, var2)
        self.BEP_data = self.processor.get_BEP_data()

    def default_plot_parameters(self):
        """Set default plot parameters as in the test."""
        
        min_efficiency_limit = 0.2
        n_contours = 25        
        extrapolation_options_vars = [1, 1]
        extrapolation_values_n11 = [20, 190, 50]
        extrapolation_values_blade_angles = [3, 29, 50]

        self.processor.set_plot_parameters(n_contours, extrapolation_options_vars, extrapolation_values_n11, extrapolation_values_blade_angles, min_efficiency_limit=min_efficiency_limit)

    def default_output_parameters(self):
        """Set default output parameters as in the test."""
        output_options = {
            '3D Hill Chart': 1,
            'Hill Chart Contour': 0,
            '2D Curve Slices': 0,
            '2D Curve Slices - const.blade': 0,
            'Best efficiency point summary': 0
        }
        output_suboptions = {
            'Hill Chart Contour': {'Hide Blade Angle Lines': 0},
            '2D Curve Slices - const.blade': {'Const. Head': 1, 'Const. n': 1, 'Const. efficiency': 1}
        }
        settings_options = {
            'Normalize': 0,
            'Save Chart Data': 0
        }

        self.processor.set_output_parameters(output_options, output_suboptions, settings_options)  
    

    

    """
    Development mode methods end here
    """

    

if __name__ == "__main__":
    processor = MainProcessor()
    