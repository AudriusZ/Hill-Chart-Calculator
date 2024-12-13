import numpy as np
from control_simulator import ControlSimulator
import matplotlib.pyplot as plt

class MaximisedOutputProcessor:
    """
    A processor for maximizing turbine output based on flow, head, speed, and blade angle ranges.
    """

    def __init__(
        self,
        Q_start=2,
        Q_stop=6.5,
        Q_step=0.5,
        H_min=0.2,
        H_max=2.8,
        n_start=20,
        n_stop=180,
        n_step=1,
        blade_start=16.2,
        blade_stop=16.2,
        blade_step=1
    ):
        """
        Initialize the processor with configurable ranges for simulation.

        Args:
            Q_start, Q_stop, Q_step (float): Range and step size for flow rates.
            H_min, H_max (float): Minimum and maximum head values.
            n_start, n_stop, n_step (int): Range and step size for speed.
            blade_start, blade_stop, blade_step (float): Range and step size for blade angles.
        """
        self.simulator = ControlSimulator()
        self.Q_start = Q_start
        self.Q_stop = Q_stop
        self.Q_step = Q_step
        self.H_min = H_min
        self.H_max = H_max
        self.n_start = n_start
        self.n_stop = n_stop
        self.n_step = n_step
        self.blade_start = blade_start
        self.blade_stop = blade_stop
        self.blade_step = blade_step

    def initialize_simulation(self, hill_data, BEP_data):
        """
        Initialize the simulation with hill chart and BEP data.

        Args:
            hill_data: Hill chart data for turbine performance.
            BEP_data: Best efficiency point data for turbine operation.

        Raises:
            ValueError: If hill_data or BEP_data is missing.
        """
        if not hill_data or not BEP_data:
            raise ValueError("Hill data and BEP data must be provided to initialize the simulation.")
        self.simulator.get_data(hill_data)
        self.simulator.get_BEP_data(BEP_data)
        self.simulator.set_operation_attribute("D", BEP_data.D)

    def set_ranges(self, **ranges):
        """
        Set custom ranges for flow, head, speed, and blade angles.

        Args:
            ranges (dict): Dictionary of custom range parameters with keys:
                - 'Q_start', 'Q_stop', 'Q_step' (for flow rates)
                - 'H_min', 'H_max' (for head range)
                - 'n_start', 'n_stop', 'n_step' (for speed)
                - 'blade_angle_start', 'blade_angle_stop', 'blade_angle_step' (for blade angles)

        Raises:
            ValueError: If any required range parameter is missing or invalid.
        """
        # Extract ranges from the provided dictionary
        try:
            # Flow rates
            Q_start = ranges.get("Q_start")
            Q_stop = ranges.get("Q_stop")
            Q_step = ranges.get("Q_step")
            if Q_start is not None and Q_stop is not None and Q_step is not None:
                Q_range = np.arange(Q_start, Q_stop + Q_step, Q_step)
            else:
                raise ValueError("Missing or invalid parameters for 'Q' range.")

            # Head range
            H_min = ranges.get("H_min")
            H_max = ranges.get("H_max")
            if H_min is not None and H_max is not None:
                H_range = (H_min, H_max)
            else:
                raise ValueError("Missing or invalid parameters for 'H' range.")

            # Speed range
            n_start = ranges.get("n_start")
            n_stop = ranges.get("n_stop")
            n_step = ranges.get("n_step")
            if n_start is not None and n_stop is not None and n_step is not None:
                n_range = np.arange(n_start, n_stop + n_step, n_step)
            else:
                raise ValueError("Missing or invalid parameters for 'n' range.")

            # Blade angle range
            blade_angle_start = ranges.get("blade_angle_start")
            blade_angle_stop = ranges.get("blade_angle_stop")
            blade_angle_step = ranges.get("blade_angle_step")
            if blade_angle_start is not None and blade_angle_stop is not None and blade_angle_step is not None:
                blade_angle_range = np.arange(blade_angle_start, blade_angle_stop + blade_angle_step, blade_angle_step)
            else:
                raise ValueError("Missing or invalid parameters for 'blade_angle' range.")

            # Pass validated ranges to the simulator
            self.simulator.set_ranges(Q_range=Q_range, H_range=H_range, n_range=n_range, blade_angle_range=blade_angle_range)

        except Exception as e:
            raise ValueError(f"Error setting ranges: {str(e)}")

    
    def get_ranges(self):
        """
        Define the ranges for flow, head, speed, and blade angles, and set them in the simulator.
        """
        Q_range = np.arange(self.Q_start, self.Q_stop + self.Q_step, self.Q_step)
        H_range = (self.H_min, self.H_max)
        n_range = np.arange(self.n_start, self.n_stop + self.n_step, self.n_step)
        blade_angle_range = np.arange(self.blade_start, self.blade_stop + self.blade_step, self.blade_step)
        self.simulator.set_ranges(Q_range=Q_range, H_range=H_range, n_range=n_range, blade_angle_range=blade_angle_range)

    def run_maximisation(self):
        """
        Run the simulation to maximize turbine output within the defined ranges.

        Returns:
            max_power_results (list): The results of the maximization process.
        """
        max_power_results = self.simulator.maximize_output_in_flow_range()
        return max_power_results

    def maximised_output(self, hill_data, BEP_data, ranges=None):
        """
        Execute the full maximization workflow.

        Args:
            hill_data: Hill chart data for turbine performance.
            BEP_data: Best efficiency point data for turbine operation.
            ranges (dict, optional): Custom range parameters to override defaults.

        Returns:
            max_power_results (list): The results of the maximization process.
        """
        self.initialize_simulation(hill_data, BEP_data)
        
        if ranges:
            self.set_ranges(**ranges)
        else:
            self.get_ranges()
        self.max_power_results = self.run_maximisation()
        
        
    
    
        
    
    def create_plot(x, y, xlabel, ylabel, title, marker, color=None):
        """
        Helper function to create a standalone plot.

        Args:
            x (list): X-axis data.
            y (list): Y-axis data.
            xlabel (str): Label for the X-axis.
            ylabel (str): Label for the Y-axis.
            title (str): Title of the plot.
            marker (str): Marker style for the plot.
            color (str, optional): Line color for the plot.
        """
        fig, ax = plt.subplots()
        ax.plot(x, y, marker=marker, label=ylabel, color=color)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend()
        ax.grid(True)
        return fig

    def create_plot(self, x, y, xlabel, ylabel, title, marker='o', color=None):
        """
        Helper method to create a standalone plot.

        Args:
            x (list): X-axis data.
            y (list): Y-axis data.
            xlabel (str): Label for the X-axis.
            ylabel (str): Label for the Y-axis.
            title (str): Title of the plot.
            marker (str, optional): Marker style for the plot. Defaults to 'o'.
            color (str, optional): Line color for the plot.
        """
        fig, ax = plt.subplots()
        ax.plot(x, y, marker=marker, label=ylabel, color=color)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend()
        ax.grid(True)
        return fig

    def generate_plots(self):
        """
        Generate plots for the maximized output results.

        Args:
            max_power_results (dict): Results from the maximization process.

        Returns:
            dict: A dictionary of plot titles and their corresponding Matplotlib figures.
        """
        # Extract data
        Q_values = []
        power_values = []
        n_values = []
        blade_angle_values = []
        efficiency_values = []
        head_values = []

        for Q, result in self.max_power_results.items():
            if result is not None:
                Q_values.append(Q)
                power_values.append(result['power'])
                n_values.append(result['n'])
                blade_angle_values.append(result['blade_angle'])
                efficiency_values.append(result['efficiency'])
                head_values.append(result['H'])

        # Create plots
        plots = {
            "Power vs Q": self.create_plot(Q_values, power_values, "Q [m³/s]", "Power [W]", "Power vs Q"),
            "n vs Power": self.create_plot(power_values, n_values, "Power [W]", "Speed [rpm]", "n vs Power"),
            "Efficiency vs Q": self.create_plot(Q_values, efficiency_values, "Q [m³/s]", "Efficiency", "Efficiency vs Q"),
            "Speed (n) vs Q": self.create_plot(Q_values, n_values, "Q [m³/s]", "Speed [rpm]", "Speed vs Q"),
            "Blade Angle vs Q": self.create_plot(Q_values, blade_angle_values, "Q [m³/s]", "Blade Angle [°]", "Blade Angle vs Q"),
            "Head vs Q": self.create_plot(Q_values, head_values, "Q [m³/s]", "Head [m]", "Head vs Q"),
        }
        return plots
