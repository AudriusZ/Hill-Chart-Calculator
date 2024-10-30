import numpy as np
from scipy.interpolate import PchipInterpolator
from HillChart import HillChart
from PerformanceCurve import PerformanceCurve
import copy
from TurbineData import TurbineData

class TurbineControlSimulator(HillChart):
    """Class for optimizing hill chart data and performing various calculations."""    
    def __init__(self):        
        self.data = TurbineData()   
        self.operation_point = TurbineData()   

    def set_operation_attribute(self, attribute_name, value):
        setattr(self.operation_point, attribute_name, value)

    def compute_n11_iteratively(self, n11_guess, n11_slice, Q11_slice, efficiency_slice, tolerance=1e-3, max_iter=1000):
        """Iteratively solve for n11, Q11, and head (H) until convergence."""
        Q = self.operation_point.Q
        D = self.operation_point.D
        n = self.operation_point.n    

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

    def compute_results(self):
        """Calculate and return the results for given inputs."""
        Q = self.operation_point.Q
        D = self.operation_point.D
        n = self.operation_point.n
        blade_angle = self.operation_point.blade_angle        
        
        performance_curve = PerformanceCurve(self)
        simulator_copy = copy.deepcopy(performance_curve)
        n11_slice, Q11_slice, efficiency_slice, _ = simulator_copy.slice_hill_chart_data(selected_blade_angle=blade_angle)

        if len(Q11_slice) < 2 or len(n11_slice) < 2:
            raise ValueError("Insufficient data for computation")

        # Initial guess for n11
        n11_initial_guess = 127.7

        # Calculate the results using the iterative function
        n11, H, Q11, efficiency = self.compute_n11_iteratively(n11_initial_guess, n11_slice, Q11_slice, efficiency_slice)

        power = 9.8 * 1000 * Q * H * efficiency

        self.operation_point.n11 = n11
        self.operation_point.H = H
        self.operation_point.Q11 = Q11
        self.operation_point.efficiency = efficiency
        self.operation_point.power = power    

        return self.operation_point
    
    def adjust_rotational_speed_for_constant_head(self, H):
        """
        Adjust the rotational speed (n) based on a constant head (H) using best efficiency n11.
        """
        D = self.operation_point.D
        try:
            # Fetch the best efficiency point n11
            #best_n11 lookpup - to do
            best_n11 = 127.7
            
            # Calculate rotational speed (n) using the constant head and D
            n = best_n11 * (H ** 0.5) / D
            return n

        except Exception as e:
            print(f"Error in adjusting rotational speed: {e}")
            raise            

    def adjust_blade_angle_for_constant_H_and_Q(self, H):        
        D = self.operation_point.D
        Q = self.operation_point.Q
        n = self.operation_point.n
        try:            
            Q11 = Q / (D**2 * H**0.5)            
            n11 = n * D / H**0.5                
            blade_angle = self.get_blade_angle(Q11, n11)

            #blade_angle = Q11 #this isn't correct, hod do I lookup/interpolate blade_angle based on Q11?

            return blade_angle

        except Exception as e:
            print(f"Error in adjusting Q11: {e}")
            raise

    
    def set_head_and_adjust(self, H):
        """
        Set the head and adjust both rotational speed and blade angle accordingly.
        """
        try:            
            
            # Step 1: Adjust rotational speed for the constant head
            n = self.adjust_rotational_speed_for_constant_head(H)
            
            # Step 2: Adjust blade angle iteratively
            blade_angle = self.adjust_blade_angle_for_constant_H_and_Q(H)                       

            return {
                "Rotational Speed (n)": n,
                "Blade Angle": blade_angle                
            }

        except Exception as e:
            print(f"Error in setting head and adjusting parameters: {e}")
            raise
    