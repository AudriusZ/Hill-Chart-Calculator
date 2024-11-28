from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTreeWidgetItem,
    QFileDialog, QMessageBox, QWidget, QVBoxLayout,
    QTabWidget, QTreeWidget
    )
from turbine_simulator_gui import ( # Generated GUI files
    Ui_MainWindow,  
    Ui_Form
    )
from HillChartProcessor import HillChartProcessor  # Processing logic
from TurbineControlProcessor import TurbineControlProcessor
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget



"""
Widget Classes Start here
"""

class ManualAutomaticControlWidget(QWidget):
    """
    Wrapper class for the Manual/Automatic Control widget.
    """
    def __init__(self, parent=None, default_h_target=2.15):
        super().__init__(parent)
        self.ui = Ui_Form()  # Use the generated UI
        self.ui.setupUi(self)  # Set up the UI on this QWidget

        # Set default value for H_t
        self.ui.lineEdit.setText(str(default_h_target))

    def get_h_target(self):
        """
        Get the head target (H_t) value entered in the lineEdit.
        Returns:
            float: The entered value, or None if invalid.
        """
        try:
            return float(self.ui.lineEdit.text())
        except ValueError:
            return None

        
"""
Widget Classes End here
"""




class PlotManager:
    def __init__(self, tab_widget: QTabWidget):
        """
        Initialize the PlotManager.
        Args:
            tab_widget (QTabWidget): The QTabWidget to manage.
        """
        self.tab_widget = tab_widget

    def embed_plot(self, fig, tab_name: str):
        """
        Embed a matplotlib figure into a new tab.
        Args:
            fig (matplotlib.figure.Figure): The matplotlib figure to embed.
            tab_name (str): The name of the new tab.
        Returns:
            FigureCanvas: The canvas object for the embedded plot.
        """
        canvas = FigureCanvas(fig)
        new_tab = QWidget()
        layout = QVBoxLayout(new_tab)
        layout.addWidget(canvas)
        self.tab_widget.addTab(new_tab, tab_name)
        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)
        return canvas  # Return the canvas for further updates
    
    def expand_tree(self, tree_widget: QTreeWidget):
        """
        Expands all items in a QTreeWidget.
        Args:
            tree_widget (QTreeWidget): The tree widget to expand.
        """
        tree_widget.expandAll()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the GUI design
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Initialize the processor
        self.processor = HillChartProcessor()
        self.turbine_processor = TurbineControlProcessor()

        # Initialize the PlotManager with the QTabWidget
        self.plot_manager = PlotManager(self.ui.tabWidget)

        # Expand the tree widget using PlotManager
        self.plot_manager.expand_tree(self.ui.treeWidget)

        # Connect tree double-clicks to an action handler
        self.ui.treeWidget.itemDoubleClicked.connect(self.tree_item_double_clicked)

        # Initialize simulation state
        self.simulation_initialized = False

        

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
            self.open_control_widget()  # Open the widget            
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

    def open_control_widget(self):
        """
        Open the Manual/Automatic Control widget.
        """
        if not hasattr(self, "control_widget"):
            # Create the widget with a default H_t value
            self.control_widget = ManualAutomaticControlWidget(default_h_target=2.15)
            
            # Connect the lineEdit text change to dynamically update H_t in control_processor
            self.control_widget.ui.lineEdit.textChanged.connect(self.update_h_target)

        self.control_widget.show()

    def update_h_target(self, value):
        """
        Update the H_t value in the control_processor dynamically.
        Args:
            value (str): The new H_t value entered in the widget.
        """
        try:
            H_t = float(value)
            self.control_processor(H_t=H_t)
        except ValueError:
            # Ignore invalid input (e.g., empty or non-numeric)
            print(f"Invalid H_t value: {value}")

    
    def control_processor(self, H_t=None):
        """
        Run the simulation loop, dynamically adapting to live updates of H_t.
        Args:
            H_t (float): The head target value. If None, the current value is fetched.
        """
        # Ensure the simulation is initialized
        if not self.simulation_initialized:
            print("Initializing simulation...")
            self.simulation_initialized = True

            # Set up the simulation
            fig, axs = self.turbine_processor.initialize_plot()
            canvas = self.plot_manager.embed_plot(fig, "Simulation Results")

            # Save axs and canvas as instance attributes
            self.plot_axs = axs
            self.plot_canvas = canvas

            # Set up initial simulation state
            self.turbine_processor.simulator.get_data(self.hill_values.data)
            self.turbine_processor.simulator.get_BEP_data(self.BEP_data)
            D = self.BEP_data.D
            self.turbine_processor.start_time = 0
            self.turbine_processor.max_duration = self.turbine_processor.start_time + 4 * 3600  # 4 hours
            self.turbine_processor.elapsed_physical_time = self.turbine_processor.start_time

            initial_blade_angle = 11.7
            initial_n = 113.5
            initial_Q = self.turbine_processor.Q_function(self.turbine_processor.elapsed_physical_time)

            self.turbine_processor.simulator.set_operation_attribute("Q", initial_Q)
            self.turbine_processor.simulator.set_operation_attribute("blade_angle", initial_blade_angle)
            self.turbine_processor.simulator.set_operation_attribute("n", initial_n)
            self.turbine_processor.simulator.set_operation_attribute("D", D)
            self.turbine_processor.compute_outputs()

        print("Starting simulation loop...")
        head_control_active = True

        # Use the stored axs and canvas
        axs = getattr(self, "plot_axs", None)
        canvas = getattr(self, "plot_canvas", None)

        if axs is None or canvas is None:
            raise RuntimeError("Simulation plots are not properly initialized.")

        # Continuous simulation loop
        while True:
            # Fetch the latest H_t value
            if H_t is None:
                H_t = self.control_widget.get_h_target() if hasattr(self, "control_widget") else 2.15
            if H_t is None:
                print("Invalid H_t value. Using default.")
                H_t = 2.15

            # Call the update_simulation method
            self.turbine_processor.update_simulation(H_t, head_control_active, axs)

            # Increment the simulation time
            self.turbine_processor.elapsed_physical_time += self.turbine_processor.refresh_rate_physical
            if self.turbine_processor.elapsed_physical_time > self.turbine_processor.max_duration:
                print("Simulation complete.")
                break

            # Redraw the canvas and process UI events
            canvas.draw()
            QtWidgets.QApplication.processEvents()

            # Optional: Control loop speed (adjust for smoothness)
            #QtCore.QThread.msleep(100)



    

    def run_test_steps(self):
        """Run the same steps as in testHillChartProcessor when ButtonDev is clicked."""
        try:
            self.turbine_hydraulics_action()
            self.control_processor()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            self.update_status(f"Error during test steps: {str(e)}")


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()    
    window.update_status("Program has started successfylly.")
    window.show()
    #window.run_test_steps()
    sys.exit(app.exec())


