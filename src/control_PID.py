from simple_pid import PID


class ControlPID:
    def __init__(self, Kp = 1.2, Ki =0.1, Kd = 0.05, H_tolerance=0.1, n_min=20.0, n_max=150.0, blade_angle_min=8.0, blade_angle_max=21.0):
        """

        
        Initialize the ControlPID controller with PID coefficients and rule-based constraints.

        Parameters:
            Kp, Ki, Kd (float): PID coefficients.
            H_tolerance (float): Tolerance range for the target head (H_t).
            n_min, n_max (float): Limits for rotational speed.
            blade_angle_min, blade_angle_max (float): Limits for blade angle.
        """
        self.H_tolerance = H_tolerance
        self.n_min = n_min
        self.n_max = n_max
        self.blade_angle_min = blade_angle_min
        self.blade_angle_max = blade_angle_max

        # Initialize the PID controller from `simple-pid`
        self.pid = PID(Kp, Ki, Kd, setpoint=0)  # The setpoint will be set dynamically
        self.pid.output_limits = (-1, 1)  # Output range maps to the direction and strength of control

    def set_constraints(self, n_min=None, n_max=None, blade_angle_min=None, blade_angle_max=None):
        """
        Dynamically update the operational constraints.

        Parameters:
            n_min (float): Minimum rotational speed. Must be positive and less than `n_max`.
            n_max (float): Maximum rotational speed. Must be greater than `n_min`.
            blade_angle_min (float): Minimum blade angle. Must be positive and less than `blade_angle_max`.
            blade_angle_max (float): Maximum blade angle. Must be greater than `blade_angle_min`.

        Raises:
            ValueError: If any constraints are invalid.
        """
        if n_min is not None:
            if n_max is not None and n_min > n_max:
                raise ValueError("n_min must be less than n_max.")
            self.n_min = n_min

        if n_max is not None:
            if n_min is not None and n_max < n_min:
                raise ValueError("n_max must be greater than n_min.")
            self.n_max = n_max

        if blade_angle_min is not None:
            if blade_angle_max is not None and blade_angle_min > blade_angle_max:
                raise ValueError("blade_angle_min must be less than blade_angle_max.")
            self.blade_angle_min = blade_angle_min

        if blade_angle_max is not None:
            if blade_angle_min is not None and blade_angle_max < blade_angle_min:
                raise ValueError("blade_angle_max must be greater than blade_angle_min.")
            self.blade_angle_max = blade_angle_max

        print(f"Constraints updated: n_min={self.n_min}, n_max={self.n_max}, "
            f"blade_angle_min={self.blade_angle_min}, blade_angle_max={self.blade_angle_max}")


    def control_step(self, H, H_t, n, n_t, blade_angle, delta_time):
        """
        Perform a single control step using PID and rule-based logic.

        Parameters:
            H (float): Current head value.
            H_t (float): Target head value.
            n (float): Current rotational speed.
            n_t (float): Target rotational speed.
            blade_angle (float): Current blade angle.
            delta_time (float): Time step for PID calculations.

        Returns:
            dict: Updated values for n and blade_angle.
        """
        # Update the PID controller's setpoint (target head)
        self.pid.setpoint = H_t

        # Compute PID output based on current head (H) and delta_time
        pid_output = self.pid(H, dt=delta_time)

        # Reverse the PID output to account for the inverse relationship
        pid_output = -pid_output

        # Use PID output to adjust blade angle or n
        if pid_output > self.H_tolerance:
            # Head too high: Increase blade angle or increase n
            if n < n_t:
                n = min(n + pid_output, self.n_max)
            elif blade_angle < self.blade_angle_max:
                blade_angle = min(blade_angle + pid_output, self.blade_angle_max)
            elif n < self.n_max:
                n = min(n + pid_output, self.n_max)
            else:
                self.handle_overflow()
        elif pid_output < -self.H_tolerance:
            # Head too low: Decrease blade angle or decrease n
            if n>n_t:
                n = max(n + pid_output, self.n_min)  # Note: + since pid_output is negative
            elif blade_angle > self.blade_angle_min:
                blade_angle = max(blade_angle + pid_output, self.blade_angle_min)  # Note: + since pid_output is negative
            elif n > self.n_min:
                n = max(n + pid_output, self.n_min)  # Note: + since pid_output is negative
            else:
                self.handle_no_flow()
        """
        else:
            # Within tolerance; fine-tune `n` towards `n_t` based on n error
            n_error = n_t - n
            if n_error > 0:  # Current n is less than target n
                n = min(n + 1*delta_time, n_t)
            elif n_error < 0:  # Current n is greater than target n
                n = max(n - 1*delta_time, n_t)
        """

        # Enforce strict limits
        blade_angle = max(self.blade_angle_min, min(blade_angle, self.blade_angle_max))
        n = max(self.n_min, min(n, self.n_max))

        # Log the PID adjustment
        # print(f"PID Output: {pid_output:.2f}, Blade Angle: {blade_angle:.2f}, n: {n:.2f}")
        
        # Return the updated parameters
        return {
            "n": n,
            "blade_angle": blade_angle
        }




    def handle_overflow(self):
        """Handle overflow condition."""
        print("Overflow detected: taking appropriate action.")

    def handle_no_flow(self):
        """Handle low-flow condition."""
        print("Too little flow detected: taking appropriate action.")


