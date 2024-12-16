
from PyQt6.QtWidgets import (
    QWidget
    )
from turbine_simulator_gui import ( # Generated GUI files      
    Ui_FormManualAutomaticControl,
    Ui_MaximiseOutput,
    Ui_Sizing
    )

class SizingWidget(QWidget):
    def __init__(
            self,
            parent=None,                        
            ):
        super().__init__(parent)        
        self.ui = Ui_Sizing()  # Use the generated UI
        self.ui.setupUi(self)  # Set up the UI on this QWidget

        self.setWindowTitle("Sizing")

        # Set default value for var
        self.ui.lineEdit_input_1.setText(f"{2:.2f}")        

    
        

class MaximiseOutputWidget(QWidget):
    def __init__(
            self,
            parent=None,                        
            ):
        super().__init__(parent)        
        self.ui = Ui_MaximiseOutput()  # Use the generated UI
        self.ui.setupUi(self)  # Set up the UI on this QWidget

        self.setWindowTitle("Maximise Output")

        # Set default value for var
        self.ui.lineEdit_Q_start.setText(f"{2:.2f}")
        self.ui.lineEdit_Q_stop.setText(f"{6.5:.2f}")
        self.ui.lineEdit_Q_step.setText(f"{0.5:.2f}")
        self.ui.lineEdit_n_start.setText(f"{10:.0f}")
        self.ui.lineEdit_n_stop.setText(f"{150:.0f}")
        self.ui.lineEdit_n_step.setText(f"{1:.0f}")
        self.ui.lineEdit_blade_angle_start.setText(f"{16.2:.1f}")
        self.ui.lineEdit_blade_angle_stop.setText(f"{16.2:.2f}")
        self.ui.lineEdit_blade_angle_step.setText(f"{1:.2f}")
        self.ui.lineEdit_H_min.setText(f"{0.1:.2f}")
        self.ui.lineEdit_H_max.setText(f"{2.8:.2f}")
        
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
            "Q_start", "Q_stop", "Q_step",
            "n_start", "n_stop", "n_step",
            "blade_angle_start", "blade_angle_stop", "blade_angle_step",
            "H_min", "H_max"
        ]

        # Dynamically fetch and validate values for all fields
        values = {}
        for field in fields:
            value = self.get_input_value(field)
            if value is None:
                raise ValueError(f"Invalid value entered for {field}. Please enter a numeric value.")
            values[field] = value

        return values


        

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



 