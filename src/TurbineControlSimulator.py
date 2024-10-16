import numpy as np
from scipy.interpolate import PchipInterpolator
from HillChart import HillChart
from PerformanceCurve import PerformanceCurve
import copy

class TurbineControlSimulator(HillChart):
    """Class for optimizing hill chart data and performing various calculations."""

    def calculate_power_hill_chart(self):
        """Calculate the power hill chart values from efficiency and Q11."""
        try:
            if not self.data.Q11 or not self.data.n11 or not self.data.efficiency:
                raise ValueError("Missing hill chart data for calculation.")
            
            Q11 = np.array(self.data.Q11)
            n11 = np.array(self.data.n11)
            efficiency = np.array(self.data.efficiency)

            # Calculate power and store the results
            power = Q11 * (1.65**2) * (2.15**0.5) * 2.15 * 1000 * 9.8 * efficiency
            self.data.power = power.tolist()
        except Exception as e:
            print(f"Error in calculating power Hill chart: {e}")
            raise

    def compute_n11_iteratively(self, Q, D, n, n11_guess, n11_slice, Q11_slice, efficiency_slice, tolerance=1e-3, max_iter=1000):
        """Iteratively solve for n11, Q11, and head (H) until convergence."""
        try:
            finite_mask = np.isfinite(efficiency_slice) & np.isfinite(n11_slice) & np.isfinite(Q11_slice)

            # Filter out non-finite values
            n11_clean = n11_slice[finite_mask]
            Q11_clean = Q11_slice[finite_mask]
            efficiency_clean = efficiency_slice[finite_mask]

            if len(n11_clean) < 2 or len(Q11_clean) < 2 or len(efficiency_clean) < 2:
                raise ValueError("Insufficient valid data points after filtering non-finite values.")

            Q11_interpolator = PchipInterpolator(n11_clean, Q11_clean)
            efficiency_interpolator = PchipInterpolator(n11_clean, efficiency_clean)

            # Iteratively solve for n11, Q11, and H using the initial guess
            for iter_count in range(max_iter):
                H = (n * D / n11_guess) ** 2
                Q11_calculated = Q / (D**2 * np.sqrt(H))

                Q11_lookup = Q11_interpolator(n11_guess)
                efficiency = efficiency_interpolator(n11_guess)

                if abs(Q11_calculated - Q11_lookup) < tolerance:
                    return n11_guess, H, Q11_calculated, efficiency

                n11_guess *= Q11_lookup / Q11_calculated

            raise ValueError("Solution did not converge within the specified number of iterations.")

        except Exception as e:
            print(f"Error in iterative solution: {e}")
            raise

    def compute_results(self, Q, D, n, Blade):
        """Calculate and return the results for given inputs."""
        performance_curve = PerformanceCurve(self)
        simulator_copy = copy.deepcopy(performance_curve)
        n11_slice, Q11_slice, efficiency_slice, _ = simulator_copy.slice_hill_chart_data(selected_blade_angle=Blade)

        if len(Q11_slice) < 2 or len(n11_slice) < 2:
            raise ValueError("Insufficient data for computation")

        # Initial guess for n11
        n11_initial_guess = 127.7

        # Calculate the results using the iterative function
        n11_solution, H_solution, Q11_solution, efficiency = self.compute_n11_iteratively(
            Q, D, n, n11_initial_guess, n11_slice, Q11_slice, efficiency_slice
        )

        power = 9.8 * 1000 * Q * H_solution * efficiency
        return Q11_solution, n11_solution, efficiency, H_solution, power
    
    def compute_results_const_H(self, Q, D, n, Blade):
        """Calculate and return the results for given inputs."""
        performance_curve = PerformanceCurve(self)
        simulator_copy = copy.deepcopy(performance_curve)
        n11_slice, Q11_slice, efficiency_slice, _ = simulator_copy.slice_hill_chart_data(selected_blade_angle=Blade)

        if len(Q11_slice) < 2 or len(n11_slice) < 2:
            raise ValueError("Insufficient data for computation")

        # Initial guess for n11
        n11_initial_guess = 127.7

        # Calculate the results using the iterative function
        n11_solution, H_solution, Q11_solution, efficiency = self.compute_n11_iteratively(
            Q, D, n, n11_initial_guess, n11_slice, Q11_slice, efficiency_slice
        )

        power = 9.8 * 1000 * Q * H_solution * efficiency
        return Q11_solution, n11_solution, efficiency, H_solution, power
    
    def adjust_rotational_speed_for_constant_head(self, head, D):
        """
        Adjust the rotational speed (n) based on a constant head (H) using best efficiency n11.
        """
        try:
            # Fetch the best efficiency point n11
            #best_n11 = max(self.data.n11, key=lambda n: self.data.efficiency[self.data.n11.index(n)])
            best_n11 = 127.7
            
            # Calculate rotational speed (n) using the constant head and D
            n = best_n11 * (head ** 0.5) / D
            return n

        except Exception as e:
            print(f"Error in adjusting rotational speed: {e}")
            raise

    def iterative_blade_angle_adjustment(self, head, Q, D, tolerance=0.01, max_iterations=100):
        """
        Adjust blade angle iteratively to optimize for efficiency or specific criterion.
        """
        try:
            current_best_efficiency = 0
            best_blade_angle = None
            
            # Create an instance of PerformanceCurve
            performance_curve = PerformanceCurve(self)
            
            # Iterate over blade angles within a reasonable range
            for angle in range(8, 20, 1):  # Example range from 5° to 45°
                # Use PerformanceCurve instance to slice data by blade angle
                n11_slice, Q11_slice, efficiency_slice, _ = performance_curve.slice_hill_chart_data(selected_blade_angle=angle)

                # Using iterative method to get a solution for the given head and Q
                n11_initial_guess = 127.7
                n11_solution, H_solution, Q11_solution, efficiency = self.compute_n11_iteratively(
                    Q, D, n11_initial_guess, n11_slice, Q11_slice, efficiency_slice
                )

                if abs(H_solution - head) < tolerance:
                    if efficiency > current_best_efficiency:
                        current_best_efficiency = efficiency
                        best_blade_angle = angle

            if best_blade_angle is not None:
                return best_blade_angle, current_best_efficiency
            else:
                raise ValueError("Could not find an optimal blade angle within the specified range.")

        except Exception as e:
            print(f"Error in blade angle adjustment: {e}")
            raise

    def set_head_and_adjust(self, head, Q, D):
        """
        Set the head and adjust both rotational speed and blade angle accordingly.
        """
        try:
            # Step 1: Adjust rotational speed for the constant head
            n = self.adjust_rotational_speed_for_constant_head(head, D)
            
            # Step 2: Adjust blade angle iteratively
            #best_blade_angle, efficiency = self.iterative_blade_angle_adjustment(head, Q, D)

            return {
                "Rotational Speed (n)": n
                #"Blade Angle": best_blade_angle,
                #"Efficiency": efficiency
            }

        except Exception as e:
            print(f"Error in setting head and adjusting parameters: {e}")
            raise
