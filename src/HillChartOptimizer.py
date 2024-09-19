# HillChartOptimizer.py
from HillChart import HillChart
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

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
