#To create standalon exe use the line below:
#pyinstaller --onefile --name Hill_Chart_Calculator_0.9.1 --icon=icon.ico Calculator.py

import tkinter as tk
from tkinter import messagebox, filedialog
from HillChartProcessor import HillChartProcessor

print("Hello, this is a tool for hydro turbine scaling")

class HillChartCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Hill Chart Calculator')

        self.checkbox_vars = []
        self.checkboxes = []
        self.options = ["Head H [m]", "Flow rate Q [m^3/s]", "Rotational speed n [rpm]", "Runner diameter D [m]"]
        self.sub_option_widgets = {}

        self.output_options = ["Best efficiency point summary","3D Hill Chart", "Hill Chart Contour", "2D Curve Slices","2D Curve Slices - const.blade"]
        self.output_vars = {option: tk.IntVar() for option in self.output_options}

        # Define sub-options for specific output options
        self.sub_output_options = {
            "Hill Chart Contour": ["Hide Blade Angle Lines"],            
            "2D Curve Slices - const.blade": ["Const. Head", "Const. n", "Const. efficiency"]            
        }
        self.sub_output_vars = {key: [tk.IntVar() for _ in value] for key, value in self.sub_output_options.items()}
        self.settings_options = ["Normalize", "Save 2D Chart Data"]
        self.settings_vars = {option: tk.IntVar() for option in self.settings_options}
        self.extrapolation_options = ["Extrapolate unit speed n11 [rpm]", "Extrapolate Blade Angles [degree]"]
        self.extrapolation_options_vars = [tk.IntVar() for _ in self.extrapolation_options]
        self.extrapolation_entry_vars = []
        self.extrapolation_entries = []

        self.n_contours = 25  # Default value for contour lines
        self.min_efficiency_limit= 0.2 # Default value for minimum efficiency cap

        # Instance variables for holding GUI inputs
        self.selected_values = [1, 4]
        self.var1 = None
        self.var2 = None
        self.extrapolation_values_n11 = [60, 200, 10]
        self.extrapolation_values_blade_angles = [7, 22.5, 10]

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

        tk.Label(surface_fit_frame, text="Set minimum efficiency limit:").grid(row=0, column=0, padx=1, pady=0, sticky="n")
        self.min_efficiency_entry = tk.Entry(surface_fit_frame, width=7)
        self.min_efficiency_entry.grid(row=1, column=0, padx=1, pady=0, sticky="n")
        self.min_efficiency_entry.insert(0, str(self.min_efficiency_limit))  # Set default value
        
        tk.Label(surface_fit_frame, text="Set number of contours:").grid(row=2, column=0, padx=1, pady=0, sticky="w")
        self.n_contours_entry = tk.Entry(surface_fit_frame, width=7)
        self.n_contours_entry.grid(row=3, column=0, padx=1, pady=0, sticky="w")
        self.n_contours_entry.insert(0, str(self.n_contours))  # Set default value
   
        # Define entry labels for extrapolation checkboxes
        extrapolation_entry_labels = [
            ["Min", "Max", "No. of Pts"],
            ["Min", "Max", "No. of Pts"]
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

        for output_option in self.output_options:
            self.create_output_checkbox(output_option, parent=output_frame)

        # Add a "Settings" subframe under the output options frame
        settings_frame = tk.LabelFrame(output_frame, text="Settings", padx=5, pady=5)
        settings_frame.pack(fill="both", expand=True, padx=5, pady=5)

        for settings_option in self.settings_options:
            self.create_settings_checkbox(settings_option, parent=settings_frame)                    
        
        '''
        # Add widgets in the "Settings" subframe
        normalize_check = tk.Checkbutton(settings_frame, text="Normalize")
        normalize_check.pack(anchor="w")

        efficiency_check = tk.Checkbutton(settings_frame, text="Save Chart Data")
        efficiency_check.pack(anchor="w")
        '''
        self.calculate_button = tk.Button(output_frame, text="Calculate", command=self.generate_outputs, state='disabled')
        self.calculate_button.pack()
    
    def create_settings_checkbox(self, text, parent):
        var = tk.IntVar()
        chk = tk.Checkbutton(parent, text=text, variable=self.settings_vars[text], onvalue=1, offvalue=0)
        chk.pack(anchor=tk.W)
        #self.checkbox_vars.append(var)
        #self.checkboxes.append(chk)
    
    def create_input_param_checkbox(self, text, value, parent):
        var = tk.IntVar()
        chk = tk.Checkbutton(parent, text=text, variable=var, onvalue=value, offvalue=0, command=self.update_count, state='disabled')
        chk.pack(anchor=tk.W)
        self.checkbox_vars.append(var)
        self.checkboxes.append(chk)
    
    def create_output_checkbox(self, text, parent):
        # Create the main checkbox with a command to toggle sub-options
        chk = tk.Checkbutton(parent, text=text, variable=self.output_vars[text], onvalue=1, offvalue=0, command=lambda: self.toggle_suboptions(text))
        chk.pack(anchor=tk.W)

        # If there are sub-options, create checkboxes for them
        if text in self.sub_output_options:
            sub_frame = tk.Frame(parent)
            sub_frame.pack(anchor=tk.W, padx=20)  # Indent the sub-options

            # If this is the first time adding sub-options for this text, initialize the list
            if text not in self.sub_option_widgets:
                self.sub_option_widgets[text] = []

            # Add each sub-option checkbox
            for sub_option, sub_var in zip(self.sub_output_options[text], self.sub_output_vars[text]):
                sub_chk = tk.Checkbutton(sub_frame, text=sub_option, variable=sub_var, onvalue=1, offvalue=0)
                sub_chk.pack(anchor=tk.W)
                sub_chk.configure(state='disabled')  # Initially disable sub-checkboxes

                # Store the sub-checkbox in the dictionary for future state toggling
                self.sub_option_widgets[text].append(sub_chk)

    # Function to enable/disable sub-options based on the main checkbox state
    def toggle_suboptions(self, text):
        # Check the state of the main checkbox
        state = 'normal' if self.output_vars[text].get() == 1 else 'disabled'

        # Enable or disable the sub-option checkboxes based on the main checkbox state
        if text in self.sub_option_widgets:
            for sub_chk in self.sub_option_widgets[text]:
                sub_chk.configure(state=state)
        

    def create_extrapolation_checkbox(self, option, var, labels, parent, set_default = 'no'):
        # Create a frame for the checkbox and associated entries
        frame = tk.Frame(parent)
        frame.grid(sticky="w", padx=5, pady=5)  # Ensure proper padding and alignment

        # Create the checkbox in its own row        
        checkbox = tk.Checkbutton(frame, text=option, variable=var, command=lambda: self.toggle_extrapolation_entries(var))        

        checkbox.grid(row=0, column=0, sticky="w", padx=5, pady=(5, 0))  # Top padding, no bottom padding

        # Create the entry labels and fields
        entry_frame = tk.Frame(frame)
        entry_frame.grid(row=1, column=0, sticky="w", padx=5, pady=(0, 5))  # Bottom padding, no top padding

        # Initialize a list for this set of entries
        entry_vars = []

        # Create the entry labels and fields in a single row
        for j, label in enumerate(labels):
            tk.Label(entry_frame, text=label).grid(row=0, column=j, padx=5)
            entry = tk.Entry(entry_frame, width=7)
            if option == self.extrapolation_options[0]:
                entry.insert(0, str(self.extrapolation_values_n11[j]))
            if option == self.extrapolation_options[1]:
                entry.insert(0, str(self.extrapolation_values_blade_angles[j]))
            entry.grid(row=1, column=j, padx=5)
            entry_vars.append(entry)
            

        # Store the list of entries in the dictionary with the option index as key
        self.extrapolation_entries.append(entry_vars)
        self.toggle_extrapolation_entries(var, initialisation=True)
        

    def toggle_extrapolation_entries(self, var, initialisation = False):
        state = 'normal' if var.get() == 1 else 'disabled'
        index = self.extrapolation_options_vars.index(var)

        # Check if the index is valid
        if index < len(self.extrapolation_entries):
            for entry in self.extrapolation_entries[index]:
                entry.config(state=state)
        else:
            print(f"Index {index} out of range for extrapolation_entries.")
        if not initialisation:
            try:
                # Ensure to use set() method for IntVar
                if self.extrapolation_options_vars[0].get() == 0:
                    self.extrapolation_options_vars[1].set(0)  # Correct way to update IntVar value
                    state = 'normal' if var.get() == 1 else 'disabled'                   

            except IndexError:
                print("IndexError: self.extrapolation_options_vars index out of range.")
            except AttributeError:
                print("AttributeError: self.extrapolation_options_vars[0] might not be an IntVar.")
        

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

    def get_n_contours(self):
        try:
            self.n_contours = int(self.n_contours_entry.get())
        except ValueError:
            messagebox.showerror("Input error", "Please enter a valid integer for the number of contours.")

    def get_min_efficiency_lim(self):
        try:
            self.min_efficiency_limit = float(self.min_efficiency_entry.get())
        except ValueError:
            messagebox.showerror("Input error", "Please enter a valid float for the number of contours.")

    def generate_outputs(self):
        # Gather all GUI inputs before processing
        self.get_n_contours()    
        self.get_min_efficiency_lim()    
        self.get_selected_values()
        self.get_extrapolation_values()
        
        plot_processor = HillChartProcessor()
        plot_processor.set_file_path(self.datapath)
        plot_processor.set_turbine_parameters(self.selected_values, self.var1, self.var2)
        plot_processor.set_plot_parameters(self.n_contours, [self.extrapolation_options_vars[0].get(),self.extrapolation_options_vars[1].get()],self.extrapolation_values_n11,self.extrapolation_values_blade_angles, min_efficiency_limit=self.min_efficiency_limit)        
        plot_options = {option: var.get() for option, var in self.output_vars.items()}
        plot_suboptions = {option: {sub_option: sub_var.get() for sub_option, sub_var in zip(self.sub_output_options[option], sub_vars)}
            for option, sub_vars in self.sub_output_vars.items()}
        settings_options = {option: var.get() for option, var in self.settings_vars.items()}
        plot_processor.set_output_parameters(plot_options, plot_suboptions, settings_options)        
        plot_processor.generate_outputs()        

    def get_selected_values(self):
        try:
            self.var1 = float(self.var_entry_1.get())
            self.var2 = float(self.var_entry_2.get())
        except ValueError:
            messagebox.showerror("Input error", "Please enter valid numbers.")
            return

    def get_extrapolation_values(self):
        # Retrieve values for the first extrapolation option
        if self.extrapolation_options_vars[0].get():  # Extrapolate unit speed n11 [rpm]
            self.extrapolation_values_n11 = [float(entry.get()) for entry in self.extrapolation_entries[0]]
            self.extrapolation_values_n11[2] = int(self.extrapolation_values_n11[2])

        # Retrieve values for the second extrapolation option
        if self.extrapolation_options_vars[1].get():  # Extrapolate Blade Angles [degree]
            self.extrapolation_values_blade_angles = [float(entry.get()) for entry in self.extrapolation_entries[1]]
            self.extrapolation_values_blade_angles[2] = int(self.extrapolation_values_blade_angles[2])      

if __name__ == "__main__":
    app = HillChartCalculator()
    app.mainloop()
