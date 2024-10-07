import os
import copy
import numpy as np
from scipy.interpolate import PchipInterpolator
from HillChart import HillChart
from PerformanceCurve import PerformanceCurve
# Assuming your HillChartOptimizer and other relevant classes are already defined above
class HillChartOptimizer(HillChart):
    def __init__(self):
        # Call the parent constructor to initialize the data
        super().__init__()

    def calculate_power_hill_chart(self):
        try:
            if not self.data.Q11 or not self.data.n11 or not self.data.efficiency:
                raise ValueError("Q11, n11, or efficiency data is missing.")
            Q11 = np.array(self.data.Q11)
            n11 = np.array(self.data.n11)
            efficiency = np.array(self.data.efficiency)
            power = Q11 * (1.65**2) * (2.15**0.5) * 2.15 * 1000 * 9.8 * efficiency
            self.data.power = power.tolist()
        except Exception as e:
            print(f"Error in calculating power Hill chart: {e}")
            raise

    def plot_power_hill_chart(self, n_contours=35):
        try:
            if not self.data.Q11 or not self.data.n11 or not self.data.power:
                raise ValueError("Power data is missing. Please calculate power first.")
            Q11 = np.array(self.data.Q11)
            n11 = np.array(self.data.n11)
            power = np.array(self.data.power)
            x_grid = np.linspace(n11.min(), n11.max(), num=101)
            y_grid = np.linspace(Q11.min(), Q11.max(), num=101)
            x_grid, y_grid = np.meshgrid(x_grid, y_grid)
            z_grid = griddata((n11, Q11), power, (x_grid, y_grid), method='cubic')
            fig, ax = plt.subplots()
            levels = np.round(np.linspace(np.nanmin(z_grid), np.nanmax(z_grid), num=n_contours), 3)
            contour = ax.contourf(x_grid, y_grid, z_grid, levels=levels, cmap='plasma')
            contour_lines = ax.contour(x_grid, y_grid, z_grid, levels=levels, colors='k', linewidths=0.5)
            ax.clabel(contour_lines, inline=False, fontsize=8, fmt='%.2f')
            cbar = fig.colorbar(contour, ax=ax)
            cbar.set_label('Power [W]')
            ax.set_xlabel('n11 (unit speed)')
            ax.set_ylabel('Q11 (unit flow)')
            ax.set_title('Power Hill Chart')
            plt.show(block=False)
        except Exception as e:
            print(f"Error in plotting power Hill chart: {e}")
            raise

    def lookup_n11(self, input_Q11, input_blade_angle):
        try:
            performance_curve = PerformanceCurve(self)
            n11_slice, Q11_slice, efficiency_slice, blade_angle_slice = performance_curve.slice_hill_chart_data(selected_blade_angle=input_blade_angle)
            if not (min(Q11_slice) <= input_Q11 <= max(Q11_slice)):
                raise ValueError(f"Input Q11 {input_Q11} is out of range for the selected blade angle.")
            n11_interpolator = PchipInterpolator(Q11_slice, n11_slice)
            output_n11 = n11_interpolator(input_Q11)
            efficiency_interpolator = PchipInterpolator(Q11_slice, efficiency_slice)
            output_efficiency = efficiency_interpolator(input_Q11)
            return output_n11, output_efficiency
        except Exception as e:
            print(f"Error in lookup_n11: {e}")
            return None, None

    def solve_recursive_Q11_guess(self, Q, D, n, Q11_guess, n11_slice, Q11_slice, efficiency_slice, tolerance=1e-6, max_iter=1000, iter_count=0):
        """
        Recursive function to solve for Q11 and H based on the given input values and precomputed slices.
        Parameters:
            Q (float): Flow rate.
            D (float): Diameter.
            n (float): Shaft speed.
            Q11_guess (float): Initial guess for Q11.
            n11_slice (array): Precomputed slice of n11 values for the given blade angle.
            Q11_slice (array): Precomputed slice of Q11 values for the given blade angle.
            efficiency_slice (array): Precomputed slice of efficiency values.
            tolerance (float): Tolerance for convergence.
            max_iter (int): Maximum number of iterations.
            iter_count (int): Current iteration count.
        Returns:
            Q11_solution (float): Converged value of Q11.
            H_solution (float): Converged value of H.
            n11_calculated (float): Value of n11 after convergence.
            efficiency (float): Interpolated efficiency value.
        """
        try:
            # Step 1: Calculate the head H based on the current guess of Q11
            H = (Q / (D**2 * Q11_guess)) ** 2

            # Step 2: Calculate n11 using the calculated H
            n11_calculated = (n * D) / np.sqrt(H)

            # Step 3: Interpolate the n11 and efficiency based on the given Q11 guess using the precomputed slices
            n11_interpolator = PchipInterpolator(Q11_slice, n11_slice)
            efficiency_interpolator = PchipInterpolator(Q11_slice, efficiency_slice)

            n11_lookup = n11_interpolator(Q11_guess)
            efficiency = efficiency_interpolator(Q11_guess)

            # Step 4: Check for convergence based on the difference between the calculated and looked-up n11
            if abs(n11_calculated - n11_lookup) < tolerance or iter_count >= max_iter:
                return Q11_guess, H, n11_calculated, efficiency
            else:
                # Step 5: Refine the guess for Q11 using the ratio of the n11 values to bring them closer
                Q11_refined = Q11_guess * (n11_calculated / n11_lookup)

                # Recursive call with updated Q11 guess
                return self.solve_recursive_Q11_guess(Q, D, n, Q11_refined, n11_slice, Q11_slice, efficiency_slice, tolerance, max_iter, iter_count + 1)

        except Exception as e:
            print(f"Error in recursive solution: {e}")
            raise

    def solve_recursive_n11_guess(self, Q, D, n, n11_guess, n11_slice, Q11_slice, efficiency_slice, tolerance=1e-3, max_iter=1000, iter_count=0):        
            try:
                # Calculate the head H based on the current guess of n11
                H = (n * D / n11_guess) ** 2

                # Calculate Q11 using the calculated H
                Q11_calculated = Q / (D**2 * np.sqrt(H))

                
                # Check for non-finite values in `efficiency_slice`
                finite_mask = np.isfinite(efficiency_slice)

                # Filter both arrays to remove non-finite values
                n11_clean = n11_slice[finite_mask]
                efficiency_finite = efficiency_slice[finite_mask]                
                
                # Interpolate the n11 and efficiency based on the given Q11 guess using the precomputed slices
                Q11_interpolator = PchipInterpolator(n11_slice, Q11_slice)
                efficiency_interpolator = PchipInterpolator(n11_clean, efficiency_finite)

                Q11_lookup = Q11_interpolator(n11_guess)
                efficiency = efficiency_interpolator(n11_guess)

                # Step 4: Check for convergence based on the difference between the calculated and looked-up n11
                if abs(Q11_calculated - Q11_lookup) < tolerance or iter_count >= max_iter:
                    
                    return n11_guess, H, Q11_calculated, efficiency
                else:
                    # Step 5: Refine the guess for n11 using the ratio of the Q11 values to bring them closer
                    n11_refined = n11_guess * (Q11_lookup / Q11_calculated)
                    print(iter_count)
                    print(n11_guess, Q11_lookup, Q11_calculated)
                    # Recursive call with updated Q11 guess
                    return self.solve_recursive_n11_guess(Q, D, n, n11_refined, n11_slice, Q11_slice, efficiency_slice, tolerance, max_iter, iter_count + 1)

            except Exception as e:
                print(f"Error in recursive solution: {e}")
                raise


'''

# Main optimization loop
def optimization_loop(optimizer, D):
    while True:
        try:
            optimizer2 = copy.deepcopy(optimizer)

            # Prompt user for inputs
            print(" ")
            Q = float(input("Enter Q (flow rate): "))
            Blade = float(input("Enter Blade angle: "))
            n = float(input("Enter n (rotational speed): "))

            # Calculate the slices once before starting the iterations
            performance_curve = PerformanceCurve(optimizer2)
            n11_slice, Q11_slice, efficiency_slice, _ = performance_curve.slice_hill_chart_data(selected_blade_angle=Blade)

            # Check if the slices are valid before proceeding
            if len(Q11_slice) < 2 or len(n11_slice) < 2:
                print(f"Error: Insufficient data points for blade angle {Blade}. Check hill chart data.")
                continue

            # Initial guess for Q11 (can be a reasonable value like 1.0)
            Q11_initial_guess = 1.0

            # Call the recursive function with precomputed slices
            Q11_solution, H_solution, n11_solution, efficiency = optimizer2.solve_recursive_Q11_guess(
                Q, D, n, Q11_initial_guess, n11_slice, Q11_slice, efficiency_slice
            )

            # Calculate power using the known formula
            power = 9.8 * 1000 * Q * H_solution * efficiency

            # Print the results with specified precision
            print("----------------")
            print(f"n11 = {n11_solution:.1f}")      
            print(f"Q11 = {Q11_solution:.2f}")      
            print(f"efficiency = {efficiency:.2f}") 
            print(f"H = {H_solution:.2f}")          
            print(f"Power = {power:.0f}")            

        except Exception as e:
            print(f"An error occurred: {e}")

        # Ask user if they want to continue or exit the loop
        cont = input("Do you want to continue? (y/n): ").strip().lower()
        if cont != 'y':
            break



# Instantiate the optimizer and load data
optimizer = HillChartOptimizer()
datapath = os.path.join(os.path.dirname(__file__), '../src/Mogu_D1.65m.csv')
optimizer.read_hill_chart_values(datapath)
optimizer.prepare_hill_chart_data()

# Start the optimization loop
optimization_loop(optimizer, D=1.65)
'''