class TurbineControlPID:
    def __init__(self, H_tolerance=0.00, n_min=20, n_max=150, blade_angle_min=8, blade_angle_max=21, Kp=1.0, Ki=0.0, Kd=0.0):
        """
        Initialize TurbineControlPID with configurable parameters.

        Parameters:
            H_tolerance (float): Tolerance range for the target head (H_t).
            n_min, n_max (float): Min and max limits for rotational speed.
            blade_angle_min, blade_angle_max (float): Min and max limits for blade angle.
            Kp, Ki, Kd (float): PID gains for proportional, integral, and derivative control.
        """
        self.H_tolerance = H_tolerance
        self.n_min = n_min
        self.n_max = n_max
        self.blade_angle_min = blade_angle_min
        self.blade_angle_max = blade_angle_max

        # PID parameters
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        # PID state variables
        self.error_integral = 0
        self.previous_error = 0

    def pid_adjust(self, error, delta_time):
        """
        Calculate PID adjustment based on error and time step.

        Parameters:
            error (float): Current error (H_t - H).
            delta_time (float): Time elapsed since the last control step.

        Returns:
            float: PID adjustment value.
        """
        # Proportional term
        P = self.Kp * error

        # Integral term
        self.error_integral += error * delta_time
        I = self.Ki * self.error_integral

        # Derivative term
        D = self.Kd * (error - self.previous_error) / delta_time if delta_time > 0 else 0
        self.previous_error = error

        return P + I + D

    def control_step(self, H, H_t, delta_time, n, blade_angle):
        """
        Execute a single PID control step.

        Parameters:
            H (float): Current head value.
            H_t (float): Target head value.
            delta_time (float): Time elapsed since the last control step.
            n (float): Current rotational speed.
            blade_angle (float): Current blade angle.

        Returns:
            dict: Updated values for n and blade_angle.
        """
        def within_limits(value, min_val, max_val):
            """Ensure the value stays within the defined limits."""
            return max(min_val, min(value, max_val))

        # Calculate error
        error = H_t - H

        # Calculate PID adjustment
        adjustment = self.pid_adjust(error, delta_time)

        # Adjust both n and blade_angle proportionally
        n += adjustment
        blade_angle += adjustment / 10  # Scale adjustment for blade angle

        # Ensure values stay within limits
        n = within_limits(n, self.n_min, self.n_max)
        blade_angle = within_limits(blade_angle, self.blade_angle_min, self.blade_angle_max)

        return {
            "n": n,
            "blade_angle": blade_angle
        }

def main():
    controller = TurbineControlPID(Kp=1.2, Ki=0.1, Kd=0.05)  # Tune these values as needed
    H_t = 2.15
    delta_time = 0.1  # Time step in seconds

    def calc_H(n_in, blade_angle_in):
        return H_t * (115 / n_in) * (16 / blade_angle_in)

    n_start = (50, 150, 50, 150, 115 / 1.2)
    blade_angle_start = (21, 21, 7, 7, 16 * 1.2)

    for n, blade_angle in zip(n_start, blade_angle_start):
        print(f"\nCase: n = {n:.1f}, blade_angle = {blade_angle:.1f}")

        n_prev = None
        blade_angle_prev = None

        # Initialize counter
        iteration_count = 0
        max_iterations = 50

        while (n_prev != n or blade_angle_prev != blade_angle) and iteration_count < max_iterations:
            # Calculate new head value
            H = calc_H(n, blade_angle)
            print(f"{H:.2f}, {n:.1f}, {blade_angle:.1f}")

            # Update previous values
            n_prev = n
            blade_angle_prev = blade_angle

            # Perform PID control step
            output = controller.control_step(H, H_t, delta_time, n, blade_angle)
            n = output["n"]
            blade_angle = output["blade_angle"]

            # Increment the counter
            iteration_count += 1

        if iteration_count == max_iterations:
            print("Stopped after reaching the maximum of", max_iterations, "iterations.")


if __name__ == "__main__":
    main()