import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Hammer data
hammer_data = {
    "Manufacturer": [
        "Stiletto", "Stiletto", "DeWalt", "Estwing", "Vaughan & Bushnell", "Milwaukee", "Fiskars",
        "Fiskars", "Hart Tools", "Estwing", "Stanley", "Milwaukee", "Vaughan", "Vaughan", "DeWalt",
        "Milwaukee", "Milwaukee", "Estwing", "Estwing"
    ],
    "Name": [
        "TiBone III 15 Oz. Milled-Face Framing Hammer",
        "TiBone Mini 14 oz. Milled-Face Framing Hammer",
        "DWHT51452 22 oz. One-Piece Steel Hammer",
        "E3-22SM 22 oz. Solid Steel Framing Hammer",
        "RS17ML 17 oz. Milled Face Framing Hammer",
        "48-22-9023 22 oz. Smooth Face Framing Hammer",
        "IsoCore 20 oz. Milled-face Framing Hammer",
        "Pro IsoCore 17 oz. Framing Hammer",
        "HH21SCS 21 oz. Steel Hammer",
        "Ultra Series 19 oz. Milled Face Framing Hammer",
        "FatMax 28oz. AntiVibe Framing Hammer",
        "19 oz. Wood Milled Face Hickory Framing Hammer",
        "21 oz. California Framer Framing Hammer",
        "20 oz. Milled Face Rip Hammer",
        "DWHT51054 20 oz. Rip Claw Hammer",
        "17 oz. Smooth Face Framing Hammer",
        "16 oz. Smooth Face Finish Hammer",
        "E3-16S 16 oz. Straight Claw Hammer",
        "EB/15SM 15oz Milled Face Framing Hammer"
    ],
    "Category": [
        "Framing Hammer", "Framing Hammer", "Framing Hammer", "Framing Hammer", "Framing Hammer",
        "Framing Hammer", "Framing Hammer", "Framing Hammer", "Framing Hammer", "Framing Hammer",
        "Framing Hammer", "Framing Hammer", "Framing Hammer", "Framing Hammer", "Framing Hammer",
        "Framing Hammer", "Finish Hammer", "Claw Hammer", "Framing Hammer"
    ],
    "Mass (Total, g)": [
        907.2, 907.2, 635, 635, 930, 997.9, 997.9, 850.5, 816.5, 997.9, 1229.2,
        836.9, 952.5, 737.1, 789.3, 861.8, None, 793.8, 848.2
    ],
    "Length (Overall, cm)": [
        45.72, 40.64, 40.13, 40.64, 39.37, 38.1, 40.64, 40.64, 45.72, 39.12, 40.89,
        40.8, 41.91, 40.64, 35.56, 40.96, 33.02, 33.02, 39.37
    ]
}

# Axe data
axe_data = {
    "Manufacturer": [
        "Gransfors Bruks", "Fiskars", "Fiskars", "Estwing", "Gerber", "Kershaw", "Gerber",
        "Hultafors", "Hultafors", "Husqvarna", "Husqvarna", "Gerber", "SOG", "CRKT",
        "Gransfors Bruks", "Council Tool", "Council Tool", "Council Tool", "Helko Werk",
        "Gransfors Bruks", "Gerber", "SOG", "CRKT"
    ],
    "Name": [
        "Small Forest Axe", "Chopping Axe", "X11 17\"", "Sportsman's Axe 14\"",
        "14\" Freescape Hatchet", "Deschutes Bearded Hatchet", "15\" Bushcraft Hatchet",
        "Hultån Hatchet", "Ågelsjön Mini Hatchet", "13\" Wooden Handle Hatchet",
        "Composite Hatchet H900", "Gator Combo II Axe & Saw", "Camp Axe",
        "Woods Chogan T-Hawk Tomahawk", "Wildlife Hatchet", "Wood-Craft Pack Axe",
        "Wood-Craft Camp Carver Axe", "Hudson Bay Camp Axe 1.25 lb", "Pathfinder Hatchet",
        "Mini Belt Hatchet / Small Hatchet", "Pack Hatchet", "FastHawk", "Kangee Tomahawk"
    ],
    "Category": [
        "Chopping/Limbing Axe", "Chopping Axe", "Camping Axe", "Camping Hatchet", "Camping Hatchet",
        "Hatchet", "Bushcraft Hatchet", "Hatchet/Trekking Axe", "Mini Hatchet", "Hatchet",
        "Hatchet", "Camping Axe", "Camping Hatchet", "Tomahawk", "Camping Hatchet",
        "Woodcraft Axe", "Camp Axe/Carving Axe", "Camp Axe", "Hatchet", "Mini Hatchet",
        "Camping Hatchet", "Tactical Tomahawk", "Tactical Tomahawk"
    ],
    "Mass (Total, g)": [
        1000, 1619.3, 1093.1, 843.7, 635, 703.1, 1088.6, 805, 775, 1016,
        898.1, 737, 456.4, 902.6, 610, 1270.1, 1451.5, 730.3, 900, 589.7,
        589.7, 538.65, 694
    ],
    "Length (Overall, cm)": [
        50, 71.12, 44.45, 35.56, 35.56, 35.56, 38.1, 39, 23, 38.02, 34.29,
        39.6, 29.21, 48.26, 34.29, 60.96, 40.64, 35.56, 38, 24, 24.03,
        31.75, 34.92
    ]
}

# Combine and clean
df_hammers = pd.DataFrame(hammer_data).dropna(subset=["Mass (Total, g)"])
df_axes = pd.DataFrame(axe_data)
df_combined = pd.concat([df_hammers, df_axes], ignore_index=True)

# Extract and fit
x = df_combined["Length (Overall, cm)"].values
y = df_combined["Mass (Total, g)"].values

# Fit quadratic curve
coeffs = np.polyfit(x, y, deg=1)
poly = np.poly1d(coeffs)

# Generate fit line
x_fit = np.linspace(0, max(x) * 1.05, 500)
y_fit = poly(x_fit)

# Plot
fig, ax = plt.subplots()
for category in df_combined["Category"].unique():
    subset = df_combined[df_combined["Category"] == category]
    ax.scatter(subset["Length (Overall, cm)"], subset["Mass (Total, g)"], label=category)

ax.plot(x_fit, y_fit, color='black', linestyle='--', label='Quadratic Fit')

# Labels and limits
ax.set_xlim(left=0)
ax.set_ylim(bottom=0)
ax.set_xlabel("Length (Overall, cm)")
ax.set_ylabel("Mass (Total, g)")
ax.set_title("Mass vs. Length with Quadratic Best Fit")
ax.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Optionally print fit equation
print("Quadratic fit: y = {:.3f}x² + {:.3f}x + {:.3f}".format(*coeffs))
