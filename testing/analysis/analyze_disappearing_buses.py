#!/usr/bin/env python3
"""Analyze disappearing buses pattern - compare bounds vs line-based API requests."""

import os
import sys
from pathlib import Path
from time import sleep

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.bods_api import BODS_request

# Load API key
secret_path = Path(__file__).parent.parent.parent / "SECRET.txt"
if secret_path.exists():
    with open(secret_path, "r") as api_reader:
        API_KEY = api_reader.readline().strip()
else:
    API_KEY = os.environ.get("BODS_API_KEY")
    if not API_KEY:
        raise RuntimeError("Set BODS_API_KEY or create SECRET.txt in project root")

# Define request parameters
request_bounds = {
    "boundingBox": "-0.7196044921875001,51.503406029464514,-1.1666107177734377,51.386786571080854"
}
request_line = {"lineRef": "17", "operatorRef": "RBUS"}

bounds_counts = []
line_counts = []

sample_count = 100

print(f"Running {sample_count} samples comparing bounds vs line-based bus counts...")

for i in range(sample_count):
    bounds_data = BODS_request(API_KEY, "location", **request_bounds)
    line_data = BODS_request(API_KEY, "location", **request_line)

    for data, counts in zip((bounds_data, line_data), (bounds_counts, line_counts)):
        data_dicts = data.to_dict()
        count = 0
        for data_dict in data_dicts:
            if data_dict.get('MonitoredVehicleJourney', {}).get('LineRef') == '17':
                count += 1
        counts.append(count)

    sleep(1)
    print(f"\r  {i+1}/{sample_count}", end="", flush=True)

print("\n✓ Analysis complete\n")

# Plot 1: Line vs Bounds counts over time
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(np.arange(sample_count), bounds_counts, label="Bounds-based", marker='.')
plt.plot(np.arange(sample_count), line_counts, label="Line-based", marker='.')
plt.ylabel("Bus count")
plt.xlabel("Sample number")
plt.legend()
plt.title("Bus Count Comparison: Bounding Box vs Line Reference")
plt.grid(True, alpha=0.3)

# Plot 2: Scatter with regression line
plt.subplot(1, 2, 2)
plt.scatter(line_counts, bounds_counts, alpha=0.6)
coef = np.polyfit(line_counts, bounds_counts, 1)
poly1d_fn = np.poly1d(coef)
plt.plot(line_counts, poly1d_fn(line_counts), "--", color='red', label='Fit line')
plt.xlabel("Line-based counts")
plt.ylabel("Bounds-based counts")
plt.legend()
plt.title("Correlation between count methods")
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Print statistics
print(f"Bounds counts:     min={min(bounds_counts)}, max={max(bounds_counts)}, mean={np.mean(bounds_counts):.1f}")
print(f"Line counts:       min={min(line_counts)}, max={max(line_counts)}, mean={np.mean(line_counts):.1f}")
print(f"All equal: {bounds_counts == line_counts}")
print(f"Correlation: {np.corrcoef(line_counts, bounds_counts)[0,1]:.3f}")
