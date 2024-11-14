class TurbineControl:
    def __init__(self, n_step=5, blade_angle_step=1, n_min = 20, n_max=150, blade_angle_min=8, blade_angle_max=21):
        """
        Initialize TurbineControl with configurable parameters.

        Parameters:
            n_step (float): Step size for adjusting rotational speed.
            blade_angle_step (float): Step size for adjusting blade angle.
            n_min (float): Minimum allowable rotational speed.
            n_max (float): Maximum allowable rotational speed.
            blade_angle_min (float): Minimum allowable blade angle.
            blade_angle_max (float): Maximum allowable blade angle.
        """
        self.n_step = n_step
        self.blade_angle_step = blade_angle_step
        self.n_min = n_min
        self.n_max = n_max
        self.blade_angle_min = blade_angle_min
        self.blade_angle_max = blade_angle_max

    def increase(self, value, step):
        """Increase a parameter by the given step."""
        return value + step

    def decrease(self, value, step):
        """Decrease a parameter by the given step."""
        return value - step    

    def handle_overflow(self):
        """Handle the overflow scenario."""
        print("Overflow detected: taking appropriate action.")
        # Additional overflow handling logic here

    def handle_no_flow(self):
        """Handle the overflow scenario."""
        print("Too little flow detected: taking appropriate action.")
        # Additional no flow handling logic here

    def control_step(self, H, H_t, n, n_t, blade_angle):
        """
        Execute a single control step based on the provided values.

        Parameters:
            H (float): Current head value.
            H_t (float): Target head value.
            n (float): Current rotational speed.
            n_t (float): Target rotational speed.
            blade_angle (float): Current blade angle.

        Returns:
            dict: Updated values for n and blade_angle.
        """
        if H > H_t:
            # Case 1: Head (H) is greater than the target head (H_t)
            if blade_angle >= self.blade_angle_max:
                if n < self.n_max:
                    n = self.increase(n, self.n_step)
                else:
                    self.handle_overflow()
            else:
                if n >= n_t:
                    blade_angle = self.increase(blade_angle, self.blade_angle_step)
                else:
                    n = self.increase(n, self.n_step)

        elif H < H_t:
            # Case 2: Head (H) is less than the target head (H_t)
            if blade_angle <= self.blade_angle_min:
                if n > self.n_min:
                    n = self.decrease(n, self.n_step)
                else:
                    self.handle_no_flow()
            else:
                if n <= n_t:
                    blade_angle = self.decrease(blade_angle, self.blade_angle_step)
                else:
                    n = self.decrease(n, self.n_step)

        else:
            # Case 3: Head (H) is at target head (H_t)
            if self.blade_angle_min < blade_angle < self.blade_angle_max:
                if n < n_t:
                    n = self.increase(n, self.n_step)
                elif n > n_t:
                    n = self.decrease(n, self.n_step)

        return {
            "n": n,
            "blade_angle": blade_angle
        }
    
def main():
    controller = TurbineControl()
    H_t = 2.15
    n_t = 115

    def calc_H(n_in,blade_angle_in):
        H_out = H_t * (n_t/n_in)*(16/blade_angle_in)
        return H_out
    
    n_start = (50, 150, 50, 150, 115/1.2)
    blade_angle_start = (21, 21, 7, 7, 16*1.2)
    
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
            # Print the current state
            print(f"{H:.2f}, {n:.1f}, {blade_angle:.1f}")

            # Update previous values
            n_prev = n
            blade_angle_prev = blade_angle

            # Perform control step
            output = controller.control_step(H, H_t, n, n_t, blade_angle)
            n = output["n"]
            blade_angle = output["blade_angle"]
            
            
            
            # Increment the counter
            iteration_count += 1

        # Optional: Notify if max iterations were reached
        if iteration_count == max_iterations:
            print("Stopped after reaching the maximum of",  max_iterations, "iterations.")


if __name__ == "__main__":
    main()

