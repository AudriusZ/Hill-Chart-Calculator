import numpy as np
from scipy.interpolate import PchipInterpolator
from HillChart import HillChart
from PerformanceCurve import PerformanceCurve
import copy
from TurbineData import TurbineData
import pandas as pd
import copy

class TurbineControlSimulator(HillChart):
    """Class for simulating turbine control."""    
    def __init__(self):        
        """
        Initialize the TurbineControlSimulator, setting up data attributes for turbine operations.

        Attributes:
            data (TurbineData): The main turbine data, including Q11, n11, efficiency, etc.
            operation_point (TurbineData): The current operational state, used for calculations.
        """
        self.data = TurbineData()   
        self.operation_point = TurbineData()   

    def set_operation_attribute(self, attribute_name, value):
        """
        Set an attribute in the operation_point data structure.

        Args:
            attribute_name (str): Name of the attribute to set.
            value (any): The value to assign to the specified attribute.
        """
        setattr(self.operation_point, attribute_name, value)

    def compute_n11_iteratively(self, n11_guess, n11_slice, Q11_slice, efficiency_slice, tolerance=1e-3, max_iter=1000):
        """
        Iteratively solve for n11, Q11, and head (H) values until a solution converges within tolerance.

        Args:
            n11_guess (float): Initial guess for n11.
            n11_slice (array): Array of n11 values for interpolation.
            Q11_slice (array): Array of Q11 values for interpolation.
            efficiency_slice (array): Array of efficiency values for interpolation.
            tolerance (float): Convergence threshold for the iterative solution.
            max_iter (int): Maximum number of iterations before stopping.

        Returns:
            tuple: (n11, H, Q11, efficiency) - calculated values for n11, head, Q11, and efficiency.

        Raises:
            ValueError: If solution does not converge or data is insufficient.
        """
        Q = self.operation_point.Q
        D = self.operation_point.D
        n = self.operation_point.n    

        #print('n11 slice = ', n11_slice)
        #print('Q11 slice =', Q11_slice)

        try:
            finite_mask = np.isfinite(efficiency_slice) & np.isfinite(n11_slice) & np.isfinite(Q11_slice)

            # Filter out non-finite values
            n11_clean = n11_slice[finite_mask]
            Q11_clean = Q11_slice[finite_mask]
            efficiency_clean = efficiency_slice[finite_mask]

            if len(n11_clean) < 2 or len(Q11_clean) < 2 or len(efficiency_clean) < 2:
                raise ValueError("Insufficient valid data points after filtering non-finite values.")

            # Define min and max bounds for n11 based on the data range
            min_n11 = n11_clean.min()
            max_n11 = n11_clean.max()

            Q11_interpolator = PchipInterpolator(n11_clean, Q11_clean)
            efficiency_interpolator = PchipInterpolator(n11_clean, efficiency_clean)

            # Iteratively solve for n11, Q11, and H using the initial guess
            for iter_count in range(max_iter):
                # Cap n11_guess within the bounds
                n11_guess = np.clip(n11_guess, min_n11, max_n11)

                H = (n * D / n11_guess) ** 2
                Q11_calculated = Q / (D**2 * np.sqrt(H))

                Q11_lookup = Q11_interpolator(n11_guess)
                efficiency = efficiency_interpolator(n11_guess)

                if abs(Q11_calculated - Q11_lookup) / abs(Q11_lookup) < tolerance:
                    return n11_guess, H, Q11_calculated, efficiency
                elif iter_count == max_iter - 1:
                    return np.nan, np.nan, np.nan, np.nan

                #print(n11_guess, Q11_lookup, Q11_calculated, efficiency)
                damping_factor = 0.1
                n11_guess *= 1 + damping_factor * ((Q11_lookup / Q11_calculated) - 1)

            raise ValueError("Solution did not converge within the specified number of iterations.")

        except Exception as e:
            print(f"Error in iterative solution: {e}")
            raise  

    def compute_results(self):
        """
        Calculate and return the results for the given input parameters.

        The method calculates operational parameters (e.g., n11, H, Q11, efficiency, and power)
        and updates them in the `operation_point` attribute.

        Returns:
            TurbineData: An instance containing the updated operational values.

        Raises:
            ValueError: If data is insufficient for computation.
        """
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
        n11_initial_guess = self.BEP_data.n11[0]

        # Calculate the results using the iterative function
        n11, H, Q11, efficiency = self.compute_n11_iteratively(n11_initial_guess, n11_slice, Q11_slice, efficiency_slice)

        power = 9.8 * 1000 * Q * H * efficiency

        # Update the operation point data
        self.operation_point.n11 = n11
        self.operation_point.H = H
        self.operation_point.Q11 = Q11
        self.operation_point.efficiency = efficiency
        self.operation_point.power = power    

        return self.operation_point
    
    def adjust_rotational_speed_for_constant_head(self, H):
        """
        Adjust the rotational speed (n) based on a constant head (H) using best efficiency n11.

        Args:
            H (float): The target head value.

        Returns:
            float: The adjusted rotational speed (n) for the given head.

        Raises:
            Exception: If an error occurs in the calculation process.
        """
        D = self.operation_point.D
        try:
            # Fetch the best efficiency point n11
            best_n11 = self.BEP_data.n11[0]            
            
            # Calculate rotational speed (n) using the constant head and D
            n = best_n11 * (H ** 0.5) / D
            return n

        except Exception as e:
            print(f"Error in adjusting rotational speed: {e}")
            raise            

    def adjust_blade_angle_for_constant_H_and_Q(self, H):        
        """
        Adjust the blade angle based on a constant head (H) and flow rate (Q).

        Args:
            H (float): The head value for which to adjust the blade angle.

        Returns:
            float: The calculated blade angle.

        Raises:
            Exception: If an error occurs in calculating the blade angle.
        """
        D = self.operation_point.D
        Q = self.operation_point.Q
        n = self.operation_point.n
        try:            
            Q11 = Q / (D**2 * H**0.5)            
            n11 = n * D / H**0.5                
            blade_angle = self.get_blade_angle(Q11, n11)            

            return blade_angle

        except Exception as e:
            print(f"Error in adjusting Q11: {e}")
            raise

    def set_head_and_adjust(self, H):
        """
        Set the head and adjust both rotational speed and blade angle accordingly.

        Args:
            H (float): The desired head value for the turbine.

        Returns:
            dict: A dictionary containing the adjusted rotational speed and blade angle.

        Raises:
            Exception: If an error occurs in the adjustment process.
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

    

    def maximize_output(self):
        H_min = 0.5
        H_max = 2.25
         
        n_range = range(93, 150, 5) # can't be float
        blade_angle_range = range(14, 19, 1)

        all_outputs = []

        for n in n_range:
            for blade_angle in blade_angle_range:
                self.operation_point.n = n
                self.operation_point.blade_angle = blade_angle
                output = self.compute_results()

                # Debugging print to check values
                # print(f"n: {n}, blade_angle: {blade_angle}, output: {output}")

                # Use copy to avoid reference issues
                all_outputs.append(copy.deepcopy(vars(output)))

        df = pd.DataFrame(all_outputs)
        df_filtered = df.dropna(subset=['power'])        
        df_capped_H = df_filtered[(df_filtered['H'] >= H_min) & (df_filtered['H'] <= H_max)]        
        max_power_row = df_capped_H.loc[df_capped_H['power'].idxmax()]

        
        # Set display options to show the full DataFrame
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        
        # Displaying the DataFrames
        print("Complete DataFrame:")
        print(df)
        print("\nFiltered DataFrame (without NaN values for power):")
        print(df_filtered)
        print("\nFiltered DataFrame with H within specified range:")
        print(df_capped_H)
        print("\nRow with maximum power in capped H range:")
        print(max_power_row)
        

        # Reset display options to default after printing
        pd.reset_option('display.max_rows')
        pd.reset_option('display.max_columns')
        pd.reset_option('display.width')

        return df, df_filtered

