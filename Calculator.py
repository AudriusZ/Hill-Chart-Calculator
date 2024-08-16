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
        self.geometry("350x850")

        self.checkbox_vars = []
        self.checkboxes = []
        self.options = ["Head H [m]", "Flow rate Q [m^3/s]", "Rotational speed n [rpm]", "Runner diameter D [m]"]

        self.output_options = ["3D Hill Chart", "Hill Chart Contour", "2D Curve Slices", 'normalized Hill Chart Contour', "normalized 2D Curve Slices"]
        self.output_vars = [tk.IntVar() for _ in self.output_options]

        self.extrapolation_options = ["Extrapolate unit speed n11 [rpm]", "Extrapolate Blade Angles [degree]"]
        self.extrapolation_options_vars = [tk.IntVar() for _ in self.extrapolation_options]
        self.extrapolation_entry_vars = []
        self.extrapolation_entries = []

        self.n_contours = 25  # Default value for contour lines

        # Instance variables for holding GUI inputs
        self.selected_values = []
        self.var1 = None
        self.var2 = None
        self.extrapolation_values_n11 = []
        self.extrapolation_values_blade_angles = []

        self.create_widgets()
        self.datapath = None  # Initially, no turbine data is selected
        
    def create_widgets(self):
        tk.Label(self, text="First, select the turbine:").pack()
        
        self.select_turbine_button = tk.Button(self, text="Select Turbine", command=self.select_turbine_datafile)
        self.select_turbine_button.pack()
        
        tk.Label(self, text="\nThen, select two parameters and press Next:").pack()
        
        for i, option in enumerate(self.options):
            self.create_checkbox(option, i + 1)
        
        self.next_button = tk.Button(self, text="Next", command=self.set_inputs, state='disabled')
        self.next_button.pack()

        self.var_label_1 = tk.Label(self, text="Input value 1")
        self.var_label_1.pack()
        self.var_entry_1 = tk.Entry(self, state='disabled')
        self.var_entry_1.pack()

        self.var_label_2 = tk.Label(self, text="Input value 2")
        self.var_label_2.pack()
        self.var_entry_2 = tk.Entry(self, state='disabled')
        self.var_entry_2.pack()

        tk.Label(self, text="\nSelect the outputs you want to see:").pack()

        for i, output_option in enumerate(self.output_options):
            self.create_output_checkbox(output_option, self.output_vars[i])

        tk.Label(self, text="\nSet number of contours:").pack()
        self.n_contours_entry = tk.Entry(self)
        self.n_contours_entry.pack()
        self.n_contours_entry.insert(0, str(self.n_contours))  # Set default value
        
        # Define entry labels for extrapolation checkboxes
        extrapolation_entry_labels = [
            ["Min", "Max", "Number of data points"],
            ["Min", "Max", "Number of data points"]
        ]

        for i, option in enumerate(self.extrapolation_options):
            self.create_extrapolation_checkbox(option, self.extrapolation_options_vars[i], extrapolation_entry_labels[i])

        self.calculate_button = tk.Button(self, text="Calculate", command=self.generate_outputs, state='disabled')
        self.calculate_button.pack()

        self.result_text = tk.Text(self, height=10, width=40)
        self.result_text.pack()


    def create_checkbox(self, text, value):
        var = tk.IntVar()
        chk = tk.Checkbutton(self, text=text, variable=var, onvalue=value, offvalue=0, command=self.update_count, state='disabled')
        chk.pack(anchor=tk.W)
        self.checkbox_vars.append(var)
        self.checkboxes.append(chk)
    
    def create_output_checkbox(self, text, var):
        chk = tk.Checkbutton(self, text=text, variable=var, onvalue=1, offvalue=0)
        chk.pack(anchor=tk.W)

    def create_extrapolation_checkbox(self, text, var, entry_labels):
        # Create the Checkbutton
        chk = tk.Checkbutton(self, text=text, variable=var, onvalue=1, offvalue=0, command=lambda: self.toggle_entries(var, entry_labels))
        chk.pack(anchor=tk.W)
        
        # Create entries for the checkbox
        entries_frame = tk.Frame(self)
        entries_frame.pack(anchor=tk.W)
        
        entry_vars = [tk.StringVar() for _ in entry_labels]
        self.extrapolation_entry_vars.append(entry_vars)  # Store entry variables
        self.extrapolation_entries.append(entries_frame)   # Store entry frames
        
        for label, entry_var in zip(entry_labels, entry_vars):
            tk.Label(entries_frame, text=label).pack(anchor=tk.W)
            entry = tk.Entry(entries_frame, textvariable=entry_var, state='disabled')
            entry.pack(anchor=tk.W)    
    
    def toggle_entries(self, var, entry_labels):
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
                self.next_button.config(state='normal')
            else:
                for chk in self.checkboxes:
                    chk.config(state='normal')
                self.next_button.config(state='disabled')

    def set_inputs(self):
        self.selected_values = [var.get() for var in self.checkbox_vars if var.get() != 0]
        self.var_entry_1.config(state='normal')
        self.var_entry_2.config(state='normal')
        self.var_label_1.config(text=self.options[self.selected_values[0] - 1])
        self.var_label_2.config(text=self.options[self.selected_values[1] - 1])
        self.calculate_button.config(state='normal')

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

    def display_results(self, BEP_data):
        self.result_text.delete(1.0, tk.END)
        print("Cleared previous BEP text data")
        
        num_sets = len(BEP_data.H)  
        for index in range(num_sets):
            self.result_text.insert(tk.END, f"BEP values:\n")
            for attr in ['H', 'Q', 'n', 'D', 'efficiency', 'power','Ns']:
                value = getattr(BEP_data, attr)[index] if getattr(BEP_data, attr) else 'N/A'
                if isinstance(value, float):
                    value_format = f"{value:.2f}"
                else:
                    value_format = str(value)
                self.result_text.insert(tk.END, f"{attr} = {value_format}\n")
            self.result_text.insert(tk.END, "\n")
        print("Displayed new BEP text data")    

if __name__ == "__main__":
    app = HillChartCalculator()
    app.mainloop()
