from control_simulator import ControlSimulator
from collections import deque
import os
import matplotlib.pyplot as plt
from control_PID import ControlPID  # Import the PID controller

class ControlProcessor:
    def __init__(self, refresh_rate_physical = 1, time_scale_factor = 10, max_duration = 14400):
        # Initialize simulator
        self.time_scale_factor = time_scale_factor  # Scale real time to simulation time
        self.refresh_rate_physical = refresh_rate_physical  # seconds

        self.simulator = ControlSimulator()

        # Initialize PID controller
        self.controller = ControlPID(
            Kp=1.2, Ki=0.1, Kd=0.05,  # PID coefficients
            H_tolerance=0.05,         # Head tolerance
            n_min=30, n_max=150,      # Rotational speed limits
            blade_angle_min=3, blade_angle_max=26  # Blade angle limits
        )

        # Initialize live data storage for plotting        
        maxlen = int(max_duration / self.refresh_rate_physical)

        self.time_data = deque(maxlen=maxlen)
        self.H = deque(maxlen=maxlen)
        self.Q = deque(maxlen=maxlen)
        self.blade_angle = deque(maxlen=maxlen)
        self.n = deque(maxlen=maxlen)
        self.power = deque(maxlen=maxlen)

        self.start_time = 0
        self.elapsed_physical_time = self.start_time
        self.previous_time = self.start_time  # For delta_time calculation
        
        self.cached_H_t = None
        self.cached_n_t = None


    def Q_function(self, elapsed_physical_time):
        # Introduce sinusoidal fluctuation for Q
        frequency = 0.25 / 3600  # 0.25 cycles per hour of physical time
        Q_rate = 0.625  # 50% per hour of physical time
        #Q = 3.375*0.8 * (1 + Q_rate * np.sin(2 * np.pi * frequency * elapsed_physical_time))
        #Q = max(1.25, min(Q, 5))        
        Q = 3.375    
        return Q  

    def load_data(self, file_name):
        """
        Load turbine data into the simulator.

        Args:
            file_name (str): Path to the CSV file containing turbine data.
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, file_name)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        print(f"Loading data from {filepath}...")
        self.simulator.read_hill_chart_values(filepath)
        self.simulator.filter_for_maximum_efficiency(remove=False)
        self.simulator.prepare_hill_chart_data(min_efficiency_limit=0.1)
        print(f"Data successfully loaded from {filepath}")    

    def perform_control_step(self, H_t = None, delta_time = 1):
        """
        Perform a single control step to adjust turbine parameters.

        Args:
            H_t (float): Desired head value.
            head_control_active (bool): Whether head control is active.
            delta_time (float): Time step between updates.

        Returns:
            dict: Updated state of the turbine (n, blade_angle, H).
        """
        

        if H_t: # change logic - if H_t is not none, then run this           

            # Recompute n_t only if H_t has changed
            if H_t != self.cached_H_t:
                self.cached_H_t = H_t
                best_n11 = self.simulator.BEP_data.n11[0]
                D = self.simulator.BEP_data.D[0]
                self.cached_n_t = best_n11 * (H_t ** 0.5) / D

            n_t = self.cached_n_t

            H = self.simulator.operation_point.H
            n = self.simulator.operation_point.n
            blade_angle = self.simulator.operation_point.blade_angle

            # Perform PID-based control step
            output = self.controller.control_step(
                H=H,
                H_t=H_t,
                n=n,
                n_t=n_t,
                blade_angle=blade_angle,
                delta_time=delta_time
            )

            # Update simulator state with controlled values
            self.simulator.set_operation_attribute("n", output["n"])
            self.simulator.set_operation_attribute("blade_angle", output["blade_angle"])

            return output

        return {
            "n": self.simulator.operation_point.n,
            "blade_angle": self.simulator.operation_point.blade_angle,
            "H": self.simulator.operation_point.H
        }

    def compute_outputs(self):
        """
        Compute turbine outputs using the simulator.

        Args:
            time_scale_factor (float): Factor to scale the simulation time.

        Returns:
            dict: Computed operation point data (Q11, n11, efficiency, H, power).
        """
        operation_point = self.simulator.compute_with_slicing()

        # Calculate elapsed physical time
        #computation_time = time.time() - self.start_time
        #elapsed_physical_time = computation_time * self.time_scale_factor
        elapsed_physical_time = self.elapsed_physical_time

        # Append physical time to time_data for plotting
        self.time_data.append(elapsed_physical_time)
        self.H.append(operation_point.H)
        self.Q.append(operation_point.Q)
        self.blade_angle.append(operation_point.blade_angle)
        self.n.append(operation_point.n)
        self.power.append(operation_point.power)

        return {
            "Q11": operation_point.Q11,
            "n11": operation_point.n11,
            "efficiency": operation_point.efficiency,
            "H": operation_point.H,
            "power": operation_point.power
        }    
    
    def update_simulation(self, H_t, Q, axs, log_callback = None):
        """
        Update the simulation and plots for each frame.

        Args:            
            H_t (float): Desired head for control.
            head_control_active (bool): Whether head control is active.
            axs (list): List of axes for updating plots.
        """
        # Calculate elapsed real-world computation time
        # Calculate delta time based on refresh rate
        delta_time = self.refresh_rate_physical

        # Simulate flow rate
        #Q = self.Q_function(self.elapsed_physical_time)

        # Update simulator state
        self.simulator.set_operation_attribute("Q", Q)

        # Perform control step
        output = self.perform_control_step(H_t = H_t, delta_time = delta_time)
        blade_angle = output["blade_angle"]
        n = output["n"]

        # Compute outputs and update plots
        self.compute_outputs()
        refresh_rate = self.time_scale_factor
        if self.elapsed_physical_time % refresh_rate == 0 and axs.any() != None:
            self.update_plot(axs)

        # Log current state
        status = f"Physical time = {self.elapsed_physical_time:.1f}  Q= {Q:.2f}  H= {self.simulator.operation_point.H:.2f}  n= {n:.2f}  blade angle= {blade_angle:.2f}"

        # If a log callback is provided, use it to log the output
        if log_callback:
            log_callback(status)
        else:
            # Default behavior: print to console
            print(status)
        


    def initialize_plot(self):
        """
        Initialize matplotlib plots for live visualization.
        """
        fig, axs = plt.subplots(5, 1, figsize=(8, 10), sharex=True)
        plt.subplots_adjust(hspace=0.4)
        return fig, axs

    def update_plot(self, axs):
        """
        Update the matplotlib plots with live data.

        Args:
            axs (list): List of subplot axes.
        """
        # Determine the maximum elapsed physical time
        max_physical_time = max(self.time_data) if self.time_data else 0

        # Determine the x-axis label and scaling based on the maximum physical time
        if max_physical_time > 300 * 60:  # If physical time exceeds 300 minutes (5 hours)
            time_unit = "Hours"
            time_data_scaled = [t / 3600 for t in self.time_data]  # Convert seconds to hours
        elif max_physical_time > 300:  # If physical time exceeds 300 seconds (5 minutes)
            time_unit = "Minutes"
            time_data_scaled = [t / 60 for t in self.time_data]  # Convert seconds to minutes
        else:
            time_unit = "Seconds"
            time_data_scaled = self.time_data  # Keep time in seconds

        # Clear and update each subplot
        axs[0].clear()
        axs[0].plot(time_data_scaled, self.H, label="H [m]")
        axs[0].set_ylabel("H [m]")
        axs[0].legend()

        axs[1].clear()
        axs[1].plot(time_data_scaled, self.Q, label="Q [m³/s]")
        axs[1].set_ylabel("Q [m³/s]")
        axs[1].legend()

        axs[2].clear()
        axs[2].plot(time_data_scaled, self.blade_angle, label="Blade Angle [°]")
        axs[2].set_ylabel("Blade Angle [°]")
        axs[2].legend()

        axs[3].clear()
        axs[3].plot(time_data_scaled, self.n, label="n [rpm]")
        axs[3].set_ylabel("n [rpm]")
        axs[3].legend()

        axs[4].clear()
        axs[4].plot(time_data_scaled, self.power, label="Power [W]")
        axs[4].set_ylabel("Power [W]")
        axs[4].legend()
        axs[4].set_xlabel(f"Physical Time [{time_unit}]")  # Dynamically update x-axis label
