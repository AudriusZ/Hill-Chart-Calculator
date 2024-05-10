import tkinter as tk
from tkinter import messagebox
from SingleCurve import SingleCurve

class HillChartCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Hill Chart Calculator')
        self.geometry("350x350")
        
        self.checkbox_vars = []
        self.checkboxes = []
        self.options = ["Head H [m]", "Flow rate Q [m^3/s]", "Rotational speed n [rpm]", "Runner diameter D [m]"]

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Select two parameters and press Next:").pack()
        
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
        chk = tk.Checkbutton(self, text=text, variable=var, onvalue=value, offvalue=0, command=self.update_count)
        chk.pack(anchor=tk.W)
        self.checkbox_vars.append(var)
        self.checkboxes.append(chk)

    def update_count(self):
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
        
        testCalculation = SingleCurve([var.get() for var in self.checkbox_vars if var.get() != 0], self.options, var1, var2)
        testCalculation.calculate_cases()
        curve_data = testCalculation.return_values()

        # Clear previous results
        self.result_text.delete(1.0, tk.END)
        
        # Display new results for each index in the lists
        num_sets = len(curve_data.H)  # Assuming all lists are of the same length
        for index in range(num_sets):
            self.result_text.insert(tk.END, f"Set {index + 1}:\n")
            for attr in ['H', 'Q', 'n', 'D', 'efficiency', 'power']:
                value = getattr(curve_data, attr)[index] if getattr(curve_data, attr) else 'N/A'
                if isinstance(value, float):
                    value_format = f"{value:.2f}"
                else:
                    value_format = str(value)
                self.result_text.insert(tk.END, f"{attr} = {value_format}\n")
            self.result_text.insert(tk.END, "\n")  # Add a newline for spacing between sets 



if __name__ == "__main__":
    app = HillChartCalculator()
    app.mainloop()
