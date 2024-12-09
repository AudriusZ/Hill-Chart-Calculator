from PyQt6.QtWidgets import (QFileDialog, QMessageBox)

from HillChartProcessor import HillChartProcessor  # Processing logic
from control_processor import ControlProcessor
from maximised_output_processor import MaximisedOutputProcessor

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

    def set_message_callback(self, callback):
        """
        Set a callback function for handling messages.
        """
        self.message_callback = callback


    def emit_message(self, message):
        """
        Emit a message using the callback if provided, or print to console.
        """
        if self.message_callback:
            self.message_callback(message)
        else:
            print(message)  # Default behavior for standalone mode

    def get_bep_data(self):
        """
        Retrieve BEP data for initializing the control widget.
        Returns:
            BEP data
        """
        if not self.BEP_data:
            raise ValueError("BEP data is not initialized. Run 'default_turbine_hydraulics_action' first.")
        
        # Return the relevant BEP data
        return self.BEP_data  
    

    def maximise_output_action(self):        
        
        self.maximised_output_processor.maximised_output(self.hill_values.data, self.BEP_data)                
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
            self.default_turbine_parameters()
            self.default_plot_parameters()
            self.default_output_parameters()

            # Generate the outputs and get the processed data
            result = self.processor.generate_outputs(show_standalone=self.standalone_figures)

            # Unpack the result (includes fig if embedded)
            self.BEP_data, self.hill_values, _, fig = result                

            self.emit_message("3D Hill Chart generated successfully.")
            return fig  # Return the result, including 'fig'            
            
        except Exception as e:
            self.emit_message(f"Error during Turbine Hydraulics action: {str(e)}")
            raise  

    def default_turbine_parameters(self):
        """Set default turbine parameters as in the test."""
        datapath = os.path.join(os.path.dirname(__file__), 'Mogu_D1.65m.csv')  # Adjust path as needed
        selected_values = [1, 4]  # 1 - H, 2 - Q, 3 - n, 4 - D
        var1 = 2.15
        var2 = 1.65

        self.processor.get_file_path(datapath)
        self.processor.get_turbine_parameters(selected_values, var1, var2)

    def default_plot_parameters(self):
        """Set default plot parameters as in the test."""
        
        min_efficiency_limit = 0.1
        n_contours = 25        
        extrapolation_options_vars = [1, 1]
        extrapolation_values_n11 = [10, 200, 10]
        extrapolation_values_blade_angles = [2, 26.1, 10]

        self.processor.get_plot_parameters(n_contours, extrapolation_options_vars, extrapolation_values_n11, extrapolation_values_blade_angles, min_efficiency_limit=min_efficiency_limit)

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

        self.processor.get_output_parameters(output_options, output_suboptions, settings_options)  
    

    

    """
    Development mode methods end here
    """

    

if __name__ == "__main__":
    processor = MainProcessor()
    