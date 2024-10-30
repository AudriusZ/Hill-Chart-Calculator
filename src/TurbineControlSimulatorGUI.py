#pyinstaller --onefile --name Turbine_Control_Simulator_0.1.2 --icon=icon.ico TurbineControlSimulatorGUI.py
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
from TurbineControlSimulator import TurbineControlSimulator
from TurbineData import TurbineData


class TurbineControlSimulatorGUI:
    def __init__(self, master, optimizer, D):         
        self.data = TurbineData() 
        self.master = master
        self.optimizer = optimizer
        self.D = D
        self.update_delay = 500  # Set delay time in milliseconds
        self.update_id = None

        # Set up the GUI layout
        self.master.title("Hill Chart Optimizer")

        self.head_control = False
        self.head_setting = 2.15
        
        # Create input labels and fields
        self.q_label = ttk.Label(master, text="Flow Rate (Q):")
        self.q_label.grid(row=0, column=0, padx=10, pady=5)
        self.q_input = ttk.Entry(master)
        self.q_input.grid(row=0, column=1, padx=10, pady=5)
        self.q_input.insert(0, "3.375")

        self.blade_label = ttk.Label(master, text="Blade Angle:")
        self.blade_label.grid(row=1, column=0, padx=10, pady=5)
        self.blade_input = ttk.Entry(master)
        self.blade_input.grid(row=1, column=1, padx=10, pady=5)
        self.blade_input.insert(0, "16.2")

        self.n_label = ttk.Label(master, text="Rotational Speed (n):")
        self.n_label.grid(row=2, column=0, padx=10, pady=5)
        self.n_input = ttk.Entry(master)
        self.n_input.grid(row=2, column=1, padx=10, pady=5)
        self.n_input.insert(0, "113.5")

        # Create the Load Data button to browse for the CSV file
        self.load_data_button = ttk.Button(master, text="Load Data", command=self.load_data)
        self.load_data_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Create output labels for results
        self.result_labels = {}
        for idx, text in enumerate(["Q11:", "n11:", "Efficiency:", "H:", "Power:"]):
            self.result_labels[text] = ttk.Label(master, text=f"{text} --")
            self.result_labels[text].grid(row=4 + idx, column=0, columnspan=2, padx=10, pady=5)

        # Add event listeners for input changes with debounce handling
        self.q_input.bind("<KeyRelease>", lambda event: self.debounced_update_output())
        self.blade_input.bind("<KeyRelease>", lambda event: self.debounced_update_output())
        self.n_input.bind("<KeyRelease>", lambda event: self.debounced_update_output())

        # Automatically load the default file if it exists in the home directory
        self.load_default_file()

        # Trigger an initial update
        self.update_output()

    def load_default_file(self):
        """Automatically load Mogu_D1.65m.csv if it is found in the script directory's parent folder."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        default_filepath = os.path.join(script_dir, "Mogu_D1.65m.csv")

        if os.path.exists(default_filepath):
            try:
                self.optimizer.read_hill_chart_values(default_filepath)
                self.optimizer.prepare_hill_chart_data()
                print(f"Data successfully loaded from {default_filepath}")

                # Update GUI to reflect successful data load
                self.master.title(f"Hill Chart Optimizer - Data Loaded: {os.path.basename(default_filepath)}")
                for key in self.result_labels:
                    self.result_labels[key].config(text=f"{key} --")  # Clear the previous results
            except Exception as e:
                print(f"Error loading default data: {e}")
                for key in self.result_labels:
                    self.result_labels[key].config(text=f"{key} Error")

    def load_data(self):
        """Prompt the user to select a CSV file and load the data."""
        filepath = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Select Hill Chart Data File"
        )

        if filepath:
            try:
                self.optimizer.read_hill_chart_values(filepath)
                self.optimizer.prepare_hill_chart_data()
                print(f"Data successfully loaded from {filepath}")
                
                # Update GUI to reflect successful data load
                self.master.title(f"Hill Chart Optimizer - Data Loaded: {os.path.basename(filepath)}")
                for key in self.result_labels:
                    self.result_labels[key].config(text=f"{key} --")  # Clear the previous results
            except Exception as e:
                print(f"Error loading data: {e}")
                for key in self.result_labels:
                    self.result_labels[key].config(text=f"{key} Error")

    def debounced_update_output(self):
        if self.update_id is not None:
            self.master.after_cancel(self.update_id)
        self.update_id = self.master.after(self.update_delay, self.update_output)

    def update_output(self):
        try:
            self.data.Q = float(self.q_input.get())
            blade_angle = float(self.blade_input.get())
            n = float(self.n_input.get())
            D = self.D  # Assuming diameter is already stored during initialization

            # Use head control if enabled
            if self.head_control:
                H_target = self.head_setting
                # Call the new method from TurbineControlSimulator
                result = self.optimizer.set_head_and_adjust(H_target, self.data.Q, D)

                # Extract updated rotational speed and blade angle
                n = result["Rotational Speed (n)"]
                #Blade = result["Blade Angle"]
                n11 = n * D / H_target**0.5
                Q11 = result["Blade Angle"]                
                blade_angle = self.optimizer.get_blade_angle(Q11, n11)
                print(blade_angle)                
                #efficiency = result["Efficiency"]

                # Update inputs to show adjusted values
                self.blade_input.delete(0, tk.END)
                self.blade_input.insert(0, f"{blade_angle:.2f}")
                self.n_input.delete(0, tk.END)
                self.n_input.insert(0, f"{n:.2f}")

            # Existing logic for computing results
            Q11, n11, efficiency, H, power = self.optimizer.compute_results(self.data.Q, D, n, blade_angle)

            # Update the result labels
            self.result_labels["Q11:"].config(text=f"Q11: {Q11:.2f}")
            self.result_labels["n11:"].config(text=f"n11: {n11:.1f}")
            self.result_labels["Efficiency:"].config(text=f"Efficiency: {efficiency:.2f}")
            self.result_labels["H:"].config(text=f"H: {H:.2f}")
            self.result_labels["Power:"].config(text=f"Power: {power:.0f}")

        except Exception as e:
            for key in self.result_labels:
                self.result_labels[key].config(text=f"{key} Error")
            print(f"An error occurred: {e}")

def main():
    # Create the TurbineControlSimulator instance with no data loaded initially
    optimizer = TurbineControlSimulator()

    # Create the GUI window
    root = tk.Tk()
    app = TurbineControlSimulatorGUI(root, optimizer, D=1.65)
    
    # Run the GUI event loop
    root.mainloop()

# Run the main function if this script is run directly
if __name__ == "__main__":
    main()
