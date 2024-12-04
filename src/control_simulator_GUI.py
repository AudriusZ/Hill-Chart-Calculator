# Application packaging command:
# pyinstaller --onefile --name Turbine_Control_Simulator_0.3.0 --icon=icon.ico ControlSimulatorGUI.py

import tkinter as tk
from tkinter import filedialog, BooleanVar
from tkinter import ttk
import os
import numpy as np
from control_simulator import ControlSimulator
from turbine_data import TurbineData
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import time
from collections import deque
from matplotlib.animation import FuncAnimation
import control_rule_based

class ControlSimulatorGUI:
    """GUI class for the Turbine Control Simulator application, built with tkinter."""

    def __init__(self, master, simulator):
        self.master = master
        self.simulator = simulator
        self.update_delay = 100  # Delay time in milliseconds for updating outputs
        self.update_id = None
        self.data_loaded = False  # Track if data has been successfully loaded

        # Store previous values for change detection
        self.prev_q = None
        self.prev_blade_angle = None
        self.prev_n = None
        self.prev_H_target = None        

        self.prev_H = None

        # Set up the main window title
        self.master.title("Turbine Control Simulator")

        # Button to load data file (CSV)
        self.load_data_button = tk.Button(master, text="Load Data", command=self.load_data)
        self.load_data_button.grid(row=0, column=0, columnspan=1, padx=10, pady=10, sticky="ew")

        # Set up notebook for tabs
        self.notebook = ttk.Notebook(master)
        self.notebook.grid(row=0, column=3, rowspan=15, padx=10, pady=5, sticky="nsew")

        # Initialize the default Overview tab
        self.add_overview_tab()

        """*****************************************************
        In development frame
        *****************************************************"""
        # Create a labeled frame for the "In Development" section
        self.dev_section_frame = tk.LabelFrame(master, text="In Development", relief=tk.GROOVE, bd=2, padx=10, pady=10)
        self.dev_section_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # Add input fields for turbine parameters inside the labeled frame
        self.D_label = tk.Label(self.dev_section_frame, text="Runner D [m]:")
        self.D_label.grid(row=0, column=0, padx=10, pady=5)
        self.D_input = tk.Entry(self.dev_section_frame)
        self.D_input.grid(row=0, column=1, padx=10, pady=5)
        self.D_input.insert(0, "1.65")

        """*****************************************************
        Input Parameters frame
        *****************************************************"""
        # Create a labeled frame for the "Input Parameters" section
        self.inputs_frame = tk.LabelFrame(master, text="Input Parameters", relief=tk.GROOVE, bd=2, padx=10, pady=10)
        self.inputs_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # Target Head input field and activation checkbox inside the "Input Parameters" frame
        self.H_target_label = tk.Label(self.inputs_frame, text="Target H [m]:")
        self.H_target_label.grid(row=0, column=0, padx=10, pady=5)

        self.H_target_input = tk.Entry(self.inputs_frame)
        self.H_target_input.grid(row=0, column=1, padx=10, pady=5)
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

        # Checkbox for activating H_target_input field inside the frame
        self.activate_checkbox = tk.Checkbutton(
            self.inputs_frame, text="Activate", variable=self.activate_var, command=toggle_H_target
        )
        self.activate_checkbox.grid(row=0, column=2, padx=10, pady=5)

        # Flow Rate input inside the "Input Parameters" frame
        self.q_label = tk.Label(self.inputs_frame, text="Q [m³/s]:")
        self.q_label.grid(row=1, column=0, padx=10, pady=5)

        self.q_input = tk.Spinbox(
            self.inputs_frame, from_=0.0, to=10.0, increment=0.1, format="%.3f", width=18
        )
        self.q_input.grid(row=1, column=1, padx=10, pady=5)
        self.q_input.delete(0, tk.END)
        self.q_input.insert(0, "3.375")

        # Blade Angle input inside the "Input Parameters" frame
        self.blade_label = tk.Label(self.inputs_frame, text="Blade Angle [°]:")
        self.blade_label.grid(row=2, column=0, padx=10, pady=5)
        self.blade_input = tk.Entry(self.inputs_frame)
        self.blade_input.grid(row=2, column=1, padx=10, pady=5)
        self.blade_input.insert(0, "16.2")

        # Rotational Speed input inside the "Input Parameters" frame
        self.n_label = tk.Label(self.inputs_frame, text="n [rpm]:")
        self.n_label.grid(row=3, column=0, padx=10, pady=5)
        self.n_input = tk.Entry(self.inputs_frame)
        self.n_input.grid(row=3, column=1, padx=10, pady=5)
        self.n_input.insert(0, "113.5")

        """*****************************************************
        Output Parameters frame
        *****************************************************"""
        # Create a labeled frame for the "Output Parameters" section
        self.outputs_frame = tk.LabelFrame(master, text="Output Parameters", relief=tk.GROOVE, bd=2, padx=10, pady=10)
        self.outputs_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # Output labels for displaying computed results inside the "Output Parameters" frame
        self.result_labels = {}
        output_texts = [
            ("Q11 =", ""), 
            ("n11 =", ""), 
            ("Efficiency =", "[-]"), 
            ("H =", "[m]"), 
            ("Power =", "[W]")
        ]

        for idx, (label_text, unit_text) in enumerate(output_texts):
            # Label for the parameter name
            label = tk.Label(self.outputs_frame, text=label_text)
            label.grid(row=idx, column=0, padx=10, pady=5, sticky="w")
            
            # Label for the computed value, initially blank
            value_label = tk.Label(self.outputs_frame, text="--")
            value_label.grid(row=idx, column=1, padx=10, pady=5, sticky="w")
            self.result_labels[label_text] = value_label  # Store value labels for updating later

            # Label for the unit
            unit_label = tk.Label(self.outputs_frame, text=unit_text)
            unit_label.grid(row=idx, column=2, padx=10, pady=5, sticky="w")

        """*****************************************************
        End of frames
        *****************************************************"""
       
        # Button to maximize output, triggering the pop-up
        self.maximise_output_button = tk.Button(master, text="Maximise Output", command=self.open_range_prompt)
        self.maximise_output_button.grid(row=0, column=1, columnspan=1, padx=10, pady=10, sticky="ew")

        # Bind input fields to trigger output updates with debounce handling
        self.q_input.bind("<KeyRelease>", lambda event: self.update_output())
        self.blade_input.bind("<KeyRelease>", lambda event: self.update_output())
        self.n_input.bind("<KeyRelease>", lambda event: self.update_output())
        self.H_target_input.bind("<KeyRelease>", lambda event: self.update_output())                

        # Initialize figure and axis for the Overview Plots tab with 5 subplots
        """
        self.overview_fig, self.overview_ax = plt.subplots(5, 1, figsize=(6, 8), sharex=True)
        self.sub_plot_canvas = FigureCanvasTkAgg(self.overview_fig, master=self.sub_plot_tab)
        self.sub_plot_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        """

        # Setup for live plot data in the Overview Plots tab
        self.time_data = deque(maxlen=240)  # Store time points up to 120s
        self.H = deque(maxlen=240)
        self.Q = deque(maxlen=240)
        self.blade_angle = deque(maxlen=240)
        self.n = deque(maxlen=240)
        self.power = deque(maxlen=240)
        self.start_time = time.time()  # Track start time for elapsed time on x-axis

        # Initialize the live plot animation
        self.anim = FuncAnimation(self.overview_fig, self.update_live_plot, interval=500, cache_frame_data=False)


        # Automatically load default data file if present in the directory
        self.load_data(file_name=True)  # Load default file if available

        # Initial output update
        self.update_output()

        # Start the scheduled continuous update loop
        self.schedule_continuous_update()

    def schedule_continuous_update(self):
        """Schedules the continuous update for live plot data at regular intervals."""
        self.update_output()  # Update outputs and live plot data
        self.master.after(500, self.schedule_continuous_update)  # Repeat interval    

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
        ax.set_xlabel("Q [m^3/s]")
        ax.set_ylabel("Power [W]")
        ax.set_title("Power vs Q")

        # Display the plot on the second tab
        canvas = FigureCanvasTkAgg(fig, self.plot_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def add_overview_tab(self):
        """Add the default 'Overview Plots' tab with live plots."""
        # Create a new frame within the notebook for overview plots
        overview_tab = ttk.Frame(self.notebook)
        self.notebook.add(overview_tab, text="Overview Plots")
        
        # Initialize figure and axes for the overview plots
        self.overview_fig, self.overview_ax = plt.subplots(5, 1, figsize=(6, 8), sharex=True)
        self.sub_plot_canvas = FigureCanvasTkAgg(self.overview_fig, master=overview_tab)
        self.sub_plot_canvas.get_tk_widget().pack(fill="both", expand=True)   
        

    def add_plot_tab(self, title, fig):
        """Adds a new tab with a given figure (plot) to the notebook."""
        # Create a frame as a new tab
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=title)

        # Place the figure's canvas inside this tab
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

    def display_plots_in_tabs(self, figures):
        """Clear dynamically added tabs and add a new tab for each figure in the notebook."""
        # Remove all tabs except the first one (Overview Plots)
        while len(self.notebook.tabs()) > 1:
            self.notebook.forget(1)

        # Add a new tab for each figure in the provided dictionary
        for title, fig in figures.items():
            self.add_plot_tab(title, fig)

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
        submit_button = tk.Button(self.range_prompt, text="Submit", command=self.submit_ranges)
        submit_button.grid(row=5, column=0, columnspan=4, pady=10)

    def create_range_inputs(self, prompt):
        """Create input fields for Q_range, H_range, n_range, and blade_angle_range in the prompt window."""
        
        # Flow Rate Range (Q_range)
        tk.Label(prompt, text="Flow Rate Range (Q): Start").grid(row=0, column=0, padx=10, pady=5)
        self.q_start_input = tk.Entry(prompt)
        self.q_start_input.grid(row=0, column=1, padx=10, pady=5)
        self.q_start_input.insert(0, "0.5")
        
        tk.Label(prompt, text="Stop").grid(row=0, column=2, padx=10, pady=5)
        self.q_stop_input = tk.Entry(prompt)
        self.q_stop_input.grid(row=0, column=3, padx=10, pady=5)
        self.q_stop_input.insert(0, "4.5")
        
        tk.Label(prompt, text="Step").grid(row=0, column=4, padx=10, pady=5)
        self.q_step_input = tk.Entry(prompt)
        self.q_step_input.grid(row=0, column=5, padx=10, pady=5)
        self.q_step_input.insert(0, "0.5")
        
        # Head Range (H_range)
        tk.Label(prompt, text="Head Range (H): Min").grid(row=1, column=0, padx=10, pady=5)
        self.h_min_input = tk.Entry(prompt)
        self.h_min_input.grid(row=1, column=1, padx=10, pady=5)
        self.h_min_input.insert(0, "0.5")
        
        tk.Label(prompt, text="Max").grid(row=1, column=2, padx=10, pady=5)
        self.h_max_input = tk.Entry(prompt)
        self.h_max_input.grid(row=1, column=3, padx=10, pady=5)
        self.h_max_input.insert(0, "2.15")

        # Rotational Speed Range (n_range)
        tk.Label(prompt, text="Rotational Speed Range (n): Start").grid(row=2, column=0, padx=10, pady=5)
        self.n_start_input = tk.Entry(prompt)
        self.n_start_input.grid(row=2, column=1, padx=10, pady=5)
        self.n_start_input.insert(0, "40")
        
        tk.Label(prompt, text="Stop").grid(row=2, column=2, padx=10, pady=5)
        self.n_stop_input = tk.Entry(prompt)
        self.n_stop_input.grid(row=2, column=3, padx=10, pady=5)
        self.n_stop_input.insert(0, "150")
        
        tk.Label(prompt, text="Step").grid(row=2, column=4, padx=10, pady=5)
        self.n_step_input = tk.Entry(prompt)
        self.n_step_input.grid(row=2, column=5, padx=10, pady=5)
        self.n_step_input.insert(0, "5")

        # Blade Angle Range
        tk.Label(prompt, text="Blade Angle Range: Start").grid(row=3, column=0, padx=10, pady=5)
        self.blade_start_input = tk.Entry(prompt)
        self.blade_start_input.grid(row=3, column=1, padx=10, pady=5)
        self.blade_start_input.insert(0, "8")
        
        tk.Label(prompt, text="Stop").grid(row=3, column=2, padx=10, pady=5)
        self.blade_stop_input = tk.Entry(prompt)
        self.blade_stop_input.grid(row=3, column=3, padx=10, pady=5)
        self.blade_stop_input.insert(0, "21")
        
        tk.Label(prompt, text="Step").grid(row=3, column=4, padx=10, pady=5)
        self.blade_step_input = tk.Entry(prompt)
        self.blade_step_input.grid(row=3, column=5, padx=10, pady=5)
        self.blade_step_input.insert(0, "1")

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
        if file_name is True:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(script_dir, "Mogu_D1.65m.csv")
            if not os.path.exists(filepath):
                print("Default file not found. Please load the data file.")
                return
            else:
                print("Default file found. Loading data...")
        elif isinstance(file_name, str):
            filepath = file_name
            print(f"Loading specified file: {filepath}")
        else:
            filepath = filedialog.askopenfilename(
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
                title="Select Hill Chart Data File"
            )
            if not filepath:
                print("No file selected. Exiting load_data.")
                return
            print(f"User selected file: {filepath}")

        try:
            self.simulator.read_hill_chart_values(filepath)
            self.simulator.filter_for_maximum_efficiency(remove=False)
            self.simulator.prepare_hill_chart_data(min_efficiency_limit = 0.1)
            self.data_loaded = True
            print(f"Data successfully loaded from {filepath}")
            # GUI title update
            self.master.title(f"Turbine Control Simulator - Data Loaded: {os.path.basename(filepath)}")
            # Clear result labels
            for key in self.result_labels:
                self.result_labels[key].config(text=f"{key} --")
        except Exception as e:
            print(f"Error loading data from {filepath}: {e}")
            for key in self.result_labels:
                self.result_labels[key].config(text=f"{key} Error")




    def update_output(self):
        """Calculate and update output, also updating time-based data for live plots."""
        if not self.data_loaded:            
            return  # Exit if data is not loaded
        
        try:
            # Retrieve input values and parse them as floats
            Q = float(self.q_input.get())
            blade_angle = float(self.blade_input.get())
            n = float(self.n_input.get())
            D = float(self.D_input.get())
            head_control = bool(self.activate_var.get())
            H_target = float(self.H_target_input.get())
            H = self.prev_H

            """
            # Check for changes to avoid unnecessary updates
            if (
                Q == self.prev_q and
                blade_angle == self.prev_blade_angle and
                n == self.prev_n and
                not head_control
            ):
                return  # Skip update if values haven't changed
            """                      

            

            if head_control:                
                if (
                    Q == self.prev_q and
                    blade_angle == self.prev_blade_angle and
                    n == self.prev_n and
                    H_target == self.prev_H_target
                ):
                    return  # Skip update if values haven't changed                
                
                # Update stored previous values
                self.prev_q = Q
                self.prev_blade_angle = blade_angle
                self.prev_n = n 
                self.prev_H_target = H_target

                controller = control_rule_based.ControlRuleBased(H_tolerance=0.05, blade_angle_step=0.5, n_step=1)

                n_t = 113.5
                output = controller.control_step(H, H_target, n, n_t, blade_angle)
                n = output["n"]
                blade_angle = output["blade_angle"]
                """
                result = self.simulator.set_head_and_adjust(H_target)
                n = result["Rotational Speed (n)"]
                blade_angle = result["Blade Angle"]
                """


                self.simulator.set_operation_attribute("n", n)
                self.simulator.set_operation_attribute("blade_angle", blade_angle)
                self.blade_input.delete(0, tk.END)
                self.blade_input.insert(0, f"{blade_angle:.2f}")
                self.n_input.delete(0, tk.END)
                self.n_input.insert(0, f"{n:.2f}")

            # Compute results using the simulator
            operation_point = self.simulator.compute_with_slicing()

            self.prev_H = operation_point.H

            # Update time-based data for live plotting
            elapsed_time = time.time() - self.start_time
            self.time_data.append(elapsed_time)
            self.H.append(operation_point.H)
            self.Q.append(operation_point.Q)
            self.blade_angle.append(operation_point.blade_angle)
            self.n.append(operation_point.n)
            self.power.append(operation_point.power)

            # Update output result labels
            self.result_labels["Q11 ="].config(text=f"{operation_point.Q11:.2f} ")
            self.result_labels["n11 ="].config(text=f"{operation_point.n11:.1f}")
            self.result_labels["Efficiency ="].config(text=f"{operation_point.efficiency:.2f}")
            self.result_labels["H ="].config(text=f"{operation_point.H:.2f}")
            self.result_labels["Power ="].config(text=f"{operation_point.power:.0f}")

            # Redraw the live plot with new data
            self.update_live_plot(None)

        except Exception as e:
            # Display error message on result labels if calculation fails
            for key in self.result_labels:
                self.result_labels[key].config(text=f"{key} Error")
            print(f"An error occurred: {e}")
    
    def update_live_plot(self, frame):
        """Update the live plot with the latest time-based data."""
        if not self.data_loaded:
            return  # Skip updating live plot if data is not loaded
        
        for ax in self.overview_ax:
            ax.clear()

        # Plot each variable against time in separate subplots
        self.overview_ax[0].plot(self.time_data, self.H, label="H")
        self.overview_ax[0].set_ylabel("H [m]")

        self.overview_ax[1].plot(self.time_data, self.Q, label="Q")
        self.overview_ax[1].set_ylabel("Q [m^3/s]")

        self.overview_ax[2].plot(self.time_data, self.blade_angle, label="Blade Angle")
        self.overview_ax[2].set_ylabel("Blade Angle [°]")

        self.overview_ax[3].plot(self.time_data, self.n, label="n")
        self.overview_ax[3].set_ylabel("n [rpm]")

        self.overview_ax[4].plot(self.time_data, self.power, label="Power")
        self.overview_ax[4].set_ylabel("Power [W]")        

        # Determine x-axis limits based on the elapsed time
        if self.time_data and self.time_data[-1] > 120:
            # Shift the window to show only the last 120 seconds
            self.overview_ax[0].set_xlim(self.time_data[-1] - 120, self.time_data[-1])
        else:
            # Set x-axis limit to the initial 0 to 120 seconds
            self.overview_ax[0].set_xlim(0, 120)

        # Draw legends and apply tight layout        
        self.overview_fig.tight_layout()

        # Refresh the canvas to show updated plots
        self.sub_plot_canvas.draw()

def main():
    simulator = ControlSimulator()
    root = tk.Tk()
    app = ControlSimulatorGUI(root, simulator)
    root.mainloop()

if __name__ == "__main__":
    main()
