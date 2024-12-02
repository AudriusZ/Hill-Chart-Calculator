from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTreeWidgetItem,
    QFileDialog, QMessageBox, QWidget, QVBoxLayout,
    QTabWidget, QTreeWidget
    )
from turbine_simulator_gui import ( # Generated GUI files
    Ui_MainWindow,  
    Ui_FormManualAutomaticControl
    )
from HillChartProcessor import HillChartProcessor  # Processing logic
from control_processor import ControlProcessor
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
    def __init__(
            self,
            parent=None,
            H_t=2.15,
            H_t_rate = 1/600,
            Q = 3.375,
            Q_rate = 0.5*3.375 /3600,
            blade_angle = 16.2,
            blade_angle_rate = 0.5,
            n = 113.5,
            n_rate = 1
            ):
        super().__init__(parent)
        self.ui = Ui_FormManualAutomaticControl()  # Use the generated UI
        self.ui.setupUi(self)  # Set up the UI on this QWidget

        # Connect the activate checkbox to toggle input fields
        self.ui.checkBox.stateChanged.connect(self.toggle_inputs)


        # Set default value for H_t
        self.ui.lineEdit_H_t.setText(f"{H_t:.2f}")
        self.ui.lineEdit_H_t_rate.setText(f"{H_t_rate:.4f}")
        self.ui.lineEdit_Q.setText(f"{Q:.3f}")
        self.ui.lineEdit_Q_rate.setText(f"{Q_rate:.4f}")
        self.ui.lineEdit_blade_angle.setText(f"{blade_angle:.1f}")
        self.ui.lineEdit_blade_angle_rate.setText(f"{blade_angle_rate:.1f}")
        self.ui.lineEdit_n.setText(f"{n:.1f}")
        self.ui.lineEdit_n_rate.setText(f"{n_rate:.1f}")    

    def toggle_inputs(self, checked):
        """
        Enable or disable blade_angle, blade_angle_rate, n, and n_rate inputs
        based on the state of the 'Activate' checkbox.

        Args:
            checked (bool): The state of the checkbox (True if checked, False otherwise).
        """
        # Disable or enable inputs based on the checkbox state
        self.ui.lineEdit_blade_angle.setDisabled(checked)
        self.ui.lineEdit_blade_angle_rate.setDisabled(checked)
        self.ui.lineEdit_n.setDisabled(checked)
        self.ui.lineEdit_n_rate.setDisabled(checked)
        print(f"Checkbox state changed. Checked: {checked}")

        
    def get_input_value(self, field_name):
        """
        Get the value from a specified input field dynamically.

        Args:
            field_name (str): The name of the variable to fetch (e.g., 'H_t', 'Q').

        Returns:
            float: The entered value if valid, otherwise None.
        """
        try:
            # Dynamically get the corresponding QLineEdit widget
            field = getattr(self.ui, f"lineEdit_{field_name}")
            return float(field.text())
        except (AttributeError, ValueError):
            # Return None for invalid input or missing fields
            return None
        
    def get_all_input_values(self):
        """
        Get all input values from the form dynamically.

        Returns:
            dict: A dictionary containing all the input field values.
        """
        # Define the list of field names corresponding to the lineEdit widgets
        fields = [
            "H_t", "H_t_rate", "Q", "Q_rate", 
            "blade_angle", "blade_angle_rate", 
            "n", "n_rate"
        ]

        # Dynamically fetch and validate values for all fields
        values = {}
        for field in fields:
            value = self.get_input_value(field)
            if value is None:
                raise ValueError(f"Invalid value entered for {field}. Please enter a numeric value.")
            values[field] = value

        return values



        
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
        self.current_Q = None  # Current value of Q
        self.target_Q = None   # Target value of Q
        self.Q_rate = None     # Rate of change for Q

        self.current_H_t = None  # Current value of H_t
        self.target_H_t = None   # Target value of H_t
        self.H_t_rate = None     # Rate of change for H_t

        self.current_blade_angle = None  # Current blade angle
        self.target_blade_angle = None   # Target blade angle
        self.blade_angle_rate = None     # Rate of change for blade angle

        self.current_n = None  # Current rotational speed
        self.target_n = None   # Target rotational speed
        self.n_rate = None     # Rate of change for rotational speed


        # Load the GUI design
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Initialize the processor
        self.processor = HillChartProcessor()
        self.turbine_processor = ControlProcessor()

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
            self.update_status(f"***Developer mode: Run control in default after double-clicking '{action}'.")            
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


    def update_status(self, message):
        """Update the status box in the GUI."""
        self.ui.plainTextEdit.appendPlainText(message)

    def open_control_widget(self):
        """
        Open the Manual/Automatic Control widget.
        """
        if not hasattr(self, "control_widget"):
            # Create the widget with a default H_t value
            self.control_widget = ManualAutomaticControlWidget()
            
            # Connect the lineEdit_H_t text change to dynamically update H_t in control_processor
            #self.control_widget.ui.lineEdit_H_t.textChanged.connect(self.update_h_target)

            # Connect the "Apply" button to fetch values only when clicked
            self.control_widget.ui.pushButtonApply.clicked.connect(self.apply_changes)

        self.control_widget.show()

    def apply_changes(self):
        """
        Apply the changes when the 'Apply' button is clicked.
        """
        try:
            # Fetch the value of H_t entered in the GUI
            #H_t = self.control_widget.get_h_target()
            H_t = self.control_widget.get_input_value("H_t")
            H_t_rate = self.control_widget.get_input_value("H_t_rate")
            Q = self.control_widget.get_input_value("Q")
            Q_rate = self.control_widget.get_input_value("Q_rate")
            blade_angle = self.control_widget.get_input_value("blade_angle")

            # Set the target Q and Q_rate
            self.target_Q = Q
            self.Q_rate = Q_rate
            
            self.target_H_t = H_t   # Target value of H_t
            self.H_t_rate = H_t_rate     # Rate of change for H_t        

            if H_t is None:
                raise ValueError("Invalid H_t value entered. Please enter a numeric value.")
            
            # Process the H_t value (e.g., update control logic)
            self.control_processor(H_t=H_t, Q=Q)

            # Optionally, update the GUI status
            self.update_status(f"Applied changes: H_t={H_t}, Q target={Q}, Q_rate={Q_rate}")
        except Exception as e:
            QMessageBox.warning(self, "Invalid Input", str(e))
            self.update_status(f"Error applying changes: {str(e)}")

    
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

    

    
    def control_processor(self, H_t=None, Q=None, blade_angle=None):
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

            initial_blade_angle = 16.2
            initial_n = 113.5
            initial_Q = self.turbine_processor.Q_function(self.turbine_processor.elapsed_physical_time)

            self.turbine_processor.simulator.set_operation_attribute("Q", initial_Q)
            self.turbine_processor.simulator.set_operation_attribute("blade_angle", initial_blade_angle)
            self.turbine_processor.simulator.set_operation_attribute("n", initial_n)
            self.turbine_processor.simulator.set_operation_attribute("D", D)
            self.turbine_processor.compute_outputs()

        print("Starting simulation loop...")        

        # Use the stored axs and canvas
        axs = getattr(self, "plot_axs", None)
        canvas = getattr(self, "plot_canvas", None)

        if axs is None or canvas is None:
            raise RuntimeError("Simulation plots are not properly initialized.")

        # Continuous simulation loop
        while True:
            # Fetch the latest H_t value
            
            if H_t is None:
                #H_t = self.control_widget.get_input_value("H_t")
                self.current_H_t = self.control_widget.get_input_value("H_t")
                self.current_Q = self.control_widget.get_input_value("Q")
                

            if H_t is None:
                print("Invalid H_t value. Using default.")
                H_t = 2.15
            
            
            # Gradually adjust Q toward the target Q
            if self.current_Q is None:
                self.current_Q = self.target_Q  # Initialize current_Q
                self.current_H_t = self.target_H_t

            if self.target_Q is not None and self.current_Q != self.target_Q:
                # Compute the incremental change
                delta_Q = self.Q_rate * self.turbine_processor.refresh_rate_physical
                if self.current_Q < self.target_Q:
                    self.current_Q = min(self.current_Q + delta_Q, self.target_Q)
                elif self.current_Q > self.target_Q:
                    self.current_Q = max(self.current_Q - delta_Q, self.target_Q)

            if self.target_H_t is not None and self.current_H_t != self.target_H_t:
                # Compute the incremental change
                delta_H_t = self.H_t_rate * self.turbine_processor.refresh_rate_physical
                if self.current_H_t < self.target_H_t:
                    self.current_H_t = min(self.current_H_t + delta_H_t, self.target_H_t)
                elif self.current_Q > self.target_Q:
                    self.current_H_t = max(self.current_H_t - delta_H_t, self.target_H_t)
            
            # Call the update_simulation method
            #self.turbine_processor.update_simulation(H_t, Q, axs, log_callback=self.update_status)
            self.turbine_processor.update_simulation(self.current_H_t, self.current_Q, self.plot_axs, log_callback=self.update_status)
            
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




    """
    Development mode methods start here
    """

    def turbine_hydraulics_action(self):
        """
        Generate and embed the 3D Hill Chart into a new tab.
        """
        try:
            # Set default turbine and plot parameters
            self.default_turbine_parameters()
            self.default_plot_parameters()
            self.default_output_parameters()

            # Generate the outputs and get the processed data
            result = self.processor.generate_outputs(show_standalone=False)

            # Unpack the result (includes fig if embedded)
            self.BEP_data, self.hill_values, _, fig = result            

            # Embed the plot in a new tab using PlotManager
            self.plot_manager.embed_plot(fig, "3D Hill Chart")

            # Update status
            # self.update_status("3D Hill Chart embedded in a new tab.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            self.update_status(f"Error during Turbine Hydraulics action: {str(e)}")
      

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

    



    

    def run_test_steps(self):
        """Run the same steps as in testHillChartProcessor when ButtonDev is clicked."""
        try:
            self.turbine_hydraulics_action()
            self.control_processor()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            self.update_status(f"Error during test steps: {str(e)}")

    """
    Development mode methods end here
    """


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()    
    window.update_status("Program has started successfylly.")
    window.show()
    #window.run_test_steps()
    sys.exit(app.exec())


