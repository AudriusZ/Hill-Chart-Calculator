from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem, QFileDialog, QMessageBox
from turbine_simulator_gui import Ui_MainWindow  # Generated GUI file
from HillChartProcessor import HillChartProcessor  # Processing logic
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the GUI design
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Initialize the processor
        self.processor = HillChartProcessor()

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

    def run_test_steps(self):
        """Run the same steps as in testHillChartProcessor when ButtonDev is clicked."""
        try:
            self.default_turbine_parameters()
            self.default_plot_parameters()
            self.default_output_parameters()
            self.processor.generate_outputs()
            self.update_status("Test steps executed successfully.")
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
        n_contours = 25
        extrapolation_options_vars = [1, 1]
        extrapolation_values_n11 = [60, 200, 10]
        extrapolation_values_blade_angles = [7.38, 21.18, 10]

        self.processor.get_plot_parameters(n_contours, extrapolation_options_vars, extrapolation_values_n11, extrapolation_values_blade_angles)

    def default_output_parameters(self):
        """Set default output parameters as in the test."""
        output_options = {
            '3D Hill Chart': 0,
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
            'Normalize': 1,
            'Save Chart Data': 0
        }

        self.processor.get_output_parameters(output_options, output_suboptions, settings_options)

    def update_status(self, message):
        """Update the status box in the GUI."""
        self.ui.plainTextEdit.appendPlainText(message)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.run_test_steps()
    #window.show()
    sys.exit(app.exec())
