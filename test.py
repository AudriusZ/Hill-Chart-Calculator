

import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.interpolate import CubicSpline
from numpy.polynomial import Polynomial
import matplotlib.pyplot as plt



new_n11_values = np.linspace(30, 250, 15)    
n11_subset = [66.70460431,
73.90124703,
81.28328397,
88.84805907,
96.41283417,
104.529011,
110.9840768,
118.177001,
125.5547882,
133.484774,
139.2025126,
145.8435039]
        
Q11_subset = [1.569096865,
1.629844634,
1.696048433,
1.748718519,
1.800086173,
1.850125273,
1.873192109,
1.904429928,
1.937037351,
1.966991398,
1.994213698,
2.029603249]

plt.plot(n11_subset,Q11_subset,'o')

# Perform cubic interpolation for Q11 and efficiency
Q11_interpolator = PchipInterpolator(n11_subset, Q11_subset)
new_Q11_values = Q11_interpolator(new_n11_values)
plt.plot(new_n11_values, new_Q11_values,'green')

Q11_interpolator = CubicSpline(n11_subset, Q11_subset)
new_Q11_values = Q11_interpolator(new_n11_values)
plt.plot(new_n11_values, new_Q11_values,'red')

Q11_interpolator = Polynomial.fit(n11_subset, Q11_subset, 2)
new_Q11_values = Q11_interpolator(new_n11_values)
plt.plot(new_n11_values, new_Q11_values,'blue')



plt.show()

