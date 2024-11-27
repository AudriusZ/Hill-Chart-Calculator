from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem, QFileDialog, QMessageBox
from turbine_simulator_gui import Ui_MainWindow  # Generated GUI file
from HillChartProcessor import HillChartProcessor  # Processing logic
from TurbineControlProcessor import TurbineControlProcessor
import os
import matplotlib.pyplot as plt



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the GUI design
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Initialize the processor
        self.processor = HillChartProcessor()
        self.turbine_processor = TurbineControlProcessor()

        # Connect tree double-clicks to an action handler
        self.ui.treeWidget.itemDoubleClicked.connect(self.tree_item_double_clicked)

        # Connect ButtonDev to perform test steps
        self.ui.ButtonDev.clicked.connect(self.run_test_steps)

    def tree_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle tree item double-click actions."""
        action = item.text(0)  # Get the text of the clicked item
        if action == "Load Data":
            self.load_data_action()
        else:
            self.update_status(f"No action defined for '{action}'.")

    def load_data_action(self):
        """Handle the 'Load Data' action."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Turbine Data File", "", "CSV Files (*.csv)")
        if file_path:
            self.processor.get_file_path(file_path)
            self.update_status(f"Loaded data from: {file_path}")
        else:
            QMessageBox.warning(self, "No File Selected", "Please select a valid file.")

    

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
        extrapolation_values_n11 = [10, 170, 10]
        extrapolation_values_blade_angles = [2, 26.1, 10]

        self.processor.get_plot_parameters(n_contours, extrapolation_options_vars, extrapolation_values_n11, extrapolation_values_blade_angles, min_efficiency_limit=min_efficiency_limit)

    def default_output_parameters(self):
        """Set default output parameters as in the test."""
        output_options = {
            '3D Hill Chart': 1,
            'Hill Chart Contour': 1,
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

    def update_status(self, message):
        """Update the status box in the GUI."""
        self.ui.plainTextEdit.appendPlainText(message)

    def control_processor(self):
        # Initialize processor and load data
        processor = TurbineControlProcessor()
        processor.load_data("Mogu_D1.65m.csv")        
        processor.simulator.get_data(self.hill_values.data)
        #processor.simulator.get_BEP_data(self.BEP_data)

        D = self.BEP_data.D

        
        processor.start_time = 0
        processor.max_duration = processor.start_time + 4*3600  # 4 hours
        processor.elapsed_physical_time = processor.start_time
        processor.previous_time = processor.start_time  # For delta_time calculation

        initial_blade_angle = 11.7
        initial_n = 113.5

        # Define initial simulation inputs
        initial_Q = processor.Q_function(processor.elapsed_physical_time)

        

        processor.simulator.set_operation_attribute("Q", initial_Q)
        processor.simulator.set_operation_attribute("blade_angle", initial_blade_angle)
        processor.simulator.set_operation_attribute("n", initial_n)
        processor.simulator.set_operation_attribute("D", D)
        processor.compute_outputs()
        
        H_t = 2.15  # Desired head
        head_control_active = True  # Enable head control

        # Initialize plots
        fig, axs = processor.initialize_plot()

        # Simulation loop
        
        try:
            while True:
                # Call the update_simulation method for each frame
                processor.update_simulation(H_t, head_control_active, axs)

                processor.elapsed_physical_time += processor.refresh_rate_physical
                if processor.elapsed_physical_time > processor.max_duration:
                    pass
                
                plt.pause(processor.refresh_rate_physical / processor.time_scale_factor)

        except KeyboardInterrupt:
            print("Simulation stopped by user.")
        finally:
            # Ensure the plot is shown when the simulation ends      
            plt.show()

    

    def run_test_steps(self):
        """Run the same steps as in testHillChartProcessor when ButtonDev is clicked."""
        try:
            self.default_turbine_parameters()
            self.default_plot_parameters()
            self.default_output_parameters()
            self.BEP_data, self.hill_values, _ = self.processor.generate_outputs()            
            #self.BEP_data, self.hill_values, self.Raw_data = self.processor.prepare_core_data()
            
            

            self.control_processor()
            


        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            self.update_status(f"Error during test steps: {str(e)}")


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.run_test_steps()
    #window.update_status("Program Started.")
    #window.show()
    sys.exit(app.exec())
