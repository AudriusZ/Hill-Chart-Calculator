#pyinstaller --onefile --name Turbine_Simulator_0.1.1 --icon=icon.ico turbine_simulator_main.py


from main_processor import MainProcessor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTreeWidgetItem,
    QMessageBox, QWidget, QVBoxLayout,
    QTabWidget, QTreeWidget, QFileDialog
    )
from turbine_simulator_gui import ( # Generated GUI files
    Ui_MainWindow,  
    Ui_FormManualAutomaticControl
    )

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

        self.setWindowTitle("Manual/Automatic Control")

        # Connect the activate checkbox to toggle input fields
        self.ui.checkBox.stateChanged.connect(self.toggle_inputs)
        self.ui.checkBox_2.stateChanged.connect(self.toggle_inputs)

        # Store initial checkbox state for comparison later
        self._checkbox_state = self.ui.checkBox.isChecked()
        self._checkbox_state = self.ui.checkBox_2.isChecked()

        checked = self._checkbox_state

        self.ui.lineEdit_H_t.setEnabled(checked)
        self.ui.lineEdit_H_t_rate.setEnabled(checked)

        # Define styles for enabled and disabled labels
        gray_style = "color: gray;"
        normal_style = "color: black;"

        self.ui.lineEdit_H_t.setStyleSheet(normal_style if checked else gray_style)
        self.ui.lineEdit_H_t_rate.setStyleSheet(normal_style if checked else gray_style)        

        # Set default value for H_t
        self.ui.lineEdit_H_t.setText(f"{H_t:.2f}")
        self.ui.lineEdit_H_t_rate.setText(f"{H_t_rate:.4f}")
        self.ui.lineEdit_Q.setText(f"{Q:.3f}")
        self.ui.lineEdit_Q_rate.setText(f"{Q_rate:.4f}")
        self.ui.lineEdit_blade_angle.setText(f"{blade_angle:.1f}")
        self.ui.lineEdit_blade_angle_rate.setText(f"{blade_angle_rate:.1f}")
        self.ui.lineEdit_n.setText(f"{n:.1f}")
        self.ui.lineEdit_n_rate.setText(f"{n_rate:.1f}")    

        settings = {
            "Kp": 1.2,              # PID control coefficient for proportional control
            "Ki": 0.1,              # PID control coefficient for integral control
            "Kd": 0.05,             # PID control coefficient for derivative control
            "H_tolerance": 0.05,    # Tolerance for head control
            "n_min": 30,            # Minimum rotational speed limit
            "n_max": 150,           # Maximum rotational speed limit
            "blade_angle_min": 3,   # Minimum blade angle
            "blade_angle_max": 26   # Maximum blade angle
        }

        # Set default value for H_t
        self.ui.lineEdit_n_min.setText(f"{30:.1f}")
        self.ui.lineEdit_n_max.setText(f"{150:.1f}")
        self.ui.lineEdit_blade_angle_min.setText(f"{3:.1f}")
        self.ui.lineEdit_blade_angle_max.setText(f"{26:.1f}")
        self.ui.lineEdit_Kp.setText(f"{1.2:.1f}")
        self.ui.lineEdit_Ki.setText(f"{0.1:.1f}")
        self.ui.lineEdit_Kd.setText(f"{0.05:.1f}")
            

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
        Get all input values from the form dynamically, including the checkbox state.

        Returns:
            dict: A dictionary containing all the input field values and the checkbox state.
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

        # Add the checkbox state to the dictionary
        values["head_control"] = self.ui.checkBox.isChecked()
        values["blade_angle_lock"] = self.ui.checkBox_2.isChecked()
        values["n_lock"] = False
        


        return values
    
    def get_all_settings_values(self):
        """
        Get all input values from the form dynamically, including the checkbox state.

        Returns:
            dict: A dictionary containing all the input field values and the checkbox state.
        """
        # Define the list of field names corresponding to the lineEdit widgets
        fields = [
            "n_min", "n_max", "blade_angle_min", "blade_angle_max", 
            "Kp", "Ki", "Kd"
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
        self.tab_widget.setTabsClosable(True)  # Enable the close button on tabs
        self.tab_widget.tabCloseRequested.connect(self.close_tab)  # Connect to the tab close signal

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
    
    def close_tab(self, index):
        """
        Handle closing of a tab.
        Args:
            index (int): The index of the tab to close.
        """
        self.tab_widget.removeTab(index)
    
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

        # Initialize main processor
        self.main_processor = MainProcessor()
        self.main_processor.set_message_callback(self.update_status)  # Set the callback for messages
        self.main_processor.standalone_figures = False

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
                    self.maximise_output_action()                   
                else:
                    self.update_status(f"Must set 'Turbine Hydraulics' first.")

            elif action == "Manual/Automatic Control":
                if self.app_state.actions.get("Turbine Hydraulics", False):
                    self.manual_automatic_control_action()                    
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


    def turbine_hydraulics_action(self):
        """
        Generate and embed the 3D Hill Chart into a new tab.
        """
        try:
            fig = self.main_processor.default_turbine_hydraulics_action()            
            self.plot_manager.embed_plot(fig, "3D Hill Chart")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            self.update_status(f"Error during Turbine Hydraulics action: {str(e)}")
    
    def load_data_action(self):
        """Handle the 'Load Data' action."""
        
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Turbine Data File", "", "CSV Files (*.csv)")
        if file_path:            
            self.main_processor.processor.get_file_path(file_path)
            self.update_status(f"Loaded data from: {file_path}")
        else:
            QMessageBox.warning(self, "No File Selected", "Please select a valid file.")    
        

    def maximise_output_action(self):
        plots = self.main_processor.maximise_output_action()

        # Embed each plot in a new tab
        for title, fig in plots.items():
            self.plot_manager.embed_plot(fig, title)
    
    def manual_automatic_control_action(self):
        """
        Handle manual/automatic control by initializing and running the simulation.
        """
        self.open_control_widget()  # Open the widget
        control_parameters, control_settings = self.initialize_simulation_and_plots()        
        
        self.main_processor.control_processor.continue_simulation = False
        
        
    
    def initialize_simulation_and_plots(self):
        """
        Initialize the simulation and set up plots.
        """
        try:
            # Fetch control parameters from the GUI
            control_parameters = self.control_widget.get_all_input_values()
            control_settings = self.control_widget.get_all_settings_values()

            # Initialize the simulation
            self.main_processor.initialize_simulation()

            # Initialize the plots
            fig, axs = self.main_processor.control_processor.initialize_plot()
            self.plot_axs = axs
            canvas = self.plot_manager.embed_plot(fig, "Simulation Results")
            self.plot_canvas = canvas

            # Update the app state
            self.app_state.simulation_initialized = True

            # Log the status
            self.update_status("Press Start to Run Simulation.")

            return control_parameters, control_settings  # Return the parameters for further use if needed
        except Exception as e:
            self.update_status(f"Error during simulation initialization: {str(e)}")
            raise
    
    def start_control(self):
        self.main_processor.control_processor.continue_simulation = True
        control_parameters = self.control_widget.get_all_input_values()
        self.manage_control_simulation(control_parameters)        


    def stop_control(self):
        self.main_processor.control_processor.continue_simulation = False

    def apply_control_parameter_changes(self):
        """
        Apply changes when the 'Apply' button is pressed.
        """
        try:
            # Fetch other input values from the GUI
            control_parameters = self.control_widget.get_all_input_values()            

            # Apply the control parameters to the simulation
            self.manage_control_simulation(control_parameters)
            
        except Exception as e:
            QMessageBox.warning(self, "Invalid Input", str(e))
            self.update_status(f"Error applying changes: {str(e)}")

    def apply_control_settings_changes(self):
        """
        Apply changes when the 'Apply' button is pressed.
        """
        try:
            # Fetch other input values from the GUI            
            control_settings = self.control_widget.get_all_settings_values()

            # Apply the control parameters to the simulation
            self.main_processor.control_processor.update_control_settings(control_settings)
            
            tunings = (control_settings["Kp"], control_settings["Ki"], control_settings["Kd"])
            self.main_processor.control_processor.controller.pid.tunings =tunings
            
            
        except Exception as e:
            QMessageBox.warning(self, "Invalid Input", str(e))
            self.update_status(f"Error applying changes: {str(e)}")
        
    def manage_control_simulation(self, control_parameters):
        """
        Run the simulation loop, dynamically adapting to live updates of control parameters.
        Args:
            control_parameters (dict): Parameters for the simulation. If None, initializes simulation.
        """
        try:
            # Use ControlProcessor to run the simulation
            self.main_processor.run_simulation(
                control_parameters,                
                axs=self.plot_axs,  # Pass the plot axes
                log_callback=self.update_status
            )

            # Finalize
            #self.update_status("Stopped. Press Start to Continue")            
        except RuntimeError as e:
            self.update_status(f"Error during simulation: {str(e)}")
            print(f"Error: {e}")

    

    def open_control_widget(self):
        """
        Open the Manual/Automatic Control widget.
        """
        if not hasattr(self, "control_widget"):
            # Create the widget with a default H_t value
            data = self.main_processor.BEP_data            
            self.control_widget = ManualAutomaticControlWidget(                
                H_t= data.H[0],
                Q=data.Q[0],
                n = data.n[0],
                blade_angle= data.blade_angle[0]
                )            
            
            # Connect the "Apply" button to fetch values only when clicked
            self.control_widget.ui.pushButtonApply.clicked.connect(self.apply_control_parameter_changes)
            self.control_widget.ui.pushButtonApply_2.clicked.connect(self.apply_control_settings_changes)
            self.control_widget.ui.pushButtonStart.clicked.connect(self.start_control)
            self.control_widget.ui.pushButtonStop.clicked.connect(self.stop_control)

        self.control_widget.show()

    


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

    def update_status(self, message):
        """Update the status box in the GUI."""
        self.ui.plainTextEdit.appendPlainText(message)

    

         




    


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()    
    #window.update_status("Program has started successfylly.")
    #window.update_status(f"***Developer mode: Set default turbine hydraulics after double-clicking '{action}'.")
    #window.turbine_hydraulics_action()
    window.app_state.update_actions("Turbine Hydraulics", True)
    window.show()    
    sys.exit(app.exec())


