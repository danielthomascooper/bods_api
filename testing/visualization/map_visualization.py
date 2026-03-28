#!/usr/bin/env python3
"""Generate a map visualization for UK bus routes.

This script creates a Basemap visualization of the UK with a sample area highlighted.
"""

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

# Create a map projection for the UK
map_builder = Basemap(
    projection='merc',
    lat_0=55,
    lon_0=-4,
    resolution='h',
    area_thresh=0.05,
    llcrnrlon=-9,
    llcrnrlat=49,
    urcrnrlon=2,
    urcrnrlat=61
)

# Draw map features
map_builder.drawmapboundary(fill_color='aqua')
map_builder.fillcontinents(color='coral', lake_color='aqua')
map_builder.drawcoastlines()
map_builder.drawcountries()

# Draw a sample bounding box on the map
x1, y1 = map_builder(-25, -25)
x2, y2 = map_builder(-25, 25)
x3, y3 = map_builder(25, 25)
x4, y4 = map_builder(25, -25)
poly = Polygon([(x1, y1), (x2, y2), (x3, y3), (x4, y4)],
               facecolor='red', edgecolor='green', linewidth=3)
#  plt.gca().add_patch(poly)  # Uncomment to display the polygon

plt.savefig("map.png", dpi=150, bbox_inches="tight")
print("✓ Map visualization saved to map.png")
