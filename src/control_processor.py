from control_simulator import ControlSimulator
from collections import deque
import os
import matplotlib.pyplot as plt
from control_PID import ControlPID  # Import the PID controller

class ControlProcessor:
    def __init__(self, refresh_rate_physical=1, time_scale_factor=1, max_duration=14400):
        """
        Initialize the ControlProcessor with simulation parameters.

        Args:
            refresh_rate_physical (int): Physical time step for simulation updates (in seconds).
            time_scale_factor (float): Factor to scale real time to simulation time.
            max_duration (int): Maximum simulation duration in seconds (default: 4 hours).
        """
        self.time_scale_factor = time_scale_factor  # Scale real time to simulation time
        self.refresh_rate_physical = refresh_rate_physical  # Time step for updates

        # Initialize the simulator instance
        self.simulator = ControlSimulator()

        self.settings = {
            "Kp": 1.2,              # PID control coefficient for proportional control
            "Ki": 0.1,              # PID control coefficient for integral control
            "Kd": 0.05,             # PID control coefficient for derivative control
            "H_tolerance": 0.05,    # Tolerance for head control
            "n_min": 30,            # Minimum rotational speed limit
            "n_max": 150,           # Maximum rotational speed limit
            "blade_angle_min": 3.5,   # Minimum blade angle
            "blade_angle_max": 28.5   # Maximum blade angle
        }

        self.continue_simulation = False

        # Initialize the PID controller with predefined coefficients and constraints
        self.controller = ControlPID(
            Kp=self.settings["Kp"],
            Ki=self.settings["Ki"],
            Kd=self.settings["Kd"],
            H_tolerance=self.settings["H_tolerance"],
            n_min=self.settings["n_min"],
            n_max=self.settings["n_max"],
            blade_angle_min=self.settings["blade_angle_min"],
            blade_angle_max=self.settings["blade_angle_max"]
        )


        # Initialize data storage for live plotting, with maximum length based on simulation duration
        maxlen = int(max_duration / self.refresh_rate_physical)
        self.time_data = deque(maxlen=maxlen)
        self.H = deque(maxlen=maxlen)
        self.Q = deque(maxlen=maxlen)
        self.blade_angle = deque(maxlen=maxlen)
        self.n = deque(maxlen=maxlen)
        self.power = deque(maxlen=maxlen)

        # Initialize time variables for simulation
        self.start_time = 0
        self.elapsed_physical_time = self.start_time
        self.previous_time = self.start_time  # For delta_time calculation

        # Cache variables for optimization
        self.cached_H_t = None
        self.cached_n_t = None
        
    def update_control_settings(self, control_settings):
        self.settings = control_settings        
        

    def initialize_simulation(self, hill_data, BEP_data, initial_conditions=None, max_duration=14400):
        """
        Initialize the simulation with hill chart and best efficiency point (BEP) data.

        Args:
            hill_data: Hill chart data for turbine performance.
            BEP_data: Best efficiency point data for turbine operation.
            initial_conditions (dict): Initial conditions for the turbine (e.g., blade angle, speed).
            max_duration (int): Maximum duration of the simulation in seconds.
        """
        # Initialize current simulation parameters
        self.current_values = {
            'Q': None,
            'H_t': None,
            'blade_angle': None,
            'n': None
        }

        # Load hill chart and BEP data into the simulator
        self.simulator.get_data(hill_data)
        self.simulator.get_BEP_data(BEP_data)

        # Reset simulation timing and duration
        self.start_time = 0
        self.elapsed_physical_time = self.start_time
        self.max_duration = max_duration

        # If no initial conditions are provided, use defaults from BEP data
        if not initial_conditions:
            initial_conditions = {
                "blade_angle": BEP_data.blade_angle,
                "n": BEP_data.n,
                "Q": BEP_data.Q,
                "D": BEP_data.D
            }

        # Apply initial conditions to the simulator
        for attribute, value in initial_conditions.items():
            self.simulator.set_operation_attribute(attribute, value)

        # Precompute initial outputs to ensure readiness for simulation
        self.compute_outputs()
    
    def set_continue_simulation(self, continue_simulation):
        self.continue_simulation = continue_simulation

    def run_simulation(self, control_parameters, axs=None, log_callback=None):
        """
        Run the simulation loop, adapting parameters dynamically.

        Args:
            control_parameters (dict): Target values and adjustment rates for control.
            axs (list): List of matplotlib axes for live plotting.
            log_callback (callable): Optional callback for logging status updates.
        """
        if axs is None:
            raise ValueError("axs parameter is required for plotting.")

        # Run simulation continuously
        while self.continue_simulation:  # Replace this with a termination condition as needed

            # Adjust control parameters dynamically
            for param, value in control_parameters.items():
                if not param.endswith("_rate"):  # Skip rate-related parameters
                    rate_param = f"{param}_rate"
                    target_value = value
                    rate_value = control_parameters.get(rate_param)

                    if target_value is not None and rate_value is not None:
                        # Initialize the current value if not already set
                        if self.current_values[param] is None:
                            self.current_values[param] = target_value

                        # Increment or decrement the current value towards the target
                        delta = rate_value * self.refresh_rate_physical
                        if self.current_values[param] < target_value:
                            self.current_values[param] = min(self.current_values[param] + delta, target_value)
                        elif self.current_values[param] > target_value:
                            self.current_values[param] = max(self.current_values[param] - delta, target_value)

            # Update simulation state based on adjusted parameters
            current_control_parameters = control_parameters.copy()
            current_control_parameters.update(self.current_values)


            control_settings = self.settings
            self.update_simulation(current_control_parameters, control_settings, axs, log_callback=log_callback)

            # Increment the simulation time
            self.elapsed_physical_time += self.refresh_rate_physical

        
    def Q_function(self, elapsed_physical_time):
        """
        Compute a sinusoidal fluctuation for flow rate (Q).

        Args:
            elapsed_physical_time (float): Time elapsed in the simulation.

        Returns:
            float: Computed flow rate (Q).
        """
        # Frequency and rate for sinusoidal fluctuation
        frequency = 0.25 / 3600  # 0.25 cycles per hour
        Q_rate = 0.625  # 50% fluctuation per hour

        # Flow rate is set to a constant value for now
        Q = 3.375
        return Q

    def load_data(self, file_name):
        """
        Load turbine data into the simulator from a file.

        Args:
            file_name (str): Path to the CSV file containing turbine data.

        Raises:
            FileNotFoundError: If the specified file does not exist.
        """
        # Get the absolute path to the file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, file_name)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        # Load hill chart data into the simulator
        print(f"Loading data from {filepath}...")
        self.simulator.read_hill_chart_values(filepath)
        self.simulator.filter_for_maximum_efficiency(remove=False)
        self.simulator.prepare_hill_chart_data(min_efficiency_limit=0.1)
        print(f"Data successfully loaded from {filepath}")

    def perform_control_step(self, H_t=None, delta_time=1):
        """
        Perform a single control step using the PID controller.

        Args:
            H_t (float): Desired head value (optional).
            delta_time (float): Time step for the control update.

        Returns:
            dict: Updated state of the turbine (n, blade_angle, H).
        """
        if H_t:  # Execute only if a target head value is provided
            # Recompute target rotational speed (n_t) only if the head target (H_t) changes
            if H_t != self.cached_H_t:
                self.cached_H_t = H_t
                best_n11 = self.simulator.BEP_data.n11[0]
                D = self.simulator.BEP_data.D[0]
                self.cached_n_t = best_n11 * (H_t ** 0.5) / D

            n_t = self.cached_n_t  # Retrieve cached target speed

            # Retrieve current simulation state
            H = self.simulator.operation_point.H
            n = self.simulator.operation_point.n
            blade_angle = self.simulator.operation_point.blade_angle

            # Execute a control step using the PID controller
            output = self.controller.control_step(
                H=H,
                H_t=H_t,
                n=n,
                n_t=n_t,
                blade_angle=blade_angle,
                delta_time=delta_time
            )

            # Update the simulator state with the controlled values
            self.simulator.set_operation_attribute("n", output["n"])
            self.simulator.set_operation_attribute("blade_angle", output["blade_angle"])

            return output

        # Return current state if no control is performed
        return {
            "n": self.simulator.operation_point.n,
            "blade_angle": self.simulator.operation_point.blade_angle,
            "H": self.simulator.operation_point.H
        }

    def compute_outputs(self):
        """
        Compute turbine outputs and update live data for plotting.

        Returns:
            dict: Computed operation point data (Q11, n11, efficiency, H, power).
        """
        # Compute the operation point of the turbine
        operation_point = self.simulator.compute_with_slicing()

        # Append current physical time and outputs to data storage
        elapsed_physical_time = self.elapsed_physical_time
        self.time_data.append(elapsed_physical_time)
        self.H.append(operation_point.H)
        self.Q.append(operation_point.Q)
        self.blade_angle.append(operation_point.blade_angle)
        self.n.append(operation_point.n)
        self.power.append(operation_point.power)

        # Return the computed data for reference
        return {
            "Q11": operation_point.Q11,
            "n11": operation_point.n11,
            "efficiency": operation_point.efficiency,
            "H": operation_point.H,
            "power": operation_point.power
        }

    def update_simulation(self, control_parameters, control_settings, axs, log_callback=None):
        """
        Update the simulation state and refresh plots.

        Args:
            control_parameters (dict): Control parameters to apply to the simulation.
            axs (list): List of matplotlib axes for updating plots.
            log_callback (callable): Optional callback for logging the state.
        """
        # Determine the delta time for simulation updates
        delta_time = self.refresh_rate_physical        

        self.simulator.set_operation_attribute("Q", control_parameters['Q'])
        # Control head (H) or directly set operational parameters
        head_control = control_parameters['head_control']
        blade_angle_lock = control_parameters['blade_angle_lock']
        n_lock = control_parameters['n_lock']

        
        self.controller.set_constraints(
                blade_angle_min = control_settings['blade_angle_min'],
                blade_angle_max = control_settings['blade_angle_max'],
                n_min=control_settings['n_min'],
                n_max=control_settings['n_max']
                )
        
        # Handle blade angle constraints
        if blade_angle_lock:
            self.controller.set_constraints(
                blade_angle_min = control_parameters['blade_angle'],
                blade_angle_max = control_parameters['blade_angle']
                )
        else:
            self.controller.set_constraints(
                blade_angle_min = self.settings['blade_angle_min'],
                blade_angle_max = self.settings['blade_angle_max']
                )
            
        # Handle rotational speed constraints      
        # Further work needed n_t resets in PID step  
        """
        if n_lock:
            self.controller.set_constraints(
                n_min=control_parameters['n'],
                n_max=control_parameters['n']
            )
        else:
            self.controller.set_constraints(
                n_min=self.settings['n_min'],
                n_max=self.settings['n_max']
            )
        """

        if head_control:
            self.perform_control_step(H_t=control_parameters['H_t'], delta_time=delta_time)
        else:
            self.simulator.set_operation_attribute("n", control_parameters['n'])
            self.simulator.set_operation_attribute("blade_angle", control_parameters['blade_angle'])

        # Compute outputs and refresh the plots
        self.compute_outputs()
        refresh_rate = self.time_scale_factor
        if self.elapsed_physical_time % refresh_rate == 0 and axs.any() is not None:
            self.update_plot(axs)

        # Log the current simulation state
        blade_angle = self.simulator.operation_point.blade_angle
        n = self.simulator.operation_point.n
        Q = self.simulator.operation_point.Q
        H = self.simulator.operation_point.H
        status = f"Physical time = {self.elapsed_physical_time:.1f}  Q= {Q:.2f}  H= {H:.2f}  n= {n:.2f}  blade angle= {blade_angle:.2f}"

        # Output log message via callback or default to console
        if log_callback:
            log_callback(status)
        else:
            print(status)

    def initialize_plot(self):
        """
        Initialize matplotlib plots for live data visualization.

        Returns:
            tuple: Matplotlib figure and axes objects for plotting.
        """
        fig, axs = plt.subplots(5, 1, figsize=(8, 10), sharex=True)
        plt.subplots_adjust(hspace=0.4)
        return fig, axs

    def update_plot(self, axs):
        """
        Update the matplotlib plots with the latest simulation data.

        Args:
            axs (list): List of subplot axes.
        """
        # Determine the appropriate time scale for plotting
        max_physical_time = max(self.time_data) if self.time_data else 0

        if max_physical_time > 300 * 60:  # If time exceeds 5 hours
            time_unit = "Hours"
            time_data_scaled = [t / 3600 for t in self.time_data]  # Convert seconds to hours
        elif max_physical_time > 300:  # If time exceeds 5 minutes
            time_unit = "Minutes"
            time_data_scaled = [t / 60 for t in self.time_data]  # Convert seconds to minutes
        else:
            time_unit = "Seconds"
            time_data_scaled = self.time_data  # Keep time in seconds

        # Update each subplot with the respective data
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
        axs[4].set_xlabel(f"Physical Time [{time_unit}]")

        # Refresh the figure to display updated plots
        axs[0].figure.canvas.draw()
        axs[0].figure.canvas.flush_events()
