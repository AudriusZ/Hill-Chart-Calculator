#pyinstaller --onefile --name Turbine_Control_Simulator_0.1.2 --icon=icon.ico TurbineControlSimulatorGUI.py

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import BooleanVar
import os
from TurbineControlSimulator import TurbineControlSimulator
from TurbineData import TurbineData


class TurbineControlSimulatorGUI:
    def __init__(self, master, simulator):                 
        self.master = master
        self.simulator = simulator        
        self.update_delay = 500  # Set delay time in milliseconds
        self.update_id = None

        # Set up the GUI layout
        self.master.title("Turbine Control Simulator")        

        # Create input labels and fields
        self.D_label = ttk.Label(master, text="Diameter (D) - Temporary input:")
        self.D_label.grid(row=0, column=0, padx=10, pady=5)
        self.D_input = ttk.Entry(master)
        self.D_input.grid(row=0, column=1, padx=10, pady=5)
        self.D_input.insert(0, "1.65")

        # Insert a horizontal separator line here        
        self.separator = ttk.Separator(master, orient="horizontal")
        self.separator.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        # Create input labels and fields
        self.H_target_label = ttk.Label(master, text="Target Head (H):")
        self.H_target_label.grid(row=2, column=0, padx=10, pady=5)

        # Create the input field for H_target and set it initially as disabled
        self.H_target_input = ttk.Entry(master)
        self.H_target_input.grid(row=2, column=1, padx=10, pady=5)
        self.H_target_input.insert(0, "2.15")
        self.H_target_input.config(state="disabled")  # Initially disabled

        # Create a BooleanVar to track the checkbox state
        self.activate_var = BooleanVar()

        # Function to enable/disable H_target_input based on the checkbox
        def toggle_H_target():
            if self.activate_var.get():
                self.H_target_input.config(state="normal")
            else:
                self.H_target_input.config(state="disabled")

        # Create the checkbox and set command to toggle the input field
        self.activate_checkbox = ttk.Checkbutton(
            master, text="Activate", variable=self.activate_var, command=toggle_H_target
        )
        self.activate_checkbox.grid(row=2, column=2, padx=10, pady=5)

        self.q_label = ttk.Label(master, text="Flow Rate (Q):")
        self.q_label.grid(row=3, column=0, padx=10, pady=5)
        self.q_input = ttk.Entry(master)
        self.q_input.grid(row=3, column=1, padx=10, pady=5)
        self.q_input.insert(0, "3.375")

        self.blade_label = ttk.Label(master, text="Blade Angle:")
        self.blade_label.grid(row=4, column=0, padx=10, pady=5)
        self.blade_input = ttk.Entry(master)
        self.blade_input.grid(row=4, column=1, padx=10, pady=5)
        self.blade_input.insert(0, "16.2")

        self.n_label = ttk.Label(master, text="Rotational Speed (n):")
        self.n_label.grid(row=5, column=0, padx=10, pady=5)
        self.n_input = ttk.Entry(master)
        self.n_input.grid(row=5, column=1, padx=10, pady=5)
        self.n_input.insert(0, "113.5")

        # Create the Load Data button to browse for the CSV file
        self.load_data_button = ttk.Button(master, text="Load Data", command=self.load_data)
        self.load_data_button.grid(row=6, column=0, columnspan=2, pady=10)

        # Create output labels for results
        self.result_labels = {}
        for idx, text in enumerate(["Q11:", "n11:", "Efficiency:", "H:", "Power:"]):
            self.result_labels[text] = ttk.Label(master, text=f"{text} --")
            self.result_labels[text].grid(row=7 + idx, column=0, columnspan=2, padx=10, pady=5)

        # Add event listeners for input changes with debounce handling
        self.q_input.bind("<KeyRelease>", lambda event: self.update_output())
        self.blade_input.bind("<KeyRelease>", lambda event: self.update_output())
        self.n_input.bind("<KeyRelease>", lambda event: self.update_output())

        # Automatically load the default file if it exists in the home directory
        self.load_data(file_name=True)  # Trigger initial load of the default file

        # Trigger an initial update
        self.update_output()

    def load_data(self, file_name=False):
        """
        Load data from a specified file or prompt the user to select one.
        
        If file_name is True, load default file if it exists.
        If file_name is a string, use it directly as the file path.
        Otherwise, open a file dialog to select the file.
        """
        # Determine file path based on file_name parameter
        if file_name is True:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(script_dir, "Mogu_D1.65m.csv")
            if not os.path.exists(filepath):
                print("Default file not found.")
                return
        elif isinstance(file_name, str):
            filepath = file_name
        else:
            filepath = filedialog.askopenfilename(
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
                title="Select Hill Chart Data File"
            )
            if not filepath:  # If no file was selected, exit the function
                return

        # Load data from the determined filepath
        try:
            self.simulator.read_hill_chart_values(filepath)
            self.simulator.filter_for_maximum_efficiency(remove=False)
            self.simulator.prepare_hill_chart_data()
            print(f"Data successfully loaded from {filepath}")

            # Update GUI to reflect successful data load
            self.master.title(f"Turbine Control Simulator - Data Loaded: {os.path.basename(filepath)}")
            for key in self.result_labels:
                self.result_labels[key].config(text=f"{key} --")  # Clear previous results
        except Exception as e:
            print(f"Error loading data from {filepath}: {e}")
            for key in self.result_labels:
                self.result_labels[key].config(text=f"{key} Error")

    def update_output(self):
        try:
            Q = float(self.q_input.get())
            blade_angle = float(self.blade_input.get())
            n = float(self.n_input.get())            
            D = float(self.D_input.get())
            head_control = bool(self.activate_var.get())            

            # Set the attribute dynamically
            self.simulator.set_operation_attribute("Q", Q)
            self.simulator.set_operation_attribute("blade_angle", blade_angle)
            self.simulator.set_operation_attribute("n", n)
            self.simulator.set_operation_attribute("D", D)

            # Use head control if enabled
            if head_control:                
                H_target = float(self.H_target_input.get())
                # Call the new method from TurbineControlSimulator
                result = self.simulator.set_head_and_adjust(H_target)                
                n = result["Rotational Speed (n)"]
                blade_angle = result["Blade Angle"]                
                self.simulator.set_operation_attribute("n", n)                
                self.simulator.set_operation_attribute("blade_angle", blade_angle)                

                # Update inputs to show adjusted values
                self.blade_input.delete(0, tk.END)
                self.blade_input.insert(0, f"{blade_angle:.2f}")
                self.n_input.delete(0, tk.END)
                self.n_input.insert(0, f"{n:.2f}")

            # Existing logic for computing results
            #Q11, n11, efficiency, H, power = self.simulator.compute_results(Q, D, n, blade_angle)
            operation_point = self.simulator.compute_results()

            # Update the result labels
            self.result_labels["Q11:"].config(text=f"Q11: {operation_point.Q11:.2f}")
            self.result_labels["n11:"].config(text=f"n11: {operation_point.n11:.1f}")
            self.result_labels["Efficiency:"].config(text=f"Efficiency: {operation_point.efficiency:.2f}")
            self.result_labels["H:"].config(text=f"H: {operation_point.H:.2f}")
            self.result_labels["Power:"].config(text=f"Power: {operation_point.power:.0f}")

        except Exception as e:
            for key in self.result_labels:
                self.result_labels[key].config(text=f"{key} Error")
            print(f"An error occurred: {e}")

def main():
    # Create the TurbineControlSimulator instance with no data loaded initially
    simulator = TurbineControlSimulator()

    # Create the GUI window
    root = tk.Tk()
    app = TurbineControlSimulatorGUI(root, simulator)
    
    # Run the GUI event loop
    root.mainloop()

# Run the main function if this script is run directly
if __name__ == "__main__":
    main()
