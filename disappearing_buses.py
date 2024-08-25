from api.bods_api import BODS_request
from time import sleep
import matplotlib.pyplot as plt
import numpy as np

with open("SECRET.txt", "r") as api_reader:
    API_KEY = api_reader.readline().strip()

request_bounds = {"boundingBox": "-0.7196044921875001,51.503406029464514,-1.1666107177734377,51.386786571080854"}
request_line = {"lineRef": "17", "operatorRef": "RBUS"}

bounds_counts = []
line_counts = []

sample_count = 100

for i in range(sample_count):
    bounds_data = BODS_request(API_KEY, "location", **request_bounds)
    line_data = BODS_request(API_KEY, "location", **request_line)

    for data, counts in zip((bounds_data, line_data), (bounds_counts, line_counts)):
        data_dicts = data.to_dict()
        count = 0
        for data_dict in data_dicts:
            if data_dict['MonitoredVehicleJourney']['LineRef'] == '17':
                count += 1
        counts.append(count)

    sleep(1)
    print(f"\r==== {i}/{sample_count} ====", end="")

print(bounds_counts)
print(line_counts)

plt.plot(np.arange(sample_count), bounds_counts, label="bounds")
plt.plot(np.arange(sample_count), line_counts, label="line")
plt.ylabel("Bus count")
plt.legend()
plt.show()

coef = np.polyfit(line_counts,bounds_counts,1)
poly1d_fn = np.poly1d(coef)

plt.scatter(line_counts, bounds_counts)
plt.plot(line_counts, poly1d_fn(line_counts), "--")
plt.xlabel("Line-based counts")
plt.ylabel("Bound-based counts")
plt.show()

print(f"all equal: {bounds_counts == line_counts}")