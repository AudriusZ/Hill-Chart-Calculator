#To create standalon exe use the line below:
#pyinstaller --onefile --name Hill_Chart_Calculator_0.1.3 --icon=icon.ico Calculator.py

import tkinter as tk
from tkinter import messagebox, filedialog
from SingleCurve import SingleCurve
import copy
import matplotlib.pyplot as plt

print("Hello, this is a tool for hydro turbine scaling")

class HillChartCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Hill Chart Calculator')
        self.geometry("350x450")
        
        self.checkbox_vars = []
        self.checkboxes = []
        self.options = ["Head H [m]", "Flow rate Q [m^3/s]", "Rotational speed n [rpm]", "Runner diameter D [m]"]

        self.create_widgets()

        self.datapath = None  # Initially, no turbine data is selected
        # Bypass selection process for debugging        
        self.bypass_selection()
        
    def create_widgets(self):
        tk.Label(self, text="First, select the turbine:").pack()
        
        self.select_turbine_button = tk.Button(self, text="Select Turbine", command=self.load_turbine_data)
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

        self.calculate_button = tk.Button(self, text="Calculate", command=self.calculate, state='disabled')
        self.calculate_button.pack()

        self.result_text = tk.Text(self, height=10, width=40)
        self.result_text.pack()

    def create_checkbox(self, text, value):
        var = tk.IntVar()
        chk = tk.Checkbutton(self, text=text, variable=var, onvalue=value, offvalue=0, command=self.update_count, state='disabled')
        chk.pack(anchor=tk.W)
        self.checkbox_vars.append(var)
        self.checkboxes.append(chk)

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

    def calculate(self):
        try:
            var1 = float(self.var_entry_1.get())
            var2 = float(self.var_entry_2.get())
        except ValueError:
            messagebox.showerror("Input error", "Please enter valid numbers.")
            return
        
        hill_values = SingleCurve()
        hill_values.read_hill_chart_values(self.datapath)
        raw_data = copy.deepcopy(hill_values)
        BEP_values = copy.deepcopy(hill_values)
        BEP_values.filter_for_maximum_efficiency()
        BEP_values.calculate_cases([var.get() for var in self.checkbox_vars if var.get() != 0], var1, var2)
        BEP_data = BEP_values.return_values()        
        hill_values.prepare_hill_chart_data()
        
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Plot both the surface and scatter on the same axis
        hill_values.plot_hill_chart(ax=ax)
        raw_data.plot_3d_scatter(ax=ax)

        plt.show(block=False)    
                
        _, axs = plt.subplots(1, 2, figsize=(15, 7))  # Adjust size and layout as needed
         # Adjust layout
        hill_values.plot_hill_chart_contour(ax=axs[0], data_type='default')                 
        
        hill_values_nD = copy.deepcopy(hill_values)
        hill_values_nD.calculate_cases([1, 4], BEP_data.H[0], BEP_data.D[0])
        hill_values_nD.plot_hill_chart_contour(ax=axs[1], data_type='nD') 
        plt.tight_layout()
        plt.show(block=False)
        
        
        q_curve_values = copy.deepcopy(hill_values)
        q_curve_values.slice_hill_chart_data(selected_n11=BEP_data.n11[0],selected_Q11=None)        
        q_curve_values.calculate_cases([3, 4], BEP_data.n[0], BEP_data.D[0])
        
        _, axs2 = plt.subplots(2, 2, figsize=(15, 10))  # Adjust size and layout as needed

        q_curve_values.plot_efficiency_vs_Q(ax=axs2[0,0])
        q_curve_values.plot_power_vs_Q(ax=axs2[1,0])

        n_curve_values = copy.deepcopy(hill_values)
        n_curve_values.slice_hill_chart_data(selected_n11=None,selected_Q11=BEP_data.Q11[0])        
        n_curve_values.calculate_cases([2, 4], BEP_data.Q[0], BEP_data.D[0])

        n_curve_values.plot_efficiency_vs_n(ax=axs2[0,1])
        n_curve_values.plot_power_vs_n(ax=axs2[1,1])

        #plt.tight_layout()
        plt.show(block=False)        

        # Clear previous results
        self.result_text.delete(1.0, tk.END)
        print("Cleared previous BEP text data")
        
        # Display new results for each index in the lists
        num_sets = len(BEP_data.H)  # Assuming all lists are of the same length
        for index in range(num_sets):
            self.result_text.insert(tk.END, f"BEP values:\n")
            for attr in ['H', 'Q', 'n', 'D', 'efficiency', 'power']:
                value = getattr(BEP_data, attr)[index] if getattr(BEP_data, attr) else 'N/A'
                if isinstance(value, float):
                    value_format = f"{value:.2f}"
                else:
                    value_format = str(value)
                self.result_text.insert(tk.END, f"{attr} = {value_format}\n")
            self.result_text.insert(tk.END, "\n")  # Add a newline for spacing between sets 
        print("Displayed new BEP text data")

    def load_turbine_data(self):
        file_path = filedialog.askopenfilename(title="Select Turbine Data File", filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.datapath = file_path
            print(f"Loaded data from {file_path}")
            # Enable the checkboxes now that a turbine file is selected
            for chk in self.checkboxes:
                chk.config(state='normal')

    def bypass_selection(self):
        # Directly set the selected options and input values
        self.datapath = 'D_Liszka_et_al_turbine.csv'
        self.checkbox_vars[0].set(1)  # Select "Head H [m]"
        self.checkbox_vars[3].set(4)  # Select "Runner diameter D [m]"
        self.set_inputs()
        self.var_entry_1.insert(0, '2.15')  # Set value for "Head H [m]"
        self.var_entry_2.insert(0, '1.65')  # Set value for "Runner diameter D [m]"
        self.calculate_button.config(state='normal')
        self.calculate()

if __name__ == "__main__":
    app = HillChartCalculator()
    app.mainloop()
