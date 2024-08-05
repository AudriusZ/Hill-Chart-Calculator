import tkinter as tk
from tkinter import messagebox, filedialog
from HillChart import HillChart
import matplotlib.pyplot as plt

print("Hello, this is a tool for hydro turbine scaling")

class HillChartCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Hill Chart Calculator')
        self.geometry("350x700")  
        
        self.checkbox_vars = []
        self.checkboxes = []
        self.options = ["Head H [m]", "Flow rate Q [m^3/s]", "Rotational speed n [rpm]", "Runner diameter D [m]"]

        self.output_options = ["3D Hill Chart", "Hill Chart Contour", "2D Curve Slices", 'normalized Hill Chart Contour', "normalized 2D Curve Slices"]
        self.output_vars = [tk.IntVar() for _ in self.output_options]

        self.n_contours = 25  # Default value

        self.create_widgets()

        self.datapath = None  # Initially, no turbine data is selected
        # Bypass selection process for debugging        
        # self.bypass_selection()
        
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

        # Widgets for setting n_contours
        tk.Label(self, text="\nSet number of contours:").pack()
        self.n_contours_entry = tk.Entry(self)
        self.n_contours_entry.pack()
        self.n_contours_entry.insert(0, str(self.n_contours))  # Set default value
        #self.set_contours_button = tk.Button(self, text="Set Contours", command=self.set_n_contours)
        #self.set_contours_button.pack()

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

    def update_count(self):
        if self.datapath:  # Ensure that turbine data has been selected
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
            # Enable the checkboxes now that a turbine file is selected
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
            self.plot_curve_slices(BEP_data)

        if self.output_vars[3].get():
            self.plot_normalized_hill_chart_contour(hill_values, BEP_data)

        if self.output_vars[4].get():
            self.plot_normalized_curve_slices(BEP_data)
        
        self.display_results(BEP_data)

    def prepare_core_data(self, var1, var2):
        BEP_values = HillChart()
        BEP_values.read_hill_chart_values(self.datapath)        
        BEP_values.filter_for_maximum_efficiency()
        BEP_values.calculate_cases([var.get() for var in self.checkbox_vars if var.get() != 0], var1, var2)
        BEP_data = BEP_values.return_values()
        
        hill_values = HillChart()
        hill_values.read_hill_chart_values(self.datapath)
        hill_values.prepare_hill_chart_data()
        
        
        return BEP_data, hill_values

    def plot_3d_hill_chart(self, hill_values):
        fig = plt.figure()
        ax1 = fig.add_subplot(111, projection='3d')        
        hill_values.plot_hill_chart(ax=ax1)
        raw_data = HillChart()
        raw_data.read_hill_chart_values(self.datapath)
        raw_data.plot_3d_scatter(ax=ax1)
        plt.show(block=False)

    def plot_hill_chart_contour(self, hill_values, BEP_data):
        hill_values_nD = HillChart()
        hill_values_nD.read_hill_chart_values(self.datapath)
        hill_values_nD.prepare_hill_chart_data()
        _, ax2 = plt.subplots(1, 2, figsize=(15, 7))        
        hill_values.plot_hill_chart_contour(ax=ax2[0], n_contours=self.n_contours, data_type='default')                 
        hill_values_nD.calculate_cases([1, 4], BEP_data.H[0], BEP_data.D[0])
        hill_values_nD.plot_hill_chart_contour(ax=ax2[1], n_contours=self.n_contours, data_type='nD') 
        plt.tight_layout()
        plt.show(block=False)

    def plot_normalized_hill_chart_contour(self, hill_values, BEP_data):
        hill_values_norm = HillChart()
        hill_values_norm.read_hill_chart_values(self.datapath)
        hill_values_norm.prepare_hill_chart_data()
        hill_values_norm.normalize_efficiency(BEP_data.efficiency)
        hill_values_norm.normalize_Q11(BEP_data.Q11)
        hill_values_norm.normalize_n11(BEP_data.n11)
        _, ax2 = plt.subplots(1, 2, figsize=(15, 7))        
        hill_values.plot_hill_chart_contour(ax=ax2[0],n_contours=self.n_contours, data_type='default')                         
        hill_values_norm.plot_hill_chart_contour(ax=ax2[1],n_contours=self.n_contours, data_type='normalized') 
        plt.tight_layout()
        plt.show(block=False)

    def plot_curve_slices(self, BEP_data):
        _, ax3 = plt.subplots(2, 2, figsize=(15, 10))  # Adjust size and layout as needed
        q_curve_values = HillChart()
        q_curve_values.read_hill_chart_values(self.datapath)
        q_curve_values.prepare_hill_chart_data()          
        q_curve_values.slice_hill_chart_data(selected_n11=BEP_data.n11[0], selected_Q11=None)        
        q_curve_values.calculate_cases([3, 4], BEP_data.n[0], BEP_data.D[0])                    
        q_curve_values.plot_efficiency_vs_Q(ax=ax3[0,0])
        q_curve_values.plot_power_vs_Q(ax=ax3[1,0])

        n_curve_values = HillChart()
        n_curve_values.read_hill_chart_values(self.datapath)
        n_curve_values.prepare_hill_chart_data()          
        n_curve_values.slice_hill_chart_data(selected_n11=None, selected_Q11=BEP_data.Q11[0])        
        n_curve_values.calculate_cases([2, 4], BEP_data.Q[0], BEP_data.D[0])
        n_curve_values.plot_efficiency_vs_n(ax=ax3[0,1])
        n_curve_values.plot_power_vs_n(ax=ax3[1,1])
        
        plt.show(block=False)

    def plot_normalized_curve_slices(self, BEP_data):
        _, ax3 = plt.subplots(2, 2, figsize=(15, 10))  # Adjust size and layout as needed
        q_curve_values = HillChart()
        q_curve_values.read_hill_chart_values(self.datapath)
        q_curve_values.prepare_hill_chart_data()          
        q_curve_values.slice_hill_chart_data(selected_n11=BEP_data.n11[0], selected_Q11=None)        
        q_curve_values.calculate_cases([3, 4], BEP_data.n[0], BEP_data.D[0])            
        q_curve_values.normalize_efficiency(BEP_data.efficiency)       
        q_curve_values.normalize_Q(BEP_data.Q)               
        q_curve_values.normalize_power(BEP_data.power)
        q_curve_values.plot_efficiency_vs_Q(ax=ax3[0,0],labels='normalized')
        q_curve_values.plot_power_vs_Q(ax=ax3[1,0],labels='normalized')

        n_curve_values = HillChart()
        n_curve_values.read_hill_chart_values(self.datapath)
        n_curve_values.prepare_hill_chart_data()          
        n_curve_values.slice_hill_chart_data(selected_n11=None, selected_Q11=BEP_data.Q11[0])        
        n_curve_values.calculate_cases([2, 4], BEP_data.Q[0], BEP_data.D[0])
        n_curve_values.normalize_efficiency(BEP_data.efficiency)               
        n_curve_values.normalize_n(BEP_data.n)       
        n_curve_values.normalize_power(BEP_data.power)
        n_curve_values.plot_efficiency_vs_n(ax=ax3[0,1],labels='normalized')
        n_curve_values.plot_power_vs_n(ax=ax3[1,1],labels='normalized')
        
        plt.show(block=False)

    def display_results(self, BEP_data):
        # Clear previous results
        self.result_text.delete(1.0, tk.END)
        print("Cleared previous BEP text data")
        
        # Display new results for each index in the lists
        num_sets = len(BEP_data.H)  # Assuming all lists are of the same length
        for index in range(num_sets):
            self.result_text.insert(tk.END, f"BEP values:\n")
            for attr in ['H', 'Q', 'n', 'D', 'efficiency', 'power','Ns']:
                value = getattr(BEP_data, attr)[index] if getattr(BEP_data, attr) else 'N/A'
                if isinstance(value, float):
                    value_format = f"{value:.2f}"
                else:
                    value_format = str(value)
                self.result_text.insert(tk.END, f"{attr} = {value_format}\n")
            self.result_text.insert(tk.END, "\n")  # Add a newline for spacing between sets 
        print("Displayed new BEP text data")


    def bypass_selection(self):
        # Directly set the selected options and input values - for debugging
        self.datapath = 'D_Liszka_et_al_turbine.csv'
        self.checkbox_vars[0].set(1)  # Select "Head H [m]"
        self.checkbox_vars[3].set(4)  # Select "Runner diameter D [m]"
        self.set_inputs()
        self.var_entry_1.insert(0, '2.15')  # Set value for "Head H [m]"
        self.var_entry_2.insert(0, '1.65')  # Set value for "Runner diameter D [m]"
        self.calculate_button.config(state='normal')
        self.generate_outputs()

if __name__ == "__main__":
    app = HillChartCalculator()
    app.mainloop()
