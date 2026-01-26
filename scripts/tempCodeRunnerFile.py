import numpy as np

STATE_ANGLES = np.concatenate((np.array([90]), np.array(list(range(50, -51, -5))), np.array([-90])))
distances = STATE_ANGLES[0::2]

