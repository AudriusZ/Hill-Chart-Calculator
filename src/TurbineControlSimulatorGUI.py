# Application packaging command:
# pyinstaller --onefile --name Turbine_Control_Simulator_0.1.3 --icon=icon.ico TurbineControlSimulatorGUI.py

import tkinter as tk
from tkinter import ttk, filedialog, BooleanVar
import os
import numpy as np
from TurbineControlSimulator import TurbineControlSimulator
from TurbineData import TurbineData
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import time
from collections import deque
from matplotlib.animation import FuncAnimation


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
        self.update_delay = 1000  # Delay time in milliseconds for updating outputs
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
            self.update_output()

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
        self.blade_input.insert(0, "16.2")

        # Rotational Speed input
        self.n_label = ttk.Label(master, text="Rotational Speed (n):")
        self.n_label.grid(row=5, column=0, padx=10, pady=5)
        self.n_input = ttk.Entry(master)
        self.n_input.grid(row=5, column=1, padx=10, pady=5)
        self.n_input.insert(0, "113.5")

        # Button to load data file (CSV)
        self.load_data_button = ttk.Button(master, text="Load Data", command=self.load_data)
        self.load_data_button.grid(row=6, column=0, columnspan=2, pady=10)

        # Output labels for displaying computed results
        self.result_labels = {}
        for idx, text in enumerate(["Q11:", "n11:", "Efficiency:", "H:", "Power:"]):
            self.result_labels[text] = ttk.Label(master, text=f"{text} --")
            self.result_labels[text].grid(row=7 + idx, column=0, columnspan=2, padx=10, pady=5)

        # Button to maximize output, triggering the pop-up
        self.maximise_output_button = ttk.Button(master, text="Maximise Output", command=self.open_range_prompt)
        self.maximise_output_button.grid(row=12, column=0, columnspan=2, pady=10)

        # Bind input fields to trigger output updates with debounce handling
        self.q_input.bind("<KeyRelease>", lambda event: self.update_output())
        self.blade_input.bind("<KeyRelease>", lambda event: self.update_output())
        self.n_input.bind("<KeyRelease>", lambda event: self.update_output())
        self.H_target_input.bind("<KeyRelease>", lambda event: self.update_output())

        # Canvas and Notebook for plots
        self.notebook = ttk.Notebook(master)
        self.notebook.grid(row=0, column=3, rowspan=15, padx=10, pady=5, sticky="nsew")

        # Tab for multiple subplots (Overview Plots)
        self.sub_plot_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.sub_plot_tab, text="Overview Plots")

        # Initialize figure and axis for the Overview Plots tab with 5 subplots
        self.overview_fig, self.overview_ax = plt.subplots(5, 1, figsize=(6, 8), sharex=True)
        self.sub_plot_canvas = FigureCanvasTkAgg(self.overview_fig, master=self.sub_plot_tab)
        self.sub_plot_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Setup for live plot data in the Overview Plots tab
        self.time_data = deque(maxlen=300)  # Store time points up to 30s (assuming 10 updates/sec)
        self.q11_data = deque(maxlen=300)
        self.n11_data = deque(maxlen=300)
        self.efficiency_data = deque(maxlen=300)
        self.h_data = deque(maxlen=300)
        self.power_data = deque(maxlen=300)
        self.start_time = time.time()  # Track start time for elapsed time on x-axis

        # Initialize the live plot animation
        self.anim = FuncAnimation(self.overview_fig, self.update_live_plot, interval=1000)

        # Automatically load default data file if present in the directory
        self.load_data(file_name=True)  # Load default file if available

        # Initial output update
        self.update_output()

    def schedule_continuous_update(self):
        """Schedules the continuous update for live plot data regardless of input change."""
        self.update_live_plot(None)  # Call the live plot update directly
        self.master.after(1000, self.schedule_continuous_update)  # Repeat every second


    def add_plot_tab(self, title):
        """Adds a new tab with a canvas for plotting to the notebook."""
        frame = ttk.Frame(self.notebook)  # Corrected from self.plot_notebook
        self.notebook.add(frame, text=title)

        # Create and place a canvas for each plot
        fig, ax = plt.subplots(figsize=(5, 4))
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Example plot (update with real data as needed)
        ax.plot([1, 2, 3], [1, 4, 9])
        ax.set_title(f"{title} - Example Plot")
        canvas.draw()

    def plot_results(self, max_power_results):
        """Plot the results in the second tab dynamically."""
        # This method remains as before, but plots will be added to `self.plot_tab` now
        Q_values, power_values, n_values, blade_angle_values, efficiency_values, head_values = [], [], [], [], [], []
        for Q, result in max_power_results.items():
            if result is not None:
                Q_values.append(Q)
                power_values.append(result['power'])
                n_values.append(result['n'])
                blade_angle_values.append(result['blade_angle'])
                efficiency_values.append(result['efficiency'])
                head_values.append(result['H'])

        fig, ax = plt.subplots()
        ax.plot(Q_values, power_values, marker='o')
        ax.set_xlabel("Flow Rate (Q)")
        ax.set_ylabel("Power")
        ax.set_title("Power vs Flow Rate (Q)")

        # Display the plot on the second tab
        canvas = FigureCanvasTkAgg(fig, self.plot_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def display_plots_in_tabs(self, figures):
        """Clear dynamically added tabs and add a new tab for each figure in the notebook."""
        # Remove all tabs except the first one (Overview Plots)
        while len(self.notebook.tabs()) > 1:
            self.notebook.forget(1)

        # Add a new tab for each figure
        for title, fig in figures.items():
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=title)

            # Create canvas for the plot
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.get_tk_widget().pack(fill="both", expand=True)
            canvas.draw()

    def open_range_prompt(self):
        """Open a prompt window to get range inputs from the user for maximization."""
        # Create a new Toplevel window as a modal dialog
        self.range_prompt = tk.Toplevel(self.master)
        self.range_prompt.title("Set Range Limits for Maximization")

        # Make the prompt window modal
        self.range_prompt.transient(self.master)
        self.range_prompt.grab_set()

        # Add input fields for Q, H, n, and blade angle ranges
        self.create_range_inputs(self.range_prompt)

        # Add a submit button
        submit_button = ttk.Button(self.range_prompt, text="Submit", command=self.submit_ranges)
        submit_button.grid(row=5, column=0, columnspan=4, pady=10)

    def create_range_inputs(self, prompt):
        """Create input fields for Q_range, H_range, n_range, and blade_angle_range in the prompt window."""
        
        # Flow Rate Range (Q_range)
        ttk.Label(prompt, text="Flow Rate Range (Q): Start").grid(row=0, column=0, padx=10, pady=5)
        self.q_start_input = ttk.Entry(prompt)
        self.q_start_input.grid(row=0, column=1, padx=10, pady=5)
        self.q_start_input.insert(0, "0.5")
        
        ttk.Label(prompt, text="Stop").grid(row=0, column=2, padx=10, pady=5)
        self.q_stop_input = ttk.Entry(prompt)
        self.q_stop_input.grid(row=0, column=3, padx=10, pady=5)
        self.q_stop_input.insert(0, "4.5")
        
        ttk.Label(prompt, text="Step").grid(row=0, column=4, padx=10, pady=5)
        self.q_step_input = ttk.Entry(prompt)
        self.q_step_input.grid(row=0, column=5, padx=10, pady=5)
        self.q_step_input.insert(0, "0.5")
        
        # Head Range (H_range)
        ttk.Label(prompt, text="Head Range (H): Min").grid(row=1, column=0, padx=10, pady=5)
        self.h_min_input = ttk.Entry(prompt)
        self.h_min_input.grid(row=1, column=1, padx=10, pady=5)
        self.h_min_input.insert(0, "0.5")
        
        ttk.Label(prompt, text="Max").grid(row=1, column=2, padx=10, pady=5)
        self.h_max_input = ttk.Entry(prompt)
        self.h_max_input.grid(row=1, column=3, padx=10, pady=5)
        self.h_max_input.insert(0, "2.15")

        # Rotational Speed Range (n_range)
        ttk.Label(prompt, text="Rotational Speed Range (n): Start").grid(row=2, column=0, padx=10, pady=5)
        self.n_start_input = ttk.Entry(prompt)
        self.n_start_input.grid(row=2, column=1, padx=10, pady=5)
        self.n_start_input.insert(0, "40")
        
        ttk.Label(prompt, text="Stop").grid(row=2, column=2, padx=10, pady=5)
        self.n_stop_input = ttk.Entry(prompt)
        self.n_stop_input.grid(row=2, column=3, padx=10, pady=5)
        self.n_stop_input.insert(0, "150")
        
        ttk.Label(prompt, text="Step").grid(row=2, column=4, padx=10, pady=5)
        self.n_step_input = ttk.Entry(prompt)
        self.n_step_input.grid(row=2, column=5, padx=10, pady=5)
        self.n_step_input.insert(0, "10")

        # Blade Angle Range
        ttk.Label(prompt, text="Blade Angle Range: Start").grid(row=3, column=0, padx=10, pady=5)
        self.blade_start_input = ttk.Entry(prompt)
        self.blade_start_input.grid(row=3, column=1, padx=10, pady=5)
        self.blade_start_input.insert(0, "9")
        
        ttk.Label(prompt, text="Stop").grid(row=3, column=2, padx=10, pady=5)
        self.blade_stop_input = ttk.Entry(prompt)
        self.blade_stop_input.grid(row=3, column=3, padx=10, pady=5)
        self.blade_stop_input.insert(0, "21")
        
        ttk.Label(prompt, text="Step").grid(row=3, column=4, padx=10, pady=5)
        self.blade_step_input = ttk.Entry(prompt)
        self.blade_step_input.grid(row=3, column=5, padx=10, pady=5)
        self.blade_step_input.insert(0, "3")

    def submit_ranges(self):
        """Retrieve range values from the prompt and perform maximization."""
        try:
            # Retrieve and parse Q_range
            Q_start = float(self.q_start_input.get())
            Q_stop = float(self.q_stop_input.get())
            Q_step = float(self.q_step_input.get())
            Q_range = np.arange(Q_start, Q_stop + Q_step, Q_step)

            # Retrieve and parse H_range
            H_min = float(self.h_min_input.get())
            H_max = float(self.h_max_input.get())
            H_range = (H_min, H_max)

            # Retrieve and parse n_range
            n_start = float(self.n_start_input.get())
            n_stop = float(self.n_stop_input.get())
            n_step = float(self.n_step_input.get())
            n_range = np.arange(n_start, n_stop + n_step, n_step)

            # Retrieve and parse blade_angle_range
            blade_start = float(self.blade_start_input.get())
            blade_stop = float(self.blade_stop_input.get())
            blade_step = float(self.blade_step_input.get())
            blade_angle_range = np.arange(blade_start, blade_stop + blade_step, blade_step)

            # Set the ranges in the simulator
            self.simulator.set_ranges(Q_range=Q_range, H_range=H_range, n_range=n_range, blade_angle_range=blade_angle_range)

            # Run the maximization function
            max_power_results = self.simulator.maximize_output_in_flow_range()
            print("Maximization completed successfully.")

            # Close the prompt
            self.range_prompt.destroy()

            # Retrieve figures from plot_results
            figures = self.simulator.plot_results(max_power_results)
            
            # Display figures in tabs
            self.display_plots_in_tabs(figures)

        except ValueError as e:
            print(f"Invalid input: {e}")

    def load_data(self, file_name=False):
        """Load data from a specified file or prompt the user to select one."""
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
            operation_point = self.simulator.compute_with_slicing()

            # Update output result labels with computed values
            self.result_labels["Q11:"].config(text=f"Q11: {operation_point.Q11:.2f}")
            self.result_labels["n11:"].config(text=f"n11: {operation_point.n11:.1f}")
            self.result_labels["Efficiency:"].config(text=f"Efficiency: {operation_point.efficiency:.2f}")
            self.result_labels["H:"].config(text=f"H: {operation_point.H:.2f}")
            self.result_labels["Power:"].config(text=f"Power: {operation_point.power:.0f}")

            # Update live plot data
            elapsed_time = time.time() - self.start_time
            self.time_data.append(elapsed_time)
            self.q11_data.append(operation_point.H)
            self.n11_data.append(operation_point.Q)
            self.efficiency_data.append(operation_point.blade_angle)
            self.h_data.append(operation_point.n)
            self.power_data.append(operation_point.power)

            # Update output result labels
            self.result_labels["Q11:"].config(text=f"Q11: {operation_point.Q11:.2f}")
            self.result_labels["n11:"].config(text=f"n11: {operation_point.n11:.1f}")
            self.result_labels["Efficiency:"].config(text=f"Efficiency: {operation_point.efficiency:.2f}")
            self.result_labels["H:"].config(text=f"H: {operation_point.H:.2f}")
            self.result_labels["Power:"].config(text=f"Power: {operation_point.power:.0f}")

            # Redraw the live plot with new data
            self.sub_plot_canvas.draw()

        except Exception as e:
            # Display error message on result labels in case of failure
            for key in self.result_labels:
                self.result_labels[key].config(text=f"{key} Error")
            print(f"An error occurred: {e}")
    
    def update_live_plot(self, frame):
            """Update the live plot with the latest data."""
            for ax in self.overview_ax:
                ax.clear()

            # Plot each variable in separate subplots
            self.overview_ax[0].plot(self.time_data, self.q11_data, label="H")
            self.overview_ax[0].set_ylabel("H")

            self.overview_ax[1].plot(self.time_data, self.n11_data, label="Q")
            self.overview_ax[1].set_ylabel("Q")

            self.overview_ax[2].plot(self.time_data, self.efficiency_data, label="Blade Angle")
            self.overview_ax[2].set_ylabel("Blade Angle")

            self.overview_ax[3].plot(self.time_data, self.h_data, label="n")
            self.overview_ax[3].set_ylabel("n")

            self.overview_ax[4].plot(self.time_data, self.power_data, label="Power")
            self.overview_ax[4].set_ylabel("Power")
            self.overview_ax[4].set_xlabel("Time (s)")

            # Set x-axis limit to last 30 seconds
            self.overview_ax[0].set_xlim(max(0, self.time_data[-1] - 30), self.time_data[-1])

            # Draw legends and apply tight layout
            for ax in self.overview_ax:
                ax.legend()
            self.overview_fig.tight_layout()

def main():
    simulator = TurbineControlSimulator()
    root = tk.Tk()
    app = TurbineControlSimulatorGUI(root, simulator)
    root.mainloop()

if __name__ == "__main__":
    main()
