import numpy as np
from scipy.interpolate import PchipInterpolator
from HillChart import HillChart
from PerformanceCurve import PerformanceCurve
import copy
from turbine_data import TurbineData
import pandas as pd
import copy
import time
import matplotlib.pyplot as plt
from control_rule_based import ControlRuleBased

class ControlSimulator(HillChart):
    """Class for simulating turbine control."""    
    def __init__(self):        
        """
        Initialize the ControlSimulator without range values, 
        allowing them to be set later.
        """
        super().__init__()
        self.data = TurbineData()   
        self.control = ControlRuleBased(H_tolerance=0.1, n_step=1, blade_angle_step=0.5)
        self.operation_point = TurbineData()

        # Initialize range attributes as None (they will be set later)
        self.Q_range = None
        self.H_range = None
        self.n_range = None
        self.blade_angle_range = None   

    def set_operation_attribute(self, attribute_name, value):
        """
        Set an attribute in the operation_point data structure.

        Args:
            attribute_name (str): Name of the attribute to set.
            value (any): The value to assign to the specified attribute.
        """

        # If value is a single-element list, extract the value
        if isinstance(value, list) and len(value) == 1:
            value = value[0]
        elif isinstance(value, list):
            raise ValueError(f"Invalid value for attribute: Expected a float or a single-element list, got {value}")
        elif not isinstance(value, (float, int)):
            raise TypeError(f"Invalid type for attribute: Expected float, got {type(value).__name__}")

        setattr(self.operation_point, attribute_name, value)

    def set_ranges(self, Q_range=None, H_range=None, n_range=None, blade_angle_range=None):
        """
        Set the ranges for Q, H, n, and blade angle.

        Args:
            Q_range (array-like): Range of flow rates to iterate over.
            H_range (tuple): Range of head values (min, max).
            n_range (array-like): Range of rotational speeds.
            blade_angle_range (array-like): Range of blade angles.
        """
        self.Q_range = Q_range if Q_range is not None else np.arange(0.5, 10, 1)
        self.H_range = H_range if H_range is not None else (0, 2.15)
        self.n_range = n_range if n_range is not None else np.arange(10, 150, 5)
        self.blade_angle_range = blade_angle_range if blade_angle_range is not None else np.arange(9, 21, 2)


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

    def compute_with_slicing(self):
        """
        Wrapper method that ensures slicing is performed before computing results.
        
        Retrieves blade angle directly from self.operation_point.

        Returns:
            TurbineData: An instance containing the updated operational values.
        """
        # Retrieve blade angle from self.operation_point
        blade_angle = self.operation_point.blade_angle
        
        # Step 1: Prepare slices based on the blade angle
        n11_slice, Q11_slice, efficiency_slice = self.slice_data_for_blade_angle(blade_angle)
        
        # Step 2: Compute results using the pre-sliced data
        return self.calculate_results_from_slice(n11_slice, Q11_slice, efficiency_slice)

    def slice_data_for_blade_angle(self, blade_angle):
        """
        Perform slicing based on blade_angle and return the slices.
        
        Args:
            blade_angle (float): Blade angle to use for slicing.

        Returns:
            tuple: n11_slice, Q11_slice, efficiency_slice
        """
        # Initialize the performance curve and create a deep copy for slicing
        performance_curve = PerformanceCurve(self)
        simulator_copy = copy.deepcopy(performance_curve)
        n11_slice, Q11_slice, efficiency_slice, _ = simulator_copy.slice_hill_chart_data(selected_blade_angle=blade_angle)

        # Verify that there’s sufficient data to proceed
        if len(Q11_slice) < 2 or len(n11_slice) < 2:
            # Check if self.operation_point exists, otherwise use blade_angle info
            operation_point_info = getattr(self, 'operation_point', f"Blade angle: {blade_angle}")
            print("\n", operation_point_info)
            raise ValueError("This point is outside of the available hill chart data range.")
            

        # Return slices if sufficient data is available
        return n11_slice, Q11_slice, efficiency_slice


    def calculate_results_from_slice(self, n11_slice, Q11_slice, efficiency_slice):
        """
        Calculate and return the results for the given input parameters using pre-sliced data.

        Args:
            n11_slice, Q11_slice, efficiency_slice (arrays): Pre-sliced data arrays for interpolation.

        Returns:
            TurbineData: An instance containing the updated operational values.
        """
        Q = self.operation_point.Q
        D = self.operation_point.D
        n = self.operation_point.n
        
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

    
    def maximize_output_in_flow_range(self):
        """
        Calculate and maximize power output within the specified ranges.

        Raises:
            ValueError: If any required range is still unset (None).
        """
        # Ensure that all ranges have been set
        if any(x is None for x in (self.Q_range, self.H_range, self.n_range, self.blade_angle_range)):
            raise ValueError("Ranges for Q, H, n, and blade_angle must be set before calling this method.")

        min_H, max_H = self.H_range
        max_power_results = {}
        Q_range_len = len(self.Q_range)
        counter = 0

        # Start timing the operation
        start_time = time.time()

        # Iterate over Q_range and calculate maximum power for each Q
        for Q in self.Q_range:
            print("\nTotal progress = ", counter,'/',Q_range_len)
            counter += 1
            
            self.operation_point.Q = Q
            max_power_row = self.maximize_output(min_H, max_H)
            max_power_results[Q] = max_power_row
            
        print("\nTotal progress = ", counter,'/',Q_range_len)
        print("\nComplete")

        # End timing the operation
        end_time = time.time()
        elapsed_time = end_time - start_time

        # Print the elapsed time in seconds
        print(f"\nTotal elapsed time: {elapsed_time:.0f} seconds")

        # Plot results based on the calculated max power data
        self.plot_results(max_power_results)
        return max_power_results

    def maximize_output(self, min_H, max_H):
        """Iterate through n_range and blade_angle_range to find max power within head constraints."""
        all_outputs = []
        counter = 0
        total = len(self.n_range) * len(self.blade_angle_range)        

        # Start timing the operation
        start_time = time.time()

        for blade_angle in self.blade_angle_range:
            # Slice data based on the blade angle
            n11_slice, Q11_slice, efficiency_slice = self.slice_data_for_blade_angle(blade_angle)
            for n in self.n_range:
                counter += 1
                print(f"\rProgress for current Q = {counter}/{total}", end="")
                
                
                self.operation_point.n = n
                self.operation_point.blade_angle = blade_angle
                output = self.calculate_results_from_slice(n11_slice, Q11_slice, efficiency_slice)                
                all_outputs.append(copy.deepcopy(vars(output)))
                
        # End timing the operation
        end_time = time.time()
        elapsed_time = end_time - start_time

        # Print the elapsed time in seconds
        print(f"\nElapsed time: {elapsed_time:.0f} seconds")

        # Process the collected outputs
        df = pd.DataFrame(all_outputs).dropna(subset=['power'])
        df_capped_H = df[(df['H'] >= min_H) & (df['H'] <= max_H)]
        max_power_row = df_capped_H.loc[df_capped_H['power'].idxmax()] if not df_capped_H.empty else None

        return max_power_row

    def plot_results(self, max_power_results):
        """Generate plots and return them as figures to be displayed in GUI tabs."""
        Q_values, power_values, n_values, blade_angle_values, efficiency_values, head_values = [], [], [], [], [], []
        for Q, result in max_power_results.items():
            if result is not None:
                Q_values.append(Q)
                power_values.append(result['power'])
                n_values.append(result['n'])
                blade_angle_values.append(result['blade_angle'])
                efficiency_values.append(result['efficiency'])
                head_values.append(result['H'])

        # Create a dictionary to store figures
        figures = {}

        # Generate plots for each attribute
        for values, ylabel, title in [
            (power_values, "Power [W]", "Power vs Q"),
            (n_values, "n [rpm]", "n vs Q"),
            (blade_angle_values, "Blade Angle [°]", "Blade Angle vs Q"),
            (efficiency_values, "Efficiency [-]", "Efficiency vs Q"),
            (head_values, "H [m]", "H vs Q")
        ]:
            fig, ax = plt.subplots()
            ax.plot(Q_values, values, marker='o')
            ax.set_xlabel("Q [m^3/s]")
            ax.set_ylabel(ylabel)
            ax.set_title(title)
            ax.grid()

            # Add figure to the dictionary with title as the key
            figures[title] = fig

        return figures


