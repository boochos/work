import matplotlib.pyplot as plt
import numpy as np


def cubic_bezier( p0, p1, p2, p3, t ):
    """Evaluate a point on a cubic bezier curve."""
    t2 = t * t
    t3 = t2 * t
    mt = 1 - t
    mt2 = mt * mt
    mt3 = mt2 * mt
    return mt3 * p0 + 3 * mt2 * t * p1 + 3 * mt * t2 * p2 + t3 * p3


def generate_curve_points( control_influence, asymmetry, middle_bias, ease_strength ):
    """Generate points for a curve with given parameters"""
    t = np.linspace( 0, 1, 100 )
    start_influence = control_influence * ( 1.0 - asymmetry )
    end_influence = control_influence * ( 1.0 + asymmetry )

    p0 = 0.0
    p3 = 1.0
    p1 = p0 + start_influence - ( start_influence * middle_bias )
    p2 = p3 - end_influence - ( end_influence * middle_bias )

    y = [cubic_bezier( p0, p1, p2, p3, ti ) for ti in t]
    if ease_strength != 1.0:
        y = [pow( yi, 1.0 / ease_strength ) for yi in y]
    return t, y


# Create figure with subplots
fig, ( ( ax1, ax2 ), ( ax3, ax4 ) ) = plt.subplots( 2, 2, figsize = ( 12, 12 ) )
fig.suptitle( 'Bezier Curve Parameter Effects', fontsize = 16 )

# Plot 1: CONTROL_INFLUENCE comparison
ax1.set_title( 'CONTROL_INFLUENCE Effect' )
t, y = generate_curve_points( 0.2, 0, 0, 1 )
ax1.plot( t, y, label = 'Low (0.2)' )
t, y = generate_curve_points( 0.5, 0, 0, 1 )
ax1.plot( t, y, label = 'Medium (0.5)' )
t, y = generate_curve_points( 0.8, 0, 0, 1 )
ax1.plot( t, y, label = 'High (0.8)' )
ax1.grid( True )
ax1.legend()

# Plot 2: ASYMMETRY comparison
ax2.set_title( 'ASYMMETRY Effect' )
t, y = generate_curve_points( 0.5, -0.3, 0, 1 )
ax2.plot( t, y, label = 'Negative (-0.3)' )
t, y = generate_curve_points( 0.5, 0, 0, 1 )
ax2.plot( t, y, label = 'Zero (0)' )
t, y = generate_curve_points( 0.5, 0.3, 0, 1 )
ax2.plot( t, y, label = 'Positive (0.3)' )
ax2.grid( True )
ax2.legend()

# Plot 3: MIDDLE_BIAS comparison
ax3.set_title( 'MIDDLE_BIAS Effect' )
t, y = generate_curve_points( 0.5, 0, 0.2, 1 )
ax3.plot( t, y, label = 'Low (0.2)' )
t, y = generate_curve_points( 0.5, 0, 0.5, 1 )
ax3.plot( t, y, label = 'Medium (0.5)' )
t, y = generate_curve_points( 0.5, 0, 0.8, 1 )
ax3.plot( t, y, label = 'High (0.8)' )
ax3.grid( True )
ax3.legend()

# Plot 4: EASE_STRENGTH comparison
ax4.set_title( 'EASE_STRENGTH Effect' )
t, y = generate_curve_points( 0.5, 0, 0, 0.5 )
ax4.plot( t, y, label = 'Low (0.5)' )
t, y = generate_curve_points( 0.5, 0, 0, 1.0 )
ax4.plot( t, y, label = 'Medium (1.0)' )
t, y = generate_curve_points( 0.5, 0, 0, 1.5 )
ax4.plot( t, y, label = 'High (1.5)' )
ax4.grid( True )
ax4.legend()

# Add labels and grid to all plots
for ax in [ax1, ax2, ax3, ax4]:
    ax.set_xlabel( 'Input Ratio' )
    ax.set_ylabel( 'Output Value' )
    ax.set_xlim( 0, 1 )
    ax.set_ylim( 0, 1 )

plt.tight_layout()
plt.show()

# Add a plot showing your current settings
plt.figure( figsize = ( 8, 6 ) )
plt.title( 'Your Current Settings\nControl=0.5, Asymmetry=0.3, Ease=0.5, Bias=0.6' )
t, y = generate_curve_points( 0.5, 0.3, 0.6, 0.5 )
plt.plot( t, y, 'b-', label = 'Current' )
plt.plot( [0, 1], [0, 1], 'k--', alpha = 0.3, label = 'Linear' )
plt.grid( True )
plt.legend()
plt.xlabel( 'Input Ratio' )
plt.ylabel( 'Output Value' )
plt.xlim( 0, 1 )
plt.ylim( 0, 1 )
plt.show()
