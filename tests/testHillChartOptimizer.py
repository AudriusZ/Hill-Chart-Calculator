import os
import sys
import unittest

# Add src to sys.path so that HillChartOptimizer and others can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from HillChartOptimizer import HillChartOptimizer

class TestHillChartOptimizer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize the optimizer and load data
        cls.optimizer = HillChartOptimizer()

        # Resolve the path to the CSV file in the src directory
        datapath = os.path.join(os.path.dirname(__file__), '../src/Mogu_D1.65m.csv')
        cls.optimizer.read_hill_chart_values(datapath)

    def test_calculate_power_hill_chart(self):
        # Test if power calculation runs without errors
        try:
            self.optimizer.calculate_power_hill_chart()
            print("Power Hill chart calculation successful.")
        except Exception as e:
            self.fail(f"Power Hill chart calculation failed: {e}")

    def test_plot_power_hill_chart(self):
        # Test plotting of the power hill chart
        try:
            self.optimizer.plot_power_hill_chart(n_contours=25)
            print("Power Hill chart plotting successful.")
        except Exception as e:
            self.fail(f"Power Hill chart plotting failed: {e}")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
