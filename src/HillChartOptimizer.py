# HillChartOptimizer.py
from HillChart import HillChart
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from scipy.interpolate import PchipInterpolator
from PerformanceCurve import PerformanceCurve  # Assuming this class is in a separate file

class HillChartOptimizer(HillChart):
    def __init__(self):
        # Call the parent constructor to initialize the data
        super().__init__()

    

    def calculate_power_hill_chart(self):
        """
        Calculates the power based on Q11, n11, and efficiency values and stores it in the HillChart data.
        The formula for power is: P = Q * H * ρ * g * η (simplified to unit values with Q11, n11)
        """
        try:
            # Assuming you have Q11, n11, and efficiency available
            if not self.data.Q11 or not self.data.n11 or not self.data.efficiency:
                raise ValueError("Q11, n11, or efficiency data is missing.")

            # Create arrays to store power values
            Q11 = np.array(self.data.Q11)
            n11 = np.array(self.data.n11)
            efficiency = np.array(self.data.efficiency)

            # Assuming unit values for density ρ and gravity g, this simplifies the formula to: Power = Q * H * η
            # Where H = n11^2 (derived from n11 = sqrt(H))
            # Thus, Power = Q11 * n11^2 * η
            power = Q11 * (1.65**2) * (2.15**0.5) * 2.15 * 1000 * 9.8 * efficiency

            # Store the calculated power in the data object (replacing efficiency with power for this case)
            self.data.power = power.tolist()

        except Exception as e:
            print(f"Error in calculating power Hill chart: {e}")
            raise

    def plot_power_hill_chart(self, n_contours=35):
        """
        Plots the power Hill chart similar to the efficiency Hill chart but with power as the Z-axis.
        """
        try:
            if not self.data.Q11 or not self.data.n11 or not self.data.power:
                raise ValueError("Power data is missing. Please calculate power first.")

            Q11 = np.array(self.data.Q11)
            n11 = np.array(self.data.n11)
            power = np.array(self.data.power)

            # Create grid coordinates for the contour plot
            x_grid = np.linspace(n11.min(), n11.max(), num=101)
            y_grid = np.linspace(Q11.min(), Q11.max(), num=101)
            x_grid, y_grid = np.meshgrid(x_grid, y_grid)

            # Interpolate unstructured data to a grid for contour plotting
            z_grid = griddata((n11, Q11), power, (x_grid, y_grid), method='cubic')

            # Plot the contour map of the power
            fig, ax = plt.subplots()
            levels = np.round(np.linspace(np.nanmin(z_grid), np.nanmax(z_grid), num=n_contours), 3)
            contour = ax.contourf(x_grid, y_grid, z_grid, levels=levels, cmap='plasma')
            contour_lines = ax.contour(x_grid, y_grid, z_grid, levels=levels, colors='k', linewidths=0.5)
            ax.clabel(contour_lines, inline=False, fontsize=8, fmt='%.2f')

            # Add color bar
            cbar = fig.colorbar(contour, ax=ax)
            cbar.set_label('Power [W]')

            # Set labels and title
            ax.set_xlabel('n11 (unit speed)')
            ax.set_ylabel('Q11 (unit flow)')
            ax.set_title('Power Hill Chart')

            plt.show(block=False)

        except Exception as e:
            print(f"Error in plotting power Hill chart: {e}")
            raise

    def get_n11_for_given_Q11_and_blade_angle(self, input_Q11, input_blade_angle):
        """
        Takes Q11 and blade_angle as inputs, slices the hill chart data by blade angle,
        and returns the interpolated n11 value.
        """
        try:
            # Initialize PerformanceCurve with the current hill chart data
            performance_curve = PerformanceCurve(self)
            
            # Slice the data based on the provided blade angle
            n11_slice, Q11_slice, efficiency_slice, blade_angle_slice = performance_curve.slice_hill_chart_data(selected_blade_angle=input_blade_angle)
            
            # Check if input Q11 is within the sliced Q11 range
            if not (min(Q11_slice) <= input_Q11 <= max(Q11_slice)):
                raise ValueError(f"Input Q11 {input_Q11} is out of range for the selected blade angle.")
            
            # Interpolate the n11 value for the given Q11
            n11_interpolator = PchipInterpolator(Q11_slice, n11_slice)
            output_n11 = n11_interpolator(input_Q11)

            efficiency_interpolator = PchipInterpolator(Q11_slice, efficiency_slice)
            output_efficiency = efficiency_interpolator(input_Q11)
            
            return output_n11, output_efficiency
        
        except Exception as e:
            print(f"Error in get_n11_for_given_Q11_and_blade_angle: {e}")
            return None, None

import os
import copy

optimizer = HillChartOptimizer()
datapath = os.path.join(os.path.dirname(__file__), '../src/Mogu_D1.65m.csv')
optimizer.read_hill_chart_values(datapath)
optimizer.prepare_hill_chart_data()


D = 1.65


# Loop for user inputs
while True:
    try:
        optimizer2 = copy.deepcopy(optimizer)
        # Prompt user for inputs
        Q = float(input("Enter Q (flow rate): "))
        H = float(input("Enter H (head): "))
        Blade = float(input("Enter Blade angle: "))
        
        # Calculate Q11
        Q11 = Q / (D**2 * H**0.5)
        
        # Get n11 and efficiency
        n11, efficiency = optimizer2.get_n11_for_given_Q11_and_blade_angle(Q11, Blade)
        
        # Calculate n
        n = n11 * H**0.5 / D

        power = 9.8 * 1000 * Q * H * efficiency
        
        # Print results
        print("----------------")
        print(f"n11 = {n11}")
        print(f"Q11 = {Q11}")
        print(f"efficiency = {efficiency}")
        print("")
        print(f"n = {n}")
        
        print(f"power = {power}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
    # Ask user if they want to continue or exit the loop
    cont = input("Do you want to continue? (y/n): ").strip().lower()
    if cont != 'y':
        break



