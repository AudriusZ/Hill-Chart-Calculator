# Application packaging command:
# pyinstaller --onefile --name Turbine_Control_Simulator_0.1.3 --icon=icon.ico TurbineControlSimulatorGUI.py

import tkinter as tk
from tkinter import ttk, filedialog, BooleanVar
import os
from TurbineControlSimulator import TurbineControlSimulator
from TurbineData import TurbineData


class TurbineControlSimulatorGUI:
    """GUI class for the Turbine Control Simulator application, built with tkinter."""

    def __init__(self, master, simulator):                 
        """
        Initialize the GUI application with main window setup, input fields, and output labels.

        Args:
            master: The root window for tkinter.
            simulator: The TurbineControlSimulator instance handling turbine calculations.
        """
        self.master = master
        self.simulator = simulator        
        self.update_delay = 500  # Delay time in milliseconds for updating outputs
        self.update_id = None

        # Set up the main window title
        self.master.title("Turbine Control Simulator")

        # Create and configure input fields for turbine parameters
        self.D_label = ttk.Label(master, text="Diameter (D) - Temporary input:")
        self.D_label.grid(row=0, column=0, padx=10, pady=5)
        self.D_input = ttk.Entry(master)
        self.D_input.grid(row=0, column=1, padx=10, pady=5)
        self.D_input.insert(0, "1.65")

        # Horizontal separator line
        self.separator = ttk.Separator(master, orient="horizontal")
        self.separator.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        # Target Head input field and activation checkbox
        self.H_target_label = ttk.Label(master, text="Target Head (H):")
        self.H_target_label.grid(row=2, column=0, padx=10, pady=5)

        self.H_target_input = ttk.Entry(master)
        self.H_target_input.grid(row=2, column=1, padx=10, pady=5)
        self.H_target_input.insert(0, "2.15")
        self.H_target_input.config(state="disabled")  # Initially disabled

        # BooleanVar for tracking checkbox state for H_target activation
        self.activate_var = BooleanVar()

        # Function to toggle H_target_input state based on checkbox
        def toggle_H_target():
            """Enable or disable the Target Head (H) input field based on checkbox state."""
            if self.activate_var.get():
                self.H_target_input.config(state="normal")
            else:
                self.H_target_input.config(state="disabled")

        # Checkbox for activating H_target_input field
        self.activate_checkbox = ttk.Checkbutton(
            master, text="Activate", variable=self.activate_var, command=toggle_H_target
        )
        self.activate_checkbox.grid(row=2, column=2, padx=10, pady=5)

        # Flow Rate input
        self.q_label = ttk.Label(master, text="Flow Rate (Q):")
        self.q_label.grid(row=3, column=0, padx=10, pady=5)
        self.q_input = ttk.Entry(master)
        self.q_input.grid(row=3, column=1, padx=10, pady=5)
        self.q_input.insert(0, "3.375")

        # Blade Angle input
        self.blade_label = ttk.Label(master, text="Blade Angle:")
        self.blade_label.grid(row=4, column=0, padx=10, pady=5)
        self.blade_input = ttk.Entry(master)
        self.blade_input.grid(row=4, column=1, padx=10, pady=5)
        self.blade_input.insert(0, "13")

        # Rotational Speed input
        self.n_label = ttk.Label(master, text="Rotational Speed (n):")
        self.n_label.grid(row=5, column=0, padx=10, pady=5)
        self.n_input = ttk.Entry(master)
        self.n_input.grid(row=5, column=1, padx=10, pady=5)
        self.n_input.insert(0, "50")

        # Button to load data file (CSV)
        self.load_data_button = ttk.Button(master, text="Load Data", command=self.load_data)
        self.load_data_button.grid(row=6, column=0, columnspan=2, pady=10)

        # Output labels for displaying computed results
        self.result_labels = {}
        for idx, text in enumerate(["Q11:", "n11:", "Efficiency:", "H:", "Power:"]):
            self.result_labels[text] = ttk.Label(master, text=f"{text} --")
            self.result_labels[text].grid(row=7 + idx, column=0, columnspan=2, padx=10, pady=5)

        # Test Button to maximise output
        self.maximise_output_button = ttk.Button(master, text="Test Maximise Output", command=self.maximise_output)
        self.maximise_output_button.grid(row=12, column=0, columnspan=2, pady=10)

        # Bind input fields to trigger output updates with debounce handling
        self.q_input.bind("<KeyRelease>", lambda event: self.update_output())
        self.blade_input.bind("<KeyRelease>", lambda event: self.update_output())
        self.n_input.bind("<KeyRelease>", lambda event: self.update_output())

        # Automatically load default data file if present in the directory
        self.load_data(file_name=True)  # Load default file if available

        # Initial output update
        self.update_output()
    def maximise_output(self):
        self.simulator.maximize_output()

    def load_data(self, file_name=False):
        """
        Load data from a specified file or prompt the user to select one.

        Args:
            file_name (bool or str): 
                - If True, attempts to load a default file from the script's directory.
                - If a string, uses it directly as the file path.
                - If False, opens a file dialog to select a file.
        """
        # Determine the appropriate file path based on file_name parameter
        if file_name is True:
            # Load default data file from the script's directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(script_dir, "Mogu_D1.65m.csv")
            if not os.path.exists(filepath):
                print("Default file not found.")
                return
        elif isinstance(file_name, str):
            filepath = file_name
        else:
            # Open file dialog if no file is specified
            filepath = filedialog.askopenfilename(
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
                title="Select Hill Chart Data File"
            )
            if not filepath:  # Exit if no file is selected
                return

        # Attempt to load data from the specified file path
        try:
            self.simulator.read_hill_chart_values(filepath)
            self.simulator.filter_for_maximum_efficiency(remove=False)
            self.simulator.prepare_hill_chart_data()
            print(f"Data successfully loaded from {filepath}")

            # Update GUI title to indicate successful data load
            self.master.title(f"Turbine Control Simulator - Data Loaded: {os.path.basename(filepath)}")
            # Clear previous result labels after data load
            for key in self.result_labels:
                self.result_labels[key].config(text=f"{key} --")
        except Exception as e:
            print(f"Error loading data from {filepath}: {e}")
            # Display error message on result labels if data load fails
            for key in self.result_labels:
                self.result_labels[key].config(text=f"{key} Error")

    def update_output(self):
        """Calculate and update the output based on the current input values."""
        try:
            # Retrieve input values and parse them as floats
            Q = float(self.q_input.get())
            blade_angle = float(self.blade_input.get())
            n = float(self.n_input.get())
            D = float(self.D_input.get())
            head_control = bool(self.activate_var.get())

            # Set simulator attributes with user inputs
            self.simulator.set_operation_attribute("Q", Q)
            self.simulator.set_operation_attribute("blade_angle", blade_angle)
            self.simulator.set_operation_attribute("n", n)
            self.simulator.set_operation_attribute("D", D)

            # Adjust attributes based on head control settings if enabled
            if head_control:
                H_target = float(self.H_target_input.get())
                # Adjust head control in the simulator
                result = self.simulator.set_head_and_adjust(H_target)
                n = result["Rotational Speed (n)"]
                blade_angle = result["Blade Angle"]
                self.simulator.set_operation_attribute("n", n)
                self.simulator.set_operation_attribute("blade_angle", blade_angle)

                # Update GUI inputs to show adjusted values
                self.blade_input.delete(0, tk.END)
                self.blade_input.insert(0, f"{blade_angle:.2f}")
                self.n_input.delete(0, tk.END)
                self.n_input.insert(0, f"{n:.2f}")

            # Compute results using the simulator
            operation_point = self.simulator.compute_results()

            # Update output result labels with computed values
            self.result_labels["Q11:"].config(text=f"Q11: {operation_point.Q11:.2f}")
            self.result_labels["n11:"].config(text=f"n11: {operation_point.n11:.1f}")
            self.result_labels["Efficiency:"].config(text=f"Efficiency: {operation_point.efficiency:.2f}")
            self.result_labels["H:"].config(text=f"H: {operation_point.H:.2f}")
            self.result_labels["Power:"].config(text=f"Power: {operation_point.power:.0f}")

        except Exception as e:
            # Display error message on result labels in case of failure
            for key in self.result_labels:
                self.result_labels[key].config(text=f"{key} Error")
            print(f"An error occurred: {e}")

def main():
    """
    Main function to initialize the Turbine Control Simulator application.
    Creates an instance of the simulator and starts the tkinter GUI event loop.
    """
    # Initialize the simulator instance with no initial data
    simulator = TurbineControlSimulator()

    # Initialize the main application window
    root = tk.Tk()
    app = TurbineControlSimulatorGUI(root, simulator)
    
    # Start the tkinter main event loop
    root.mainloop()

# Run the main function if this script is run directly
if __name__ == "__main__":
    main()
