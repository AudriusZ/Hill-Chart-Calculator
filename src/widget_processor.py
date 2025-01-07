
from PyQt6.QtWidgets import (
    QWidget
    )

from PyQt6.QtGui import QIntValidator

from turbine_simulator_gui import ( # Generated GUI files      
    Ui_FormManualAutomaticControl,
    Ui_MaximiseOutput,
    Ui_Sizing,
    Ui_SurfaceFitting
    )

class BaseWidget(QWidget):
    
    def get_line_edit_value(self, field_name):
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
            return None

    def get_all_line_edit_values(self, fields):
        """
        Get all input values from the form dynamically.

        Args:
            fields (list): List of field names to fetch.

        Returns:
            dict: A dictionary containing all the input field values.
        """
        values = {}
        for field in fields:
            value = self.get_line_edit_value(field)
            if value is None:
                raise ValueError(f"Invalid value entered for {field}. Please enter a numeric value.")
            values[field] = value
        return values
    
    def set_widget_enabled_with_style(self, widget, enabled):
        """
        Enables or disables a widget and updates its text color to reflect the state,
        explicitly preserving font size and other inherited styles.

        Args:
            widget (QWidget): The widget to enable/disable.
            enabled (bool): True to enable, False to disable.
        """
        widget.setEnabled(enabled)

        # Extract the existing style sheet
        current_style = widget.styleSheet()

        # Get the current font size from the widget's font
        font = widget.font()
        font_size = font.pointSize()

        # Define the new color based on the enabled state
        color = "gray" if not enabled else "black"

        # Construct a full style sheet, preserving font size
        updated_style = f"color: {color}; font-size: {font_size}pt;"

        # Append existing style properties if any
        if current_style:
            updated_style = current_style + f"; {updated_style}"

        # Apply the updated style
        widget.setStyleSheet(updated_style)


    

    def update_checkboxes_state(self, checkboxes, max_selected=2):
        """
        Allow up to 'max_selected' checkboxes to be selected. Disable others and gray them out.

        Args:
            checkboxes (list): List of QCheckBox widgets.
            max_selected (int): Maximum number of checkboxes allowed to be selected.
        """
        selected = [cb for cb in checkboxes if cb.isChecked()]
        for cb in checkboxes:
            enabled = cb in selected or len(selected) < max_selected
            self.set_widget_enabled_with_style(cb, enabled)
        return selected

    def update_input_field_labels(self, input_labels, input_fields, selected_checkboxes, default_labels):
        """
        Update input field labels and enable/disable input fields based on selected checkboxes.

        Args:
            input_labels (list): List of QLabel widgets for input field labels.
            input_fields (list): List of QLineEdit widgets for input fields.
            selected_checkboxes (list): List of selected QCheckBox widgets.
            default_labels (list): Default labels to show when no selection is valid.
        """
        if len(selected_checkboxes) == 2:
            # Update labels to match selected checkboxes
            input_labels[0].setText(selected_checkboxes[0].text())
            input_labels[1].setText(selected_checkboxes[1].text())
            input_fields[0].setEnabled(True)
            input_fields[1].setEnabled(True)
        else:
            # Reset labels and disable inputs
            for lbl, field, default in zip(input_labels, input_fields, default_labels):
                lbl.setText(default)
                field.setEnabled(False)

class SurfaceFittingWidget(BaseWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_SurfaceFitting()
        self.ui.setupUi(self)

        self.setWindowTitle("Surface Fitting")

        # Define groups of widgets for n11 and blade angle
        self.n11_widgets = [
            self.ui.label_n11_min,
            self.ui.lineEdit_n11_min,
            self.ui.label_n11_max,
            self.ui.lineEdit_n11_max,
            self.ui.label_n11_pts,
            self.ui.lineEdit_n11_pts,
        ]
        self.blade_angle_widgets = [
            self.ui.label_blade_angle_min,
            self.ui.lineEdit_blade_angle_min,
            self.ui.label_blade_angle_max,
            self.ui.lineEdit_blade_angle_max,
            self.ui.label_blade_angle_pts,
            self.ui.lineEdit_blade_angle_pts,
        ]

        # Apply integer-only validators for pts fields (min value: 3)
        int_validator = QIntValidator(3, 9999, self)
        self.ui.lineEdit_blade_angle_pts.setValidator(int_validator)
        self.ui.lineEdit_n11_pts.setValidator(int_validator)

        # Initialize widget states
        self.set_widget_enabled_with_style(self.ui.checkBox_extrapolate_n11, True)
        self.set_widget_enabled_with_style(self.ui.checkBox_extrapolate_blade_angle, False)
        self.toggle_widgets(self.n11_widgets, False)
        self.toggle_widgets(self.blade_angle_widgets, False)

        # Connect checkbox signals to handlers
        self.ui.checkBox_extrapolate_n11.stateChanged.connect(self.update_widget_states)
        self.ui.checkBox_extrapolate_blade_angle.stateChanged.connect(self.update_widget_states)

    def toggle_widgets(self, widgets, enabled):
        """
        Enable or disable a group of widgets.

        Args:
            widgets (list): List of widgets to enable/disable.
            enabled (bool): Whether to enable the widgets.
        """
        for widget in widgets:
            self.set_widget_enabled_with_style(widget, enabled)

    def update_widget_states(self):
        """
        Update widget states dynamically based on checkbox states.
        """
        # Update n11 widgets based on its checkbox state
        n11_enabled = self.ui.checkBox_extrapolate_n11.isChecked()
        self.toggle_widgets(self.n11_widgets, n11_enabled)

        # Automatically uncheck and disable blade angle checkbox if n11 is unchecked
        if not n11_enabled:
            self.ui.checkBox_extrapolate_blade_angle.setChecked(False)

        # Update blade angle checkbox and widgets based on n11 checkbox state
        self.set_widget_enabled_with_style(self.ui.checkBox_extrapolate_blade_angle, n11_enabled)
        blade_angle_enabled = n11_enabled and self.ui.checkBox_extrapolate_blade_angle.isChecked()
        self.toggle_widgets(self.blade_angle_widgets, blade_angle_enabled)

    def get_all_input_values(self):
        """
        Get input values and selected checkboxes dynamically.

        Returns:
            dict: A dictionary containing input field values and selected checkboxes.
        """
        fields = [
            "n11_min", "n11_max", "n11_pts",
            "blade_angle_min", "blade_angle_max", "blade_angle_pts", 
            "min_efficiency_limit"
            ]
        values = super().get_all_line_edit_values(fields)

        # Get checkbox states
        values["checkBox_extrapolate_n11"] = self.ui.checkBox_extrapolate_n11.isChecked()
        values["checkBox_extrapolate_blade_angle"] = self.ui.checkBox_extrapolate_blade_angle.isChecked()

        return values
        

class SizingWidget(BaseWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Sizing()
        self.ui.setupUi(self)

        self.setWindowTitle("Sizing")

        # Store checkboxes in a list for dynamic control
        self.checkboxes = [
            self.ui.checkBox_1,
            self.ui.checkBox_2,
            self.ui.checkBox_3,
            self.ui.checkBox_4,
        ]

        # Define input labels, input fields, and their default values
        self.input_labels = [self.ui.label_input_1, self.ui.label_input_2]
        self.input_fields = [self.ui.lineEdit_input_1, self.ui.lineEdit_input_2]
        self.default_labels = ["Input value 1", "Input value 2"]

        # Connect checkboxes to the update method
        for checkbox in self.checkboxes:
            checkbox.stateChanged.connect(self.update_checkboxes)

    def update_checkboxes(self):
        """
        Update the checkboxes, input field labels, and states.
        """
        selected = self.update_checkboxes_state(self.checkboxes, max_selected=2)
        self.update_input_field_labels(
            input_labels=self.input_labels,
            input_fields=self.input_fields,
            selected_checkboxes=selected,
            default_labels=self.default_labels
        )

    def get_all_input_values(self):
        """
        Get input values and selected checkboxes dynamically.

        Returns:
            dict: A dictionary containing input field values and selected checkboxes.
        """
        fields = ["input_1", "input_2"]
        values = super().get_all_line_edit_values(fields)

        # Dynamically find the indices of selected checkboxes
        selected_values = [i + 1 for i, cb in enumerate(self.checkboxes) if cb.isChecked()]
        
        # Add the selected checkbox indices to the dictionary
        values["selected_values"] = selected_values

        return values

    
        

class MaximiseOutputWidget(BaseWidget):
    def __init__(
            self,
            parent=None,                        
            ):
        super().__init__(parent)        
        self.ui = Ui_MaximiseOutput()  # Use the generated UI
        self.ui.setupUi(self)  # Set up the UI on this QWidget

        self.setWindowTitle("Maximise Output")

        # Set default value for var
        self.ui.lineEdit_Q_start.setText(f"{1.5:.2f}")
        self.ui.lineEdit_Q_stop.setText(f"{4.5:.2f}")
        self.ui.lineEdit_Q_step.setText(f"{0.5:.2f}")
        self.ui.lineEdit_n_start.setText(f"{10:.0f}")
        self.ui.lineEdit_n_stop.setText(f"{150:.0f}")
        self.ui.lineEdit_n_step.setText(f"{5:.0f}")
        self.ui.lineEdit_blade_angle_start.setText(f"{4:.1f}")
        self.ui.lineEdit_blade_angle_stop.setText(f"{25:.2f}")
        self.ui.lineEdit_blade_angle_step.setText(f"{2:.2f}")
        self.ui.lineEdit_H_min.setText(f"{0.1:.2f}")
        self.ui.lineEdit_H_max.setText(f"{2.15:.2f}")
        
    def get_all_input_values(self):
        fields = [
            "Q_start", "Q_stop", "Q_step",
            "n_start", "n_stop", "n_step",
            "blade_angle_start", "blade_angle_stop", "blade_angle_step",
            "H_min", "H_max"
        ]
        return super().get_all_line_edit_values(fields)


        

class ManualAutomaticControlWidget(BaseWidget):
    
    
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
            "blade_angle_min": 4,   # Minimum blade angle
            "blade_angle_max": 25   # Maximum blade angle
        }

        # Set default value for H_t
        self.ui.lineEdit_n_min.setText(f"{30:.1f}")
        self.ui.lineEdit_n_max.setText(f"{150:.1f}")
        self.ui.lineEdit_blade_angle_min.setText(f"{4:.1f}")
        self.ui.lineEdit_blade_angle_max.setText(f"{25:.1f}")
        self.ui.lineEdit_Kp.setText(f"{1.2:.1f}")
        self.ui.lineEdit_Ki.setText(f"{0.1:.1f}")
        self.ui.lineEdit_Kd.setText(f"{0.05:.1f}")
            

    def toggle_inputs(self, checked):
        """
        Enable or disable blade_angle, blade_angle_rate, n, and n_rate inputs
        based on the state of the 'Activate' checkbox, preserving font size and style.

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

        # Helper function to update the style of a widget
        def set_widget_style(widget, enabled):
            font = widget.font()
            font_size = font.pointSize()
            color = "black" if enabled else "gray"
            updated_style = f"color: {color}; font-size: {font_size}pt;"
            widget.setStyleSheet(updated_style)

        # Update styles for the widgets
        set_widget_style(self.ui.lineEdit_blade_angle, not checked)
        set_widget_style(self.ui.lineEdit_blade_angle_rate, not checked)
        set_widget_style(self.ui.lineEdit_n, not checked)
        set_widget_style(self.ui.lineEdit_n_rate, not checked)
        set_widget_style(self.ui.lineEdit_H_t, checked)
        set_widget_style(self.ui.lineEdit_H_t_rate, checked)
    
    def get_all_input_values(self):
        # Define the list of standard fields to fetch
        fields = [
            "H_t", "H_t_rate", "Q", "Q_rate",
            "blade_angle", "blade_angle_rate",
            "n", "n_rate"
        ]

        # Get the standard input values from the base class
        values = super().get_all_line_edit_values(fields)

        # Add the additional checkbox states to the dictionary
        values["head_control"] = self.ui.checkBox.isChecked()
        values["blade_angle_lock"] = self.ui.checkBox_2.isChecked()
        values["n_lock"] = False  # Default value

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

        return super().get_all_line_edit_values(fields)

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)  # Create the application instance
    sizing = SurfaceFittingWidget()       # Instantiate your widget
    sizing.show()                 # Show the widget
    sys.exit(app.exec())          # Execute the app's main loop
 