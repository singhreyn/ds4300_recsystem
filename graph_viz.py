import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

fig, ax = plt.subplots(1, 1, figsize=(10, 8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 8)
ax.axis('off')
ax.set_facecolor('#191414')
fig.patch.set_facecolor('#191414')

# Node positions
strokes = [
    (4.5, 6.5, "Last Nite"),
    (3.0, 5.5, "Someday"),
    (2.5, 4.0, "Is This It"),
    (3.5, 2.5, "Barely Legal"),
    (5.5, 2.0, "Reptilia"),
    (6.5, 3.5, "12:51"),
]
regina = [
    (7.5, 6.5, "The Call"),
    (8.5, 5.0, "Two Birds"),
    (7.0, 4.0, "Samson"),
]
recs = [
    (1.5, 6.5, "Passenger Seat"),
    (1.0, 4.0, "Northbound"),
    (2.0, 2.0, "Sharp Edges"),
    (5.0, 0.8, "HandClap"),
    (7.5, 1.5, "Symphony of\nDestruction"),
]

# Edges 
connections = {
    "Passenger Seat": ["Last Nite", "Barely Legal"],
    "Northbound":     ["Is This It", "Someday"],
    "Sharp Edges":    ["Last Nite", "Someday", "Is This It"],
    "HandClap":       ["Last Nite", "Barely Legal"],
    "Symphony of\nDestruction": ["Reptilia", "12:51"],
}

pos = {}
for x, y, name in strokes + regina + recs:
    pos[name] = (x, y)

for rec, seeds in connections.items():
    for seed in seeds:
        if seed in pos and rec in pos:
            x_vals = [pos[seed][0], pos[rec][0]]
            y_vals = [pos[seed][1], pos[rec][1]]
            ax.plot(x_vals, y_vals, color='#444444', linewidth=1.2, zorder=1)

# Draw nodes 
for x, y, name in strokes:
    ax.scatter(x, y, s=600, color='#1DB954', zorder=3)
    ax.text(x, y - 0.4, name, ha='center', fontsize=7, color='white')

for x, y, name in regina:
    ax.scatter(x, y, s=600, color='#4A90D9', zorder=3)
    ax.text(x, y - 0.4, name, ha='center', fontsize=7, color='white')

for x, y, name in recs:
    ax.scatter(x, y, s=800, color='#F26522', zorder=3)
    ax.text(x, y - 0.45, name, ha='center', fontsize=7, color='white')

# Legend
legend = [
    mpatches.Patch(color='#1DB954', label='The Strokes'),
    mpatches.Patch(color='#4A90D9', label='Regina Spektor'),
    mpatches.Patch(color='#F26522', label='Recommendations'),
]
ax.legend(handles=legend, loc='upper center', facecolor='#2D2D2D',
          labelcolor='white', fontsize=9, framealpha=0.8)

plt.tight_layout()
plt.savefig('graph_viz.png', dpi=150, bbox_inches='tight',
            facecolor='#191414')

print("done")
