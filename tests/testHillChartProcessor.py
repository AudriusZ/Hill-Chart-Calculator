import os
import sys
import unittest

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from HillChartProcessor import HillChartProcessor

class TestHillChartProcessor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_instance = HillChartProcessor()
    
    def setUp(self):
        # This method will run before each test case
        self.default_turbine_parameters()
        self.default_plot_parameters()
        self.default_output_parameters()

    def default_turbine_parameters(self):        
        datapath = '../src/Mogu_D1.65m.csv'
        #datapath = 'D_Liszka_et_al_turbine.csv'
        selected_values = [1,4]  # 1 - H, 2 - Q, 3 - n, 4 - D
        var1 = 2.15
        var2 = 1.65        

        self.test_instance.get_file_path(datapath)
        self.test_instance.get_turbine_parameters(selected_values, var1, var2)

    def default_plot_parameters(self):
        n_contours = 25
        extrapolation_options_vars = [1, 1]
        extrapolation_values_n11 = [80, 160, 10]
        extrapolation_values_blade_angles = [-6, 9, 10]
        
        self.test_instance.get_plot_parameters(n_contours, extrapolation_options_vars, extrapolation_values_n11, extrapolation_values_blade_angles)

    def default_output_parameters(self):
        output_options = {
            '3D Hill Chart': 1,
            'Hill Chart Contour': 1,
            '2D Curve Slices': 1,
            '2D Curve Slices - const.blade': 1,
            'Normalized Hill Chart Contour': 1,
            'Normalized 2D Curve Slices': 1,
            'Normalized 2D Curve Slices - const.blade': 1,
            'Best efficiency point summary': 1
        }
               
        output_suboptions = {
            'Hill Chart Contour': {'Hide Blade Angle Lines': 1},
            'Normalized Hill Chart Contour': {'Hide Blade Angle Lines': 1},
            '2D Curve Slices - const.blade': {'Const. Head': 1, 'Const. n': 1, 'Const. efficiency': 1},
            'Normalized 2D Curve Slices - const.blade': {'Const. Head': 1, 'Const. n': 1, 'Const. efficiency': 1}
        }

        self.test_instance.get_output_parameters(output_options, output_suboptions)

    def test_generate_outputs(self):
        # Test the generate_outputs method
        self.test_instance.generate_outputs()
        print("done")

if __name__ == '__main__':
    unittest.main()
