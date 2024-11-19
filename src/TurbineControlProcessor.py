from TurbineControlSimulator import TurbineControlSimulator
from TurbineControl import TurbineControl
from collections import deque
import time
import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np


class TurbineControlProcessor:
    """
    Processor class to handle non-GUI turbine control logic.
    """

    def __init__(self):
        # Initialize simulator and controller
        self.simulator = TurbineControlSimulator()
        self.controller = TurbineControl(H_tolerance=0.1, n_step=1, blade_angle_step=0.5)

        # Initialize live data storage for plotting
        self.time_data = deque(maxlen=240)  # Store time points up to 120s
        self.H = deque(maxlen=240)
        self.Q = deque(maxlen=240)
        self.blade_angle = deque(maxlen=240)
        self.n = deque(maxlen=240)
        self.power = deque(maxlen=240)

        self.start_time = time.time()  # Track start time for elapsed time on x-axis

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

    def update_inputs(self, Q, blade_angle, n, D):
        """
        Update turbine simulation inputs.

        Args:
            Q (float): Flow rate [m³/s].
            blade_angle (float): Blade angle [°].
            n (float): Rotational speed [rpm].
            D (float): Runner diameter [m].
        """
        self.simulator.set_operation_attribute("Q", Q)
        self.simulator.set_operation_attribute("blade_angle", blade_angle)
        self.simulator.set_operation_attribute("n", n)
        self.simulator.set_operation_attribute("D", D)

    def perform_control_step(self, target_head, head_control_active):
        """
        Perform a single control step to adjust turbine parameters.

        Args:
            target_head (float): Desired head value.
            head_control_active (bool): Whether head control is active.

        Returns:
            dict: Updated state of the turbine (n, blade_angle, H).
        """
        if head_control_active:
            H = self.simulator.operation_point.H
            n = self.simulator.operation_point.n
            blade_angle = self.simulator.operation_point.blade_angle

            output = self.controller.control_step(
                H=H,
                H_t=target_head,
                n=n,
                n_t=113.5,  # Example target RPM
                blade_angle=blade_angle
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

    def compute_outputs(self, time_scale_factor):
        """
        Compute turbine outputs using the simulator.

        Args:
            time_scale_factor (float): Factor to scale the simulation time.

        Returns:
            dict: Computed operation point data (Q11, n11, efficiency, H, power).
        """
        operation_point = self.simulator.compute_with_slicing()

        # Calculate elapsed physical time
        computation_time = time.time() - self.start_time
        elapsed_physical_time = computation_time * time_scale_factor

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
    
    def update_animation(self, frame, simulation_state, initial_Q, target_head, head_control_active, time_scale_factor, axs):
        """
        Update the simulation and plots for each frame.

        Args:
            frame (int): The current animation frame.
            simulation_state (dict): Tracks the simulation's current state.
            initial_Q (float): Initial flow rate.
            target_head (float): Desired head for control.
            head_control_active (bool): Whether head control is active.
            time_scale_factor (float): Scaling factor for physical time.
            axs (list): List of axes for updating plots.
        """
        # Calculate elapsed real-world computation time
        current_time = time.time()
        computation_time = current_time - simulation_state["last_update_time"]

        # Scale computation time to physical time
        scaled_time_delta = computation_time * time_scale_factor
        elapsed_physical_time = (current_time - simulation_state["start_time"]) * time_scale_factor

        # Update simulation state
        simulation_state["last_update_time"] = current_time

        # Introduce sinusoidal fluctuation for Q
        frequency = 0.25 / 3600  # 0.25 cycles per hour of physical time
        Q_rate = 0.5  # 50% per hour of physical time
        Q = initial_Q * (1 + Q_rate * np.sin(2 * np.pi * frequency * elapsed_physical_time))
        Q = max(2.1, min(Q, 4.3))
        simulation_state["Q"] = Q

        # Handle initial values for blade_angle and n
        if frame == 0:
            # Pass initial values for the first iteration
            blade_angle = 16.2  # Initial blade angle
            n = 113.5  # Initial RPM
        else:
            # Use the outputs from the previous control step for subsequent iterations
            output = self.perform_control_step(target_head, head_control_active)
            blade_angle = output["blade_angle"]
            n = output["n"]

        # Update simulation inputs
        self.update_inputs(
            Q=simulation_state["Q"],
            blade_angle=blade_angle,
            n=n,
            D=1.65  # Runner diameter remains unchanged
        )

        # Compute outputs and update plots
        self.compute_outputs(time_scale_factor)
        self.update_plot(axs)


def main():
    # Initialize processor and load data
    processor = TurbineControlProcessor()
    processor.load_data("Mogu_D1.65m.csv")

    # Define initial simulation inputs
    initial_Q = 3.375  
    initial_blade_angle = 16.2
    initial_n = 113.5
    D = 1.65

    processor.update_inputs(
        Q=initial_Q,  # Flow rate
        blade_angle=initial_blade_angle,  # Blade angle
        n=initial_n,  # Rotational speed
        D=D  # Runner diameter
    )
    target_head = 2.15  # Desired head
    head_control_active = True  # Enable head control

    # Initialize plots
    fig, axs = processor.initialize_plot()

    # Initialize simulation state
    simulation_state = {
        "Q": initial_Q,  # Track the current flow rate
        "start_time": time.time(),
        "last_update_time": time.time()  # To calculate scaled time deltas
    }

    # Set time scaling factor (e.g., 1 hour of real time = 1 minute of simulation time)
    time_scale_factor = 240  # Scale real time to simulation time by x60 (1 minutes = 1 second)

    # Create live updating animation
    ani = FuncAnimation(
        fig,
        lambda frame: processor.update_animation(frame, simulation_state, initial_Q, target_head, head_control_active, time_scale_factor, axs),
        interval=500  # Update every 500ms
    )

    # Display the plots
    plt.show()




if __name__ == "__main__":
    main()
