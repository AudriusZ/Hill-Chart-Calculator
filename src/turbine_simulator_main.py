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


class AppState:
    def __init__(self, actions_list=None):
        """
        Initialize the actions with default states.
        
        Args:
            actions_list (list): A list of action names to initialize (default is an empty list).
        """
        # Initialize actions as False (not initiated)
        self.actions = {action: False for action in (actions_list or [])}
        
        # Track if the simulation has been initialized
        self.simulation_initialized = False

    def update_actions(self, action, state=False):
        """
        Update the state of a specific action.

        Args:
            action (str): The name of the action to update.
            state (bool): The state to set for the action (True for initiated).
        """
        if action in self.actions:
            self.actions[action] = state
        else:
            print(f"Warning: Action '{action}' not defined in AppState.")


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
            control_processor=None,
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

        self.setWindowTitle("Manual/Automatic Control")

        # Connect the activate checkbox to toggle input fields
        self.ui.checkBox.stateChanged.connect(self.toggle_inputs)

        # Store initial checkbox state for comparison later
        self._checkbox_state = self.ui.checkBox.isChecked()

        checked = self._checkbox_state

        self.ui.lineEdit_H_t.setEnabled(checked)
        self.ui.lineEdit_H_t_rate.setEnabled(checked)

        # Define styles for enabled and disabled labels
        gray_style = "color: gray;"
        normal_style = "color: black;"

        self.ui.lineEdit_H_t.setStyleSheet(normal_style if checked else gray_style)
        self.ui.lineEdit_H_t_rate.setStyleSheet(normal_style if checked else gray_style)

        self.control_processor = control_processor  # Pass ControlProcessor instance

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

        self.ui.lineEdit_H_t.setEnabled(checked)
        self.ui.lineEdit_H_t_rate.setEnabled(checked)      
        
        # Define styles for enabled and disabled labels
        gray_style = "color: gray;"
        normal_style = "color: black;"

        # Update QLabel styles based on the checkbox state
        self.ui.lineEdit_blade_angle.setStyleSheet(gray_style if checked else normal_style) 
        self.ui.lineEdit_blade_angle_rate.setStyleSheet(gray_style if checked else normal_style)
        self.ui.lineEdit_n.setStyleSheet(gray_style if checked else normal_style)
        self.ui.lineEdit_n_rate.setStyleSheet(gray_style if checked else normal_style)

        self.ui.lineEdit_H_t.setStyleSheet(normal_style if checked else gray_style)
        self.ui.lineEdit_H_t_rate.setStyleSheet(normal_style if checked else gray_style)
        

    def check_and_apply_checkbox(self):
        """
        Check if the checkbox state has changed, and if so, apply the changes.
        """
        current_state = self.ui.checkBox.isChecked()
        if current_state != self._checkbox_state:
            # Update stored checkbox state
            self._checkbox_state = current_state            

            # Update head control in the ControlProcessor
            if self.control_processor:
                self.control_processor.toggle_head_control(current_state)

            print(f"Checkbox state changed. Checked: {current_state}")

        
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

        # Load the GUI design
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("Turbine Simulator")


        # Initialize the processor
        self.processor = HillChartProcessor()
        self.control_processor = ControlProcessor()

        # Initialize the PlotManager with the QTabWidget
        self.plot_manager = PlotManager(self.ui.tabWidget)

        actions = self.get_tree_widget_actions()
        self.app_state = AppState(actions)
        
        # Expand the tree widget using PlotManager
        self.plot_manager.expand_tree(self.ui.treeWidget)

        # Connect tree double-clicks to an action handler
        self.ui.treeWidget.itemDoubleClicked.connect(self.tree_item_double_clicked)

        # Initialize simulation state
        self.simulation_initialized = False

    def get_tree_widget_actions(self):
        """
        Extract all actions from the QTreeWidget.

        Returns:
            list: A list of action names (text of tree items).
        """
        actions = []

        def traverse_tree(item):
            # Add the item's text to actions
            actions.append(item.text(0))
            # Recursively traverse child items
            for i in range(item.childCount()):
                traverse_tree(item.child(i))

        # Traverse top-level items in the QTreeWidget
        tree_widget = self.ui.treeWidget
        for i in range(tree_widget.topLevelItemCount()):
            traverse_tree(tree_widget.topLevelItem(i))

        return actions

        

    def tree_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle tree item double-click actions."""
        action = item.text(0)  # Get the text of the clicked item
        
        try:
            if action == "Turbine Hydraulics":
                self.update_status(f"***Developer mode: Set default turbine hydraulics after double-clicking '{action}'.")
                self.turbine_hydraulics_action()
            elif action == "Load Data":
                self.load_data_action()
            elif action == "Maximised Output":
                if self.app_state.actions.get("Turbine Hydraulics", False):

                    from maximised_output_processor import MaximisedOutputProcessor
                    maximised_output_processor = MaximisedOutputProcessor()
                    maximised_output_processor.maximised_output(self.hill_values.data, self.BEP_data)
                    # Add plots to tabs
                    plots = maximised_output_processor.generate_plots()

                    # Embed each plot in a new tab
                    for title, fig in plots.items():
                        self.plot_manager.embed_plot(fig, title)
                    
                    
                else:
                    self.update_status(f"Must set 'Turbine Hydraulics' first.")

            elif action == "Manual/Automatic Control":
                if self.app_state.actions.get("Turbine Hydraulics", False):
                    self.open_control_widget()  # Open the widget
                    self.manage_simulation()
                else:
                    self.update_status(f"Must set 'Turbine Hydraulics' first.")
            else:
                self.update_status(f"No action defined for '{action}'.")
            
            # If no exception occurred, mark the action as successful
            self.app_state.update_actions(action, True)

        except Exception as e:
            # Log the error and mark the action as failed
            self.update_status(f"Error handling action '{action}': {str(e)}")
            self.app_state.update_actions(action, False)


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
            data = self.BEP_data
            self.control_widget = ManualAutomaticControlWidget(
                control_processor=self.control_processor,
                H_t= data.H[0],
                Q=data.Q[0],
                n = data.n[0],
                blade_angle= data.blade_angle[0]
                )            
            
            # Connect the "Apply" button to fetch values only when clicked
            self.control_widget.ui.pushButtonApply.clicked.connect(self.apply_changes)

        self.control_widget.show()

    def apply_changes(self):
        """
        Apply changes when the 'Apply' button is pressed.
        """
        try:
            # Check and apply the checkbox state
            self.control_widget.check_and_apply_checkbox()

            # Fetch other input values from the GUI
            control_parameters = self.control_widget.get_all_input_values()

            # Apply the control parameters to the simulation
            self.manage_simulation(control_parameters)
            
        except Exception as e:
            QMessageBox.warning(self, "Invalid Input", str(e))
            self.update_status(f"Error applying changes: {str(e)}")

        
    def manage_simulation(self, control_parameters = {}):
        """
        Run the simulation loop, dynamically adapting to live updates of H_t.
        Args:
            H_t (float): The head target value. If None, the current value is fetched.
        """
        # Ensure the simulation is initialized

        

        if not control_parameters:        
            
            control_parameters = self.control_widget.get_all_input_values()

            # Initialize simulation
            self.control_processor.initialize_simulation(self.hill_values.data, self.BEP_data)

            # Initialize the plots
            fig, axs = self.control_processor.initialize_plot()
            self.plot_axs = axs
            canvas = self.plot_manager.embed_plot(fig, "Simulation Results")
            self.plot_canvas = canvas

            self.app_state.simulation_initialized = True

            self.update_status(f"Starting simulation loop.")

        
        

        # Use ControlProcessor to run the simulation
        
        try:
            self.control_processor.run_simulation(
                control_parameters,
                axs=self.plot_axs,  # Pass the plot axes
                log_callback=self.update_status
            )
        except RuntimeError as e:
            self.update_status(f"Error: {e}")
            print(f"Error: {e}")

        # Finalize
        self.update_status("Simulation complete.")
        print("Simulation complete.")






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

    



    

    def run_test_steps(self):
        """Run the same steps as in testHillChartProcessor when ButtonDev is clicked."""
        try:
            self.turbine_hydraulics_action()
            self.manage_simulation()

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
    sys.exit(app.exec())


