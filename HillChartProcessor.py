
from HillChart import HillChart  # Ensure HillChart module is available in the environment
#import matplotlib.pyplot as plt
#import copy

class HillChartProcessor:
    
    def manual_setup(self):
        self.datapath = 'Mogu_D1.65m.csv'        
        self.selected_values = [1,4]
        self.var1 = 2.15
        self.var2 = 1.65
        self.n_contours = 25

        

    def get_file_path(self, file_path):
        self.datapath = file_path

    def prepare_core_data(self):
        BEP_values = HillChart()
        BEP_values.read_hill_chart_values(self.datapath)
        BEP_values.filter_for_maximum_efficiency()
        BEP_values.calculate_cases(self.selected_values, self.var1, self.var2)
        BEP_data = BEP_values.return_values()

        hill_values = HillChart()
        hill_values.read_hill_chart_values(self.datapath)

        if self.extrapolation_options_vars[0].get():  # Extrapolate unit speed n11 [rpm]
            hill_values.extrapolate_along_n11(min_n11=self.extrapolation_values_n11[0], max_n11=self.extrapolation_values_n11[1], n_n11=self.extrapolation_values_n11[2])

        if self.extrapolation_options_vars[1].get():  # Extrapolate Blade Angles [degree]
            hill_values.extrapolate_along_blade_angles(min_angle=self.extrapolation_values_blade_angles[0], max_angle=self.extrapolation_values_blade_angles[1], n_angle=self.extrapolation_values_blade_angles[2])

        hill_values.prepare_hill_chart_data()

        return BEP_data, hill_values
    
    def generate_outputs(self):
        # Gather all GUI inputs before processing
        self.get_selected_values()
        self.get_extrapolation_values()

        # Proceed with calculations using instance variables
        #self.set_n_contours()
        BEP_data, hill_values = self.prepare_core_data()

        # Generate the outputs based on user selection
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
    
    def prepare_core_data(self):
        BEP_values = HillChart()
        BEP_values.read_hill_chart_values(self.datapath)
        BEP_values.filter_for_maximum_efficiency()
        BEP_values.calculate_cases(self.selected_values, self.var1, self.var2)
        BEP_data = BEP_values.return_values()

        hill_values = HillChart()
        hill_values.read_hill_chart_values(self.datapath)

        if self.extrapolation_options_vars[0].get():  # Extrapolate unit speed n11 [rpm]
            hill_values.extrapolate_along_n11(min_n11=self.extrapolation_values_n11[0], max_n11=self.extrapolation_values_n11[1], n_n11=self.extrapolation_values_n11[2])

        if self.extrapolation_options_vars[1].get():  # Extrapolate Blade Angles [degree]
            hill_values.extrapolate_along_blade_angles(min_angle=self.extrapolation_values_blade_angles[0], max_angle=self.extrapolation_values_blade_angles[1], n_angle=self.extrapolation_values_blade_angles[2])

        hill_values.prepare_hill_chart_data()

        return BEP_data, hill_values