from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem, QFileDialog, QMessageBox
from turbine_simulator_gui import Ui_MainWindow  # Generated GUI file
from HillChartProcessor import HillChartProcessor  # Processing logic
from TurbineControlProcessor import TurbineControlProcessor
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas



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
        
        if action == "Turbine Hydraulics":
            self.update_status(f"***Developer mode: Set default turbine hydraulics after double-clicking '{action}'.")
            self.turbine_hydraulics_action()
        elif action == "Load Data":
            self.load_data_action()
        elif action == "Manual/Automatic Control":
            self.update_status(f"***Developer mode: Run control in defaukt after double-clicking '{action}'.")
            self.control_processor()            
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




    """Development mode methods start here"""

    def turbine_hydraulics_action(self):
        """Run the same steps as in testHillChartProcessor when ButtonDev is clicked."""
        try:
            self.default_turbine_parameters()
            self.default_plot_parameters()
            self.default_output_parameters()
            self.BEP_data, self.hill_values, _ = self.processor.generate_outputs()                        

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            self.update_status(f"Error during test steps: {str(e)}")        

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

    def update_status(self, message):
        """Update the status box in the GUI."""
        self.ui.plainTextEdit.appendPlainText(message)

    def control_processor(self):
        #Parameters
        
        initial_blade_angle = 11.7
        initial_n = 113.5
        H_t = 2.15  # Desired head
        head_control_active = True  # Enable head control


        
        # Initialize processor and load data        
        
        self.turbine_processor.simulator.get_data(self.hill_values.data)
        self.turbine_processor.simulator.get_BEP_data(self.BEP_data)

        D = self.BEP_data.D
        
        self.turbine_processor.start_time = 0
        self.turbine_processor.max_duration = self.turbine_processor.start_time + 4*3600  # 4 hours
        self.turbine_processor.elapsed_physical_time = self.turbine_processor.start_time
        self.turbine_processor.previous_time = self.turbine_processor.start_time  # For delta_time calculation        

        # Define initial simulation inputs
        initial_Q = self.turbine_processor.Q_function(self.turbine_processor.elapsed_physical_time)        

        self.turbine_processor.simulator.set_operation_attribute("Q", initial_Q)
        self.turbine_processor.simulator.set_operation_attribute("blade_angle", initial_blade_angle)
        self.turbine_processor.simulator.set_operation_attribute("n", initial_n)
        self.turbine_processor.simulator.set_operation_attribute("D", D)
        self.turbine_processor.compute_outputs()
        
        

        # Initialize plots
        fig, axs = self.turbine_processor.initialize_plot()

        # Embed the figure into a new tab
        canvas = FigureCanvas(fig)
        new_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(new_tab)
        layout.addWidget(canvas)
        self.ui.tabWidget.addTab(new_tab, "Simulation Results")

        # Activate the new tab
        self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.count() - 1)
        
        # Simulation loop
        
        try:
            while True:
                # Call the update_simulation method for each frame
                self.turbine_processor.update_simulation(H_t, head_control_active, axs)

                self.turbine_processor.elapsed_physical_time += self.turbine_processor.refresh_rate_physical
                if self.turbine_processor.elapsed_physical_time > self.turbine_processor.max_duration:
                    pass
                
                canvas.draw()  # Redraw the embedded canvas
                QtWidgets.QApplication.processEvents()  # Process PyQt events


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
    #window.run_test_steps()
    window.update_status("Program has started successfylly.")
    window.show()
    sys.exit(app.exec())
