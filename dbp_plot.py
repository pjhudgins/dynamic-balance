import plotly.graph_objects as go
import pandas as pd
import webbrowser
import math
import numpy as np
from astro_colors import palette
from scipy.stats import gmean

# Configuration
SWORD_NAME = "Albion Crecy"
DEMO = False

# Theme colors
theme = {
    'target': palette["red"][500],
    'tip': palette["hotorange"][500],
    'rog': palette["green"][500],
    'pommel': palette['brightblue'][500],
    'rog_grip': palette["pink"][500],
    'grip': palette['grey'][300],
    'com': palette['yellow'][500],
    'measurement': palette['yellow'][500],
    'sword': palette['neutral'][0],
    'background': palette["darkblue"][950],
    'paper': palette["darkblue"][700],
    'font': palette["neutral"][0],
}


class Sword:
    def __init__(self, mass, grip_ref, cog_ref, hilt_ext, blade_ext, lever_ref, name="Unnamed"):
        print(f"Loading sword: {name} {grip_ref} {cog_ref}")
        self.mass = float(mass)
        self.grip_ref = float(grip_ref)
        self.cog_ref = float(cog_ref)
        self.hilt_ext = float(hilt_ext)
        self.blade_ext = float(blade_ext)
        self.lever_ref = float(lever_ref)
        self.name = name
        
        # Calculate derived properties relative to grip position
        self.grip = -4.5  # Middle of hand approximately
        self.lever = self.lever_ref - self.grip_ref
        self.length = self.blade_ext - self.grip_ref
        self.com = self.cog_ref - self.grip_ref
        self.pommel = self.hilt_ext - self.grip_ref
        self.rog = None
        self.pairs = []

    def add_pair(self, point1, point2):
        """Add measurement point pair for ROG calculation"""
        point1 = point1 - self.grip_ref
        point2 = point2 - self.grip_ref
        self.pairs.append((point1, point2))


def load_swords_from_csv(filename):
    """Load sword data from CSV and return list of Sword objects"""
    df = pd.read_csv(filename)
    swords = []
    
    for _, row in df.iterrows():
        sword = Sword(
            mass=row['mass'],
            grip_ref=row['grip_ref'],
            cog_ref=row['cog_ref'],
            hilt_ext=row['hilt_ext'],
            blade_ext=row['blade_ext'],
            lever_ref=row['lever_ref'],
            name=row.get('name', f'Sword_{len(swords)+1}')
        )
        
        # Process measurement pairs
        pair_cols = [col for col in df.columns if col.startswith('pair_')]
        pair_points = [row[col] for col in pair_cols if not pd.isna(row[col])]
        
        # Add pairs and calculate ROG
        rogs = []
        for i in range(0, len(pair_points)-1, 2):
            if i+1 < len(pair_points):
                sword.add_pair(pair_points[i], pair_points[i+1])
                rogs.append(rog_from_pair(sword.com, pair_points[i]-sword.grip_ref, pair_points[i+1]-sword.grip_ref))
        
        sword.rog = gmean(rogs) if rogs else None
        swords.append(sword)
    
    return swords


def hudgins_circle(com, rog, p):
    """Calculate circle parameters for given pivot point"""
    h = (p*p - com*com - rog*rog) / (2 * (p - com))
    r = math.sqrt((com - h)**2 + rog**2)
    
    def get_x(theta):
        return h + r * math.cos(theta)
    
    def get_y(theta):
        return r * math.sin(theta)
    
    return get_x, get_y


def rog_from_pair(com, point1, point2):
    """Calculate radius of gyration from measurement pair"""
    d1 = com - point1
    d2 = point2 - com
    return math.sqrt(d1 * d2)


def plot_circle(fig, get_x, get_y, name="unnamed", style=dict(color='black'), showlegend=False, legendrank=10):
    """Plot circle with clipping for display range"""
    theta_values = [math.radians(t) for t in range(-180, 181, 3)]
    
    x_vals = []
    y_vals = []
    for t in theta_values:
        x = get_x(t)
        y = get_y(t)
        
        # Clip to reasonable display range
        if -55 <= y <= 55 and x < 120:
            x_vals.append(x)
            y_vals.append(y)
        else:
            if len(x_vals) > 0:
                fig.add_trace(go.Scatter(
                    x=x_vals, y=y_vals, mode='lines', name=name,
                    showlegend=showlegend, legendrank=legendrank, line=style,
                    hovertemplate='x=%{x:.1f}<br>y=%{y:.2f}'
                ))
                showlegend = False
            x_vals = []
            y_vals = []

    if x_vals:
        fig.add_trace(go.Scatter(
            x=x_vals, y=y_vals, mode='lines', name=name,
            showlegend=showlegend, legendrank=legendrank, line=style,
            hovertemplate='x=%{x:.1f}<br>y=%{y:.2f}'
        ))


def add_sword_geometry(fig, sword):
    """Add basic sword shape to plot"""
    # Blade
    fig.add_trace(go.Scatter(
        x=[0, sword.length], y=[0, 0], mode='lines',
        line=dict(color=theme['sword'], width=8),
        name='Blade', showlegend=False
    ))
    
    # Hilt
    fig.add_trace(go.Scatter(
        x=[sword.pommel, 0], y=[0, 0], mode='lines',
        line=dict(color=theme['sword'], width=5),
        name='Hilt', showlegend=False
    ))

    # Crossguard
    fig.add_trace(go.Scatter(
        x=[0.0, 0.0], y=[-10, 10], mode='lines',
        line=dict(color=theme['sword'], width=5),
        name='Crossguard', showlegend=False
    ))


def add_dynamics_visualization(fig, sword):
    """Add dynamic balance circles and points"""
    # Grip circles along hilt
    hilt_position = 0
    while hilt_position > sword.pommel + 2:
        get_x, get_y = hudgins_circle(sword.com, sword.rog, hilt_position)
        plot_circle(fig, get_x, get_y, "Grip Circle", 
                   {'color': theme['background'], 'width': 2}, showlegend=False)
        plot_circle(fig, get_x, get_y, "Grip Circle", 
                   {'color': theme['grip'], 'width': .5, 'dash':'dash'}, showlegend=False)
        hilt_position -= 4.5

    # Center of percussion
    cop = sword.com + sword.rog**2 / (sword.com - sword.grip)
    fig.add_trace(go.Scatter(
        x=[cop], y=[0], mode='markers',
        marker=dict(color=theme['background'], size=10),
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=[cop], y=[0], mode='markers',
        marker=dict(color=theme['grip'], size=6),
        name='Center of Percussion', showlegend=True, legendrank=7
    ))

    # Main ROG circle
    get_x, get_y = hudgins_circle(sword.com, sword.rog, sword.com + sword.rog)
    plot_circle(fig, get_x, get_y, "ROG Circle", 
               {'color': theme['background'], 'width': 5}, showlegend=False)
    plot_circle(fig, get_x, get_y, "Radius of Gyration", 
               {'color': theme['rog'], 'width': 2}, showlegend=True, legendrank=2)

    # Pivot circles for different positions
    pivot_configs = [
        (sword.length, "Pivot at Tip", theme['tip'], 6),
        (sword.length + 100, "Pivot at Target", theme['target'], 3),
        (sword.pommel, "Action at Pommel", theme['pommel'], 5)
    ]
    
    for position, name, color, rank in pivot_configs:
        get_x, get_y = hudgins_circle(sword.com, sword.rog, position)
        plot_circle(fig, get_x, get_y, f"{name} Circle", 
                   {'color': theme['background'], 'width': 3}, showlegend=False)
        plot_circle(fig, get_x, get_y, name, 
                   {'color': color, 'width': 1}, showlegend=True, legendrank=rank)

    # ROG around grip
    r_hilt_squared = (sword.com - sword.grip) ** 2 + sword.rog**2
    rog_grip = math.sqrt(r_hilt_squared) + sword.grip
    get_x, get_y = hudgins_circle(sword.com, sword.rog, rog_grip)
    plot_circle(fig, get_x, get_y, "ROG Grip Circle", 
               {'color': theme['background'], 'width': 3}, showlegend=False)
    plot_circle(fig, get_x, get_y, "ROG around Grip", 
               {'color': theme['rog_grip'], 'width': 1}, showlegend=True, legendrank=1)

    # ROG grip line
    for width, color in [(4, theme['background']), (2, theme['rog_grip'])]:
        fig.add_trace(go.Scatter(
            x=[sword.grip, sword.com], y=[0, -sword.rog], mode='lines',
            line=dict(color=color, width=width, dash="solid"),
            showlegend=False
        ))


def add_measurement_points(fig, sword):
    """Add measurement pairs and their circles"""
    legend_added = False
    
    for point1, point2 in sword.pairs:
        # Measurement points
        for size, color in [(6, theme['background']), (4, theme['measurement'])]:
            fig.add_trace(go.Scatter(
                x=[point1, point2], y=[0, 0], mode='markers',
                marker=dict(color=color, size=size),
                name='Measurements' if not legend_added and size == 4 else '',
                showlegend=not legend_added and size == 4,
                legendrank=4
            ))
        legend_added = True
        
        # Measurement circle
        get_x, get_y = hudgins_circle(sword.com, sword.rog, point1)
        plot_circle(fig, get_x, get_y, "Measurement Circle", 
                   {'color': theme['measurement'], 'width': 1, "dash":"5px 20px"}, 
                   showlegend=False)


def add_center_points(fig, sword):
    """Add center of mass and dynamic balance points"""
    # ROG line
    fig.add_trace(go.Scatter(
        x=[sword.com, sword.com], y=[0, sword.rog], mode='lines',
        line=dict(color=theme['rog'], width=2, dash="solid"),
        showlegend=False
    ))

    # Background circles for center points
    fig.add_trace(go.Scatter(
        x=[sword.com] * 3, y=[sword.rog, 0, -sword.rog], mode='markers',
        marker=dict(color=theme['background'], size=12),
        showlegend=False
    ))
    
    # Center of Mass
    fig.add_trace(go.Scatter(
        x=[sword.com], y=[0], mode='markers',
        marker=dict(color=theme['com'], size=8),
        name='Center of Mass', showlegend=True, legendrank=8
    ))
    
    # Dynamic Balance Points
    fig.add_trace(go.Scatter(
        x=[sword.com] * 2, y=[sword.rog, -sword.rog], mode='markers',
        marker=dict(color=theme['rog'], size=6),
        showlegend=False
    ))

    # DBP label
    fig.add_annotation(
        x=sword.com, y=sword.rog + 5, text="DBP", showarrow=False,
        font=dict(color=theme['rog'], size=18, family="Arial"),
        bgcolor=theme['background'], bordercolor=theme['background'], borderwidth=0
    )


def plot_sword(fig, sword, demo=False):
    """Plot complete sword with all dynamics visualization"""
    add_sword_geometry(fig, sword)
    
    if not demo:
        add_dynamics_visualization(fig, sword)
        add_measurement_points(fig, sword)
        add_center_points(fig, sword)

    # Print sword statistics
    print(f"\n{sword.name}:")
    print(f"Pommel: {sword.pommel:.2f} mm")
    print(f"Grip: {sword.grip:.2f} mm")
    print(f"COM: {sword.com:.2f} mm")
    print(f"Length: {sword.length:.2f} mm")
    print(f"ROG: {sword.rog:.2f} mm")


def configure_plot_layout(fig, sword):
    """Configure plot axes and layout"""
    fig.update_xaxes(
        range=[-40, 120], autorange=False, dtick=20,
        gridcolor='rgb(60, 60, 60)', zerolinecolor='rgb(100, 100, 100)',
        tickcolor='rgb(150, 150, 150)', linecolor='rgb(150, 150, 150)'
    )
    fig.update_yaxes(
        scaleanchor="x", scaleratio=1, dtick=20,
        gridcolor='rgb(60, 60, 60)', zerolinecolor='rgb(100, 100, 100)',
        tickcolor='rgb(150, 150, 150)', linecolor='rgb(150, 150, 150)'
    )
    
    fig.update_layout(
        height=500, width=700,
        title_text=f"Dynamic Balance Point - {sword.name}",
        title_x=0.5, title_y=0.98,
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="top", y=-0.08,
            xanchor="center", x=0.5,
            bgcolor=theme['paper'], bordercolor=theme['font'], borderwidth=1,
            font=dict(color=theme['font'], size=10)
        ),
        plot_bgcolor=theme['background'],
        paper_bgcolor=theme['paper'],
        font=dict(color=theme['font']),
        margin=dict(l=20, r=20, t=40, b=50)
    )


def plot_single_sword(sword):
    """Create and display plot for a single sword"""
    fig = go.Figure()
    plot_sword(fig, sword, demo=DEMO)
    configure_plot_layout(fig, sword)
    
    html_file = f"{sword.name.lower().replace(' ', '_')}_sword_plot.html"
    fig.write_html(html_file, auto_open=False)
    webbrowser.open(html_file)


def main():
    """Main execution function"""
    swords = load_swords_from_csv('data_swords.csv')
    
    target_sword = next((sword for sword in swords if sword.name == SWORD_NAME), None)
    
    if target_sword:
        plot_single_sword(target_sword)
    else:
        print(f"Sword '{SWORD_NAME}' not found in the data file.")
        print("Available swords:")
        for sword in swords:
            print(f"  - {sword.name}")


if __name__ == "__main__":
    main()
    