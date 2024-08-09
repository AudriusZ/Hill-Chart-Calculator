#To create standalon exe use the line below:
#pyinstaller --onefile --name Hill_Chart_Calculator_0.3.0 --icon=icon.ico Calculator.py

import tkinter as tk
from tkinter import messagebox, filedialog
from HillChart import HillChart  # Ensure HillChart module is available in the environment
import matplotlib.pyplot as plt
import copy



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

        self.extrapolation_options = ["Extrapolate unit speed n11 [rpm]","Extrapolate Blade Angles [degree]"]
        self.extrapolation_options_vars = [tk.IntVar() for _ in self.extrapolation_options]
        self.extrapolation_entry_vars = []
        self.extrapolation_entries = []

        self.n_contours = 25  # Default value for contour lines

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
        selected_values = [var.get() for var in self.checkbox_vars if var.get() != 0]
        self.var_entry_1.config(state='normal')
        self.var_entry_2.config(state='normal')
        self.var_label_1.config(text=self.options[selected_values[0]-1])
        self.var_label_2.config(text=self.options[selected_values[1]-1])
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
        try:
            var1 = float(self.var_entry_1.get())
            var2 = float(self.var_entry_2.get())
        except ValueError:
            messagebox.showerror("Input error", "Please enter valid numbers.")
            return
        self.set_n_contours()

        BEP_data, hill_values = self.prepare_core_data(var1, var2)
        
        if self.output_vars[0].get():
            self.plot_3d_hill_chart(hill_values)
        
        if self.output_vars[1].get():
            self.plot_hill_chart_contour(hill_values, BEP_data)
        
        if self.output_vars[2].get():
            self.plot_curve_slices(hill_values, BEP_data)

        if self.output_vars[3].get():
            self.plot_normalized_hill_chart_contour(hill_values, BEP_data)

        if self.output_vars[4].get():
            self.plot_normalized_curve_slices(hill_values, BEP_data)
        
        self.display_results(BEP_data)

    def prepare_core_data(self, var1, var2):
        BEP_values = HillChart()
        BEP_values.read_hill_chart_values(self.datapath)        
        BEP_values.filter_for_maximum_efficiency()
        BEP_values.calculate_cases([var.get() for var in self.checkbox_vars if var.get() != 0], var1, var2)
        BEP_data = BEP_values.return_values()
        
        hill_values = HillChart()
        hill_values.read_hill_chart_values(self.datapath)                
        
        
        if self.extrapolation_options_vars[0].get():  # Check if "Extrapolate unit speed n11 [rpm]" is selected                        
            entry_values = [float(var.get()) for var in self.extrapolation_entry_vars[0]]            
            entry_values[2] = int(entry_values[2])
            hill_values.extrapolate_along_n11(min_n11=entry_values[0],max_n11=entry_values[1],n_n11=entry_values[2])

        if self.extrapolation_options_vars[1].get():  # Check if "Extrapolate Blade Angles [degree]" is selected
            entry_values = [float(var.get()) for var in self.extrapolation_entry_vars[1]]            
            entry_values[2] = int(entry_values[2])
            hill_values.extrapolate_along_blade_angles(min_angle=entry_values[0],max_angle=entry_values[1],n_angle=entry_values[2])
        
        
        hill_values.prepare_hill_chart_data()
        
        return BEP_data, hill_values

    def plot_3d_hill_chart(self, hill_values):
        fig = plt.figure()
        ax1 = fig.add_subplot(111, projection='3d')        
        hill_values.plot_hill_chart(ax=ax1)
        raw_data = HillChart()
        raw_data.read_hill_chart_values(self.datapath)        

        '''
        if self.extrapolation_options_vars[0].get():  # Check if "Extrapolate unit speed n11 [rpm]" is selected                        
            entry_values = [float(var.get()) for var in self.extrapolation_entry_vars[0]]            
            entry_values[2] = int(entry_values[2])
            raw_data.extrapolate_along_n11(min_n11=entry_values[0],max_n11=entry_values[1],n_n11=entry_values[2])

        if self.extrapolation_options_vars[1].get():  # Check if "Extrapolate Blade Angles [degree]" is selected
            entry_values = [float(var.get()) for var in self.extrapolation_entry_vars[1]]            
            entry_values[2] = int(entry_values[2])
            raw_data.extrapolate_along_blade_angles(min_angle=entry_values[0],max_angle=entry_values[1],n_angle=entry_values[2])
        '''
        raw_data.plot_3d_scatter(ax=ax1)
        plt.show(block=False)

    def plot_hill_chart_contour(self, hill_values, BEP_data):
        hill_values_nD = copy.deepcopy(hill_values)        
        _, ax2 = plt.subplots(1, 2, figsize=(15, 7))        
        hill_values.plot_hill_chart_contour(ax=ax2[0], n_contours=self.n_contours, data_type='default')                 
        hill_values_nD.calculate_cases([1, 4], BEP_data.H[0], BEP_data.D[0])
        hill_values_nD.plot_hill_chart_contour(ax=ax2[1], n_contours=self.n_contours, data_type='nD') 
        plt.tight_layout()
        plt.show(block=False)

    def plot_normalized_hill_chart_contour(self, hill_values, BEP_data):
        hill_values_norm = copy.deepcopy(hill_values)        
        hill_values_norm.normalize_efficiency(BEP_data.efficiency)
        hill_values_norm.normalize_Q11(BEP_data.Q11)
        hill_values_norm.normalize_n11(BEP_data.n11)
        _, ax2 = plt.subplots(1, 2, figsize=(15, 7))        
        hill_values.plot_hill_chart_contour(ax=ax2[0],n_contours=self.n_contours, data_type='default')                         
        hill_values_norm.plot_hill_chart_contour(ax=ax2[1],n_contours=self.n_contours, data_type='normalized') 
        plt.tight_layout()
        plt.show(block=False)

    def plot_curve_slices(self, hill_values, BEP_data):
        _, ax3 = plt.subplots(2, 2, figsize=(15, 10))  
        q_curve_values = copy.deepcopy(hill_values)        
        q_curve_values.slice_hill_chart_data(selected_n11=BEP_data.n11[0], selected_Q11=None)        
        q_curve_values.calculate_cases([3, 4], BEP_data.n[0], BEP_data.D[0])                    
        q_curve_values.plot_efficiency_vs_Q(ax=ax3[0,0])
        q_curve_values.plot_power_vs_Q(ax=ax3[1,0])

        n_curve_values = copy.deepcopy(hill_values)        
        n_curve_values.slice_hill_chart_data(selected_n11=None, selected_Q11=BEP_data.Q11[0])        
        n_curve_values.calculate_cases([2, 4], BEP_data.Q[0], BEP_data.D[0])
        n_curve_values.plot_efficiency_vs_n(ax=ax3[0,1])
        n_curve_values.plot_power_vs_n(ax=ax3[1,1])
        
        plt.show(block=False)

    def plot_normalized_curve_slices(self, hill_values, BEP_data):
        _, ax3 = plt.subplots(2, 2, figsize=(15, 10))  
        q_curve_values = copy.deepcopy(hill_values)        
        q_curve_values.slice_hill_chart_data(selected_n11=BEP_data.n11[0], selected_Q11=None)        
        q_curve_values.calculate_cases([3, 4], BEP_data.n[0], BEP_data.D[0])            
        q_curve_values.normalize_efficiency(BEP_data.efficiency)       
        q_curve_values.normalize_Q(BEP_data.Q)               
        q_curve_values.normalize_power(BEP_data.power)
        q_curve_values.plot_efficiency_vs_Q(ax=ax3[0,0], labels='normalized')
        q_curve_values.plot_power_vs_Q(ax=ax3[1,0], labels='normalized')

        n_curve_values = copy.deepcopy(hill_values)        
        n_curve_values.slice_hill_chart_data(selected_n11=None, selected_Q11=BEP_data.Q11[0])        
        n_curve_values.calculate_cases([2, 4], BEP_data.Q[0], BEP_data.D[0])
        n_curve_values.normalize_efficiency(BEP_data.efficiency)               
        n_curve_values.normalize_n(BEP_data.n)       
        n_curve_values.normalize_power(BEP_data.power)
        n_curve_values.plot_efficiency_vs_n(ax=ax3[0,1], labels='normalized')
        n_curve_values.plot_power_vs_n(ax=ax3[1,1], labels='normalized')
        
        plt.show(block=False)

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

    def bypass_selection(self):
        self.datapath = 'Mogu_D1.65m.csv'
        self.checkbox_vars[0].set(1)  
        self.checkbox_vars[3].set(4)  
        self.set_inputs()
        self.var_entry_1.insert(0, '2.15')  
        self.var_entry_2.insert(0, '1.65')  
        self.calculate_button.config(state='normal')
        self.generate_outputs()

if __name__ == "__main__":
    app = HillChartCalculator()
    app.mainloop()
