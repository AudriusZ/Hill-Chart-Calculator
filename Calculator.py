#To create standalon exe use the line below:
#pyinstaller --onefile --name Hill_Chart_Calculator_0.3.0 --icon=icon.ico Calculator.py

import tkinter as tk
from tkinter import messagebox, filedialog
from HillChart import HillChart  # Ensure HillChart module is available in the environment
import matplotlib.pyplot as plt
import copy
from HillChartProcessor import HillChartProcessor




print("Hello, this is a tool for hydro turbine scaling")

class HillChartCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Hill Chart Calculator')

        self.checkbox_vars = []
        self.checkboxes = []
        self.options = ["Head H [m]", "Flow rate Q [m^3/s]", "Rotational speed n [rpm]", "Runner diameter D [m]"]

        self.output_options = ["3D Hill Chart", "Hill Chart Contour", "2D Curve Slices", 'Normalized Hill Chart Contour', "Normalized 2D Curve Slices", "Best efficiency point summary"]
        self.output_vars = [tk.IntVar() for _ in self.output_options]

        self.extrapolation_options = ["Extrapolate unit speed n11 [rpm]", "Extrapolate Blade Angles [degree]"]
        self.extrapolation_options_vars = [tk.IntVar() for _ in self.extrapolation_options]
        self.extrapolation_entry_vars = []
        self.extrapolation_entries = []

        self.n_contours = 25  # Default value for contour lines

        # Instance variables for holding GUI inputs
        self.selected_values = [1, 4]
        self.var1 = None
        self.var2 = None
        self.extrapolation_values_n11 = [60, 200, 5]
        self.extrapolation_values_blade_angles = [-5, 8.8, 10]

        self.create_main_frame()
        self.datapath = None  # Initially, no turbine data is selected

    def create_main_frame(self):
        # Create a frame to contain the three side-by-side frames
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Configure grid columns and rows to expand
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Create and pack the three frames side by side
        self.create_input_param_widgets(main_frame)
        self.create_surface_fit_widgets(main_frame)
        self.create_output_options_widgets(main_frame)

    def create_input_param_widgets(self, parent):
        # Create a frame for input parameters
        input_frame = tk.LabelFrame(parent, text="Input Parameters", padx=10, pady=10, relief=tk.GROOVE, bd=2)
        input_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")  # Use grid layout
        
        # Configure input_frame to expand
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)

        # Load turbine performance data
        self.select_turbine_button = tk.Button(input_frame, text="Load Data", command=self.select_turbine_datafile)
        self.select_turbine_button.pack()

        # Create checkboxes for input parameters
        tk.Label(input_frame, text="\nInput parameters (select two):").pack()        
        for i, option in enumerate(self.options):
            self.create_input_param_checkbox(option, i + 1, parent=input_frame)

        # Create textboxes for input parameters
        self.var_label_1 = tk.Label(input_frame, text="Input value 1")
        self.var_label_1.pack()
        self.var_entry_1 = tk.Entry(input_frame, state='disabled')
        self.var_entry_1.pack()

        self.var_label_2 = tk.Label(input_frame, text="Input value 2")
        self.var_label_2.pack()
        self.var_entry_2 = tk.Entry(input_frame, state='disabled')
        self.var_entry_2.pack()

    def create_surface_fit_widgets(self, parent):
        # Create a frame for surface fit options
        surface_fit_frame = tk.LabelFrame(parent, text="Surface Fit Options", padx=10, pady=10, relief=tk.GROOVE, bd=2)
        surface_fit_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")  # Use grid layout
        
        # Configure surface_fit_frame to expand
        surface_fit_frame.columnconfigure(0, weight=1)
        surface_fit_frame.rowconfigure(0, weight=1)

        tk.Label(surface_fit_frame, text="\nSet number of contours:").pack()        
        self.n_contours_entry = tk.Entry(surface_fit_frame)
        self.n_contours_entry.pack()
        self.n_contours_entry.insert(0, str(self.n_contours))  # Set default value

        # Define entry labels for extrapolation checkboxes
        extrapolation_entry_labels = [
            ["Min", "Max", "Number of data points"],
            ["Min", "Max", "Number of data points"]
        ]

        for i, option in enumerate(self.extrapolation_options):
            self.create_extrapolation_checkbox(option, self.extrapolation_options_vars[i], extrapolation_entry_labels[i], parent=surface_fit_frame)

    def create_output_options_widgets(self, parent):
        # Create a frame for output options
        output_frame = tk.LabelFrame(parent, text="Output Options", padx=10, pady=10, relief=tk.GROOVE, bd=2)
        output_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")  # Use grid layout
        
        # Configure output_frame to expand
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        for i, output_option in enumerate(self.output_options):
            self.create_output_checkbox(output_option, self.output_vars[i], parent=output_frame)

        self.calculate_button = tk.Button(output_frame, text="Calculate", command=self.generate_outputs, state='disabled')
        self.calculate_button.pack()
 


    def create_input_param_checkbox(self, text, value, parent):
        var = tk.IntVar()
        chk = tk.Checkbutton(parent, text=text, variable=var, onvalue=value, offvalue=0, command=self.update_count, state='disabled')
        chk.pack(anchor=tk.W)
        self.checkbox_vars.append(var)
        self.checkboxes.append(chk)
    
    def create_output_checkbox(self, text, var, parent):
        chk = tk.Checkbutton(parent, text=text, variable=var, onvalue=1, offvalue=0)
        chk.pack(anchor=tk.W)
        

    def create_extrapolation_checkbox(self, text, var, entry_labels, parent):
        # Create the Checkbutton
        chk = tk.Checkbutton(parent, text=text, variable=var, onvalue=1, offvalue=0, command=lambda: self.toggle_entries(var))
        chk.pack(anchor=tk.W)
        
        # Create entries for the checkbox
        entries_frame = tk.Frame(parent)
        entries_frame.pack(anchor=tk.W)
        
        entry_vars = [tk.StringVar() for _ in entry_labels]
        self.extrapolation_entry_vars.append(entry_vars)  # Store entry variables
        self.extrapolation_entries.append(entries_frame)   # Store entry frames
        
        for label, entry_var in zip(entry_labels, entry_vars):
            tk.Label(entries_frame, text=label).pack(anchor=tk.W)
            entry = tk.Entry(entries_frame, textvariable=entry_var, state='disabled')
            entry.pack(anchor=tk.W)


    def toggle_entries(self, var):
        state = 'normal' if var.get() == 1 else 'disabled'
        index = self.extrapolation_options_vars.index(var)
        for entry in self.extrapolation_entries[index].winfo_children():
            entry.config(state=state)

    def update_count(self):
        if self.datapath:
            selected_values = [var.get() for var in self.checkbox_vars if var.get() != 0]
            selected_count = len(selected_values)
            if selected_count == 2:
                for var, chk in zip(self.checkbox_vars, self.checkboxes):
                    chk.config(state='disabled' if var.get() == 0 else 'normal')                
                self.set_input_parameters()
            else:
                for chk in self.checkboxes:
                    chk.config(state='normal')                
                self.set_input_parameters('disabled')

    def set_input_parameters(self, state='normal'):
        if state == 'normal':
            self.selected_values = [var.get() for var in self.checkbox_vars if var.get() != 0]
            self.var_entry_1.config(state='normal')
            self.var_entry_2.config(state='normal')
            self.var_label_1.config(text=self.options[self.selected_values[0] - 1])
            self.var_label_2.config(text=self.options[self.selected_values[1] - 1])
            self.calculate_button.config(state='normal')
        else:
            self.var_entry_1.config(state='disabled')
            self.var_entry_2.config(state='disabled')

    def select_turbine_datafile(self):
        file_path = filedialog.askopenfilename(title="Select Turbine Data File", filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.datapath = file_path
            print(f"Loaded data from {file_path}")
            for chk in self.checkboxes:
                chk.config(state='normal')

    def set_n_contours(self):
        try:
            self.n_contours = int(self.n_contours_entry.get())
        except ValueError:
            messagebox.showerror("Input error", "Please enter a valid integer for the number of contours.")

    def generate_outputs(self):
        # Gather all GUI inputs before processing
        self.set_n_contours()
        
        
        self.get_selected_values()
        self.get_extrapolation_values()
        
        plot_processor = HillChartProcessor()
        plot_processor.get_file_path(self.datapath)
        plot_processor.get_turbine_parameters(self.selected_values, self.var1, self.var2)
        plot_processor.get_plot_parameters(self.n_contours,[self.extrapolation_options_vars[0].get(),self.extrapolation_options_vars[1].get()],self.extrapolation_values_n11,self.extrapolation_values_blade_angles)
        plot_options = [var.get() for var in self.output_vars]
        plot_processor.get_output_parameters(plot_options)        
        plot_processor.generate_outputs()        

    def get_selected_values(self):
        try:
            self.var1 = float(self.var_entry_1.get())
            self.var2 = float(self.var_entry_2.get())
        except ValueError:
            messagebox.showerror("Input error", "Please enter valid numbers.")
            return

    def get_extrapolation_values(self):
        
        
        if self.extrapolation_options_vars[0].get():  # Extrapolate unit speed n11 [rpm]
            self.extrapolation_values_n11 = [float(var.get()) for var in self.extrapolation_entry_vars[0]]
            self.extrapolation_values_n11[2] = int(self.extrapolation_values_n11[2])

        if self.extrapolation_options_vars[1].get():  # Extrapolate Blade Angles [degree]
            self.extrapolation_values_blade_angles = [float(var.get()) for var in self.extrapolation_entry_vars[1]]
            self.extrapolation_values_blade_angles[2] = int(self.extrapolation_values_blade_angles[2])              

if __name__ == "__main__":
    app = HillChartCalculator()
    app.mainloop()
