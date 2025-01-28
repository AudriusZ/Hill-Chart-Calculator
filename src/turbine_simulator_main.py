
#pyinstaller --onefile --name Turbine_Simulator_1.0.2 --icon=src/icon.ico --noconsole --add-data "src/logo.png;src/" src/turbine_simulator_main.py

from main_processor import MainProcessor

from turbine_simulator_gui import ( # Generated GUI files
    Ui_MainWindow
    )
from widget_processor import (
    SizingWidget,
    SurfaceFittingWidget,
    OutputOptionsHydraulicWidget,    
    MaximiseOutputWidget,
    ManualAutomaticControlWidget    
    )

from plot_manager import PlotManager

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTreeWidgetItem,
    QMessageBox,
    QFileDialog,
    QWidget
    )

from PyQt6.QtGui import QPixmap

import os



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






class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the GUI design
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("Turbine Simulator")

                # Determine the base path based on whether the app is bundled or not
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS  # PyInstaller sets this in bundled apps
        else:
            base_path = os.path.abspath(".")

        # Load the image from the bundled or source directory
        logo_path = os.path.join(base_path, "src/logo.png")
        self.ui.CoverImage.setPixmap(QPixmap(logo_path))
        self.ui.CoverImage.setScaledContents(True)  # Ensure the image scales to fit QLabel        

        # Initialize main processor
        self.main_processor = MainProcessor()
        self.main_processor.set_message_callback(self.update_status)  # Set the callback for messages
        self.main_processor.standalone_figures = False

        # Initialize the PlotManager with the QTabWidget
        self.plot_manager = PlotManager(self.ui.tabWidget)

        # Register specific cleanup actions for tabs
        self.plot_manager.register_tab_action("Simulation Results", self.cleanup_simulation_results)        

        actions = self.get_tree_widget_actions()
        self.app_state = AppState(actions)
        
        # Expand the tree widget using PlotManager
        self.plot_manager.expand_tree(self.ui.treeWidget)

        # Connect tree double-clicks to an action handler
        self.ui.treeWidget.itemDoubleClicked.connect(self.tree_item_double_clicked)

        # Initialize simulation state
        self.simulation_initialized = False

        self.update_status(f"Program has started successfully.") 

    

    def tree_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle tree item double-click actions."""
        action = item.text(0)  # Get the text of the clicked item
        
        try:
            if action == "Turbine Hydraulics":
                self.update_status(f"***Developer mode: Set default turbine hydraulics after double-clicking '{action}'.")
                self.turbine_hydraulics_action()

            elif action == "Load Data":
                self.load_data_action()                

            elif action == "Sizing":
                if self.app_state.actions.get("Load Data", False):
                    self.sizing_action()
                else:
                    self.update_status(f"Must 'Load Data' first.")

            elif action == "Surface Fit Settings":
                if self.app_state.actions.get("Sizing", False):
                    self.surface_fit_action()
                else:
                    self.update_status(f"Must set'Sizing' parameters first.")

            elif action == "Output Options (Hydraulics)":                
                if self.app_state.actions.get("Surface Fit Settings", False):                    
                    self.output_options_hydraulics_action()
                else:
                    self.update_status(f"Must set 'Surface Fit Settings' first.")                
                

            elif action == "Maximised Output":
                if self.app_state.actions.get("Turbine Hydraulics", False) or self.app_state.actions.get("Surface Fit Settings", False):
                    self.maximise_output_action()                   
                else:
                    self.update_status(f"Must set 'Turbine Hydraulics' or 'Surface Fit Settings' first.")

            elif action == "Manual/Automatic Control":
                if self.app_state.actions.get("Turbine Hydraulics", False) or self.app_state.actions.get("Surface Fit Settings", False):
                    self.manual_automatic_control_action()                    
                else:
                    self.update_status(f"Must set 'Turbine Hydraulics' or 'Surface Fit Settings' first.")
            
            elif action == "Output Options (Simulator)":
                self.update_status(f"***Action '{action}' triggered but no action defined.")
                #self.output_options_performance_action()

            elif action == "Turbine Loads":
                self.update_status(f"***Action '{action}' triggered but no action defined.")
                
            
            else:
                self.update_status(f"***No action defined for '{action}'.")            
            
            # If no exception occurred, mark the action as successful
            self.app_state.update_actions(action, True)

        except Exception as e:
            # Log the error and mark the action as failed
            self.update_status(f"Warning: '{action}': {str(e)}")
            self.app_state.update_actions(action, False)


    def turbine_hydraulics_action(self):
        """
        Generate and embed the 3D Hill Chart into a new tab.
        """
        try:
            fig = self.main_processor.default_turbine_hydraulics_action()            
            self.plot_manager.embed_plot(fig, "3D Hill Chart", add_export_button=True)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            self.update_status(f"Error during Turbine Hydraulics action: {str(e)}")
    
    def load_data_action(self):
        """Handle the 'Load Data' action."""
        
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Turbine Data File", "", "CSV Files (*.csv)")
        if file_path:            
            self.main_processor.set_file_path(file_path)
            self.update_status(f"Loaded data from: {file_path}")
        else:
            QMessageBox.warning(self, "No File Selected", "Please select a valid file.")
            raise ValueError("File selection cancelled by user.")  

    def sizing_action(self):
        """
        Select key parameters for turbine sizing
        """
        try:
            self.open_sizing_widget()

        except Exception as e:
            self.update_status(f"Error in sizing: {str(e)}")

    def surface_fit_action(self):
        """
        Select key parameters for data fitting
        """
        try:
            self.open_surface_fitting_widget()

        except Exception as e:
            self.update_status(f"Error in surface fitting: {str(e)}")

    def output_options_hydraulics_action(self):
        """
        Select what outputs to show
        """
        try:
            self.open_hydraulic_output_options_widget()

        except Exception as e:
            self.update_status(f"Error in output options: {str(e)}")

    def maximise_output_action(self):
        """
        Generate plots for maximised output and embed them into tabs with an export feature.
        """
        try:
            self.open_maximise_output_widget()  # Open the widget

        except Exception as e:
            self.update_status(f"Error in maximising output: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def manual_automatic_control_action(self):
        """
        Handle manual/automatic control by initializing and running the simulation.
        """
        self.open_control_widget()  # Open the widget
        self.initialize_simulation_and_plots()                
        self.main_processor.control_processor.continue_simulation = False

    def set_turbine_size_parameters(self):
        
        """
        Set turbine size
        """
        try:
            parameters = self.sizing_widget.get_all_input_values()
            text_widget = self.main_processor.set_turbine_size_parameters(parameters)
            self.plot_manager.embed_textEdit(text_widget, "Turbine Sizing")       
            self.update_status(f"Turbine sizing set.")     

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            self.update_status(f"Error during Turbine Sizing action: {str(e)}")

    

    def set_surface_fitting_parameters(self):        
        """
        Set suraface fitting parameters
        """
        try:
            parameters = self.surface_fitting_widget.get_all_input_values()
            fig = self.main_processor.set_surface_fitting_parameters(parameters)            
            self.plot_manager.embed_plot(fig, "3D Hill Chart", add_export_button=False)
            self.update_status(f"Surface fitting parameters set.") 

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            self.update_status(f"Error during Turbine Sizing action: {str(e)}")
    
    def set_output_options_hydraulic(self):
        """
        Set hydraulic output options to show
        """
        try:            
            #parameters = self.surface_fitting_widget.get_all_input_values()
            fig = self.main_processor.create_contour_plot()            
            #fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.1, wspace=0.3, hspace=1)
            self.plot_manager.embed_plot(fig[1], "Contour Plot", add_export_button=True)
            self.plot_manager.embed_plot(fig[2], "Contour Plot", add_export_button=True)

            '''
            fig = self.main_processor.create_plot_curve_slices()            
            fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.1, wspace=0.3, hspace=1)
            self.plot_manager.embed_plot(fig, "2D Slices", add_export_button=True)
            '''

            
            self.update_status(f"Output options set.") 

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            self.update_status(f"Error during Output options action: {str(e)}")


    def start_maximise_output(self):
        try:
            
            
            # Retrieve the plots from main_processor
            ranges = self.maximise_output_widget.get_all_input_values()            
            plots = self.main_processor.maximise_output_action(ranges)

            # Embed each plot in a new tab
            for title, fig in plots.items():
                self.plot_manager.embed_plot(fig, title, add_export_button=True)

        except Exception as e:
            self.update_status(f"Error in maximising output: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    
        
        
    
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
            canvas = self.plot_manager.embed_plot(fig, "Simulation Results", add_export_button=True)
            self.plot_canvas = canvas

            # Update the app state
            self.app_state.simulation_initialized = True

            # Log the status
            self.update_status("Press Start to Run Simulation.")

            return control_parameters, control_settings  # Return the parameters for further use if needed
        except Exception as e:
            self.update_status(f"Error during simulation initialization: {str(e)}")
            raise
    
    def cleanup_simulation_results(self):
        """
        Cleanup actions for the 'Simulation Results' tab.
        """        
        self.update_status(f"Cleaning up resources for Simulation Results tab.")
        self.main_processor.control_processor.continue_simulation = False
        self.main_processor.reset_simulation()
        self.close_widget("control_widget")
    
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

    def open_sizing_widget(self):
        """
        Open the Sizing widget.
        """
                
        if not hasattr(self, "sizing_widget"):
            self.sizing_widget = SizingWidget()
            self.sizing_widget.ui.pushButton.clicked.connect(self.set_turbine_size_parameters)
            
        self.sizing_widget.show()
        

    def open_surface_fitting_widget(self):
        """
        Open the Surface Fitting widget.
        """ 
                
        if not hasattr(self, "surface_fitting_widget"):
            self.surface_fitting_widget = SurfaceFittingWidget()
            self.surface_fitting_widget.ui.pushButton.clicked.connect(self.set_surface_fitting_parameters)
            
        self.surface_fitting_widget.show()

    def open_hydraulic_output_options_widget(self):
        """
        Open the widget to select outputs.
        """
        if not hasattr(self, "hydraulic_output_options_widget"):
            self.hydraulic_output_options_widget = OutputOptionsHydraulicWidget()
            self.hydraulic_output_options_widget.ui.pushButton.clicked.connect(self.set_output_options_hydraulic)
        self.hydraulic_output_options_widget.show()


    def open_maximise_output_widget(self):
        """
        Open the Manual/Automatic Control widget.
        """
        if not hasattr(self, "maximise_output_widget"):
            # Create the widget
            #data = self.main_processor.BEP_data            
            self.maximise_output_widget = MaximiseOutputWidget()                        
            # Connect the "Start" button to fetch values only when clicked
            self.maximise_output_widget.ui.pushButtonStart.clicked.connect(self.start_maximise_output)            

        self.maximise_output_widget.show()

    def open_control_widget(self):
        """
        Open the Manual/Automatic Control widget.
        """
        if not hasattr(self, "control_widget"):
            # Create the widget with a default H_t value
            data = self.main_processor.get_BEP_data()
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

    def close_widget(self, widget_name):
        """
        Close and delete a widget by its attribute name.

        Args:
            widget_name (str): The name of the widget attribute to close (e.g., "control_widget").
        """
        widget = getattr(self, widget_name, None)
        if widget and isinstance(widget, QWidget):
            widget.close()  # Properly close the widget
            delattr(self, widget_name)  # Remove the attribute reference
            self.update_status(f"Closed and deleted widget: {widget_name}")
        else:
            self.update_status(f"Widget '{widget_name}' does not exist or is not a valid QWidget.")


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

    
    def update_status(self, message, overwrite=False):
        """Update the status box in the GUI.

        Args:
            message (str): The message to display.
            overwrite (bool): If True, overwrite the last message.
        """
        if overwrite:
            # Overwrite the last line in the plainTextEdit
            text = self.ui.plainTextEdit.toPlainText()
            lines = text.split("\n")
            if lines:  # If there are existing lines, replace the last one
                lines[-1] = message
            else:  # If no lines, just add the message
                lines.append(message)
            self.ui.plainTextEdit.setPlainText("\n".join(lines))
        else:
            # Append the message
            self.ui.plainTextEdit.appendPlainText(message)

    



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()    
    
    window.turbine_hydraulics_action()
    window.main_processor.default_pathname()
    window.main_processor.default_turbine_parameters()
    window.app_state.update_actions("Load Data", True)
    window.app_state.update_actions("Sizing", True)
    window.app_state.update_actions("Surface Fit Settings", True)
    window.show()    
    sys.exit(app.exec())


