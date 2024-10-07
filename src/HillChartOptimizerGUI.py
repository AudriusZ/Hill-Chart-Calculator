import tkinter as tk
from tkinter import ttk
import os
import copy
from PerformanceCurve import PerformanceCurve
from HillChartOptimizer import HillChartOptimizer

class HillChartOptimizerGUI:
    def __init__(self, master, optimizer, D):
        self.master = master
        self.optimizer = optimizer
        self.D = D
        self.update_delay = 500  # Set delay time in milliseconds (e.g., 500ms = 0.5s)
        self.update_id = None    # Variable to hold the ID of the after() timer

        # Set up the GUI layout
        self.master.title("Hill Chart Optimizer")

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

        # Create output labels for results
        self.result_labels = {}
        for idx, text in enumerate(["Q11:", "n11:", "Efficiency:", "H:", "Power:"]):
            self.result_labels[text] = ttk.Label(master, text=f"{text} --")
            self.result_labels[text].grid(row=3 + idx, column=0, columnspan=2, padx=10, pady=5)

        # Add event listeners for input changes with debounce handling
        self.q_input.bind("<KeyRelease>", lambda event: self.debounced_update_output())
        self.blade_input.bind("<KeyRelease>", lambda event: self.debounced_update_output())
        self.n_input.bind("<KeyRelease>", lambda event: self.debounced_update_output())

        # Trigger an initial update
        self.update_output()

    def debounced_update_output(self):
        # If there's already a scheduled update, cancel it
        if self.update_id is not None:
            self.master.after_cancel(self.update_id)

        # Schedule a new update with the delay specified
        self.update_id = self.master.after(self.update_delay, self.update_output)

    def update_output(self):
        try:
            # Read the inputs
            Q = float(self.q_input.get())
            Blade = float(self.blade_input.get())
            n = float(self.n_input.get())

            # Copy the optimizer and prepare the slices
            optimizer2 = copy.deepcopy(self.optimizer)
            performance_curve = PerformanceCurve(optimizer2)
            n11_slice, Q11_slice, efficiency_slice, _ = performance_curve.slice_hill_chart_data(selected_blade_angle=Blade)

            if len(Q11_slice) < 2 or len(n11_slice) < 2:
                for key in self.result_labels:
                    self.result_labels[key].config(text=f"{key} Error")
                return

            # Initial guess for n11
            n11_initial_guess = 127.7

            # Calculate the results using the recursive function
            n11_solution, H_solution, Q11_solution, efficiency = optimizer2.solve_recursive_n11_guess(
                Q, self.D, n, n11_initial_guess, n11_slice, Q11_slice, efficiency_slice
            )

            # Calculate power
            power = 9.8 * 1000 * Q * H_solution * efficiency

            # Update the result labels
            self.result_labels["Q11:"].config(text=f"Q11: {Q11_solution:.2f}")
            self.result_labels["n11:"].config(text=f"n11: {n11_solution:.1f}")
            self.result_labels["Efficiency:"].config(text=f"Efficiency: {efficiency:.2f}")
            self.result_labels["H:"].config(text=f"H: {H_solution:.2f}")
            self.result_labels["Power:"].config(text=f"Power: {power:.0f}")

        except Exception as e:
            for key in self.result_labels:
                self.result_labels[key].config(text=f"{key} Error")
            print(f"An error occurred: {e}")

# Create the HillChartOptimizer instance and load data
optimizer = HillChartOptimizer()
datapath = os.path.join(os.path.dirname(__file__), '../src/Mogu_D1.65m.csv')
optimizer.read_hill_chart_values(datapath)
optimizer.prepare_hill_chart_data()

# Create the GUI window
root = tk.Tk()
app = HillChartOptimizerGUI(root, optimizer, D=1.65)

# Run the GUI event loop
root.mainloop()

