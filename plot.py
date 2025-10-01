import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Read the CSV (single-row case)
df = pd.read_csv('laser_content_spiral.csv', skipinitialspace=True)

# Step 1: Extract fields
ranges_str = df.loc[0, 'ranges']
angle_increment = float(df.loc[0, 'angle_increment'])

# Step 2: Split the semicolon-separated string into floats
range_values = []
for val in ranges_str.strip().split(';'):
    try:
        v = float(val)
        if np.isfinite(v):  # Filters out inf and NaN
            range_values.append(v)
        else:
            range_values.append(np.nan)  # mark invalid entries as NaN
    except:
        range_values.append(np.nan)

ranges = np.array(range_values)

# Step 3: Generate angle array (assume angle_min = 0)
angles = np.arange(0, len(ranges)) * angle_increment

# Step 4: Clean data
mask = np.isfinite(ranges)
ranges_clean = ranges[mask]
angles_clean = angles[mask]

# Step 5: Polar to Cartesian
x = ranges_clean * np.cos(angles_clean)
y = ranges_clean * np.sin(angles_clean)

# Step 6: Plot
plt.figure(figsize=(6, 6))
plt.scatter(x, y, s=3, color='blue')
plt.title("Laser Scan (Cartesian Plot)")
plt.xlabel("X (meters)")
plt.ylabel("Y (meters)")
plt.axis('equal')
plt.grid(True)
plt.show()
