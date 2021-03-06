import os
import time

import numpy as np
import matplotlib.pyplot as plt


def plot_record(record, outdir="."):
    localtime = time.localtime(record.rtime)
    print(f"Plotting spectrum for {time.strftime('%Y-%m-%d %H', localtime)}")

    dirs = np.flip(np.append(record.dirs, record.dirs[0]) - np.pi/2)
    periods = 1/record.freqs
    data = np.append(record.data, np.atleast_2d(record.data[0]), axis=0)
    r, theta = np.meshgrid(periods, dirs)

    levels = np.logspace(np.log2(data.mean()), np.log2(data.max()), num=17, base=2, endpoint=False)
    colors = ("#0066ff", "#00b7ff", "#00e0ff", "#00ffff", "#00ffcc",
              "#00ff99", "#00ff00", "#99ff00", "#ccff00", "#ffff00", "#ffcc00",
              "#ff9900", "#ff6600", "#ff0000", "#b03060", "#d02090")

    # Create Axis and Figure
    fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))
    ax.set_rlim(22, 6)
    ax.set_thetalim(2*np.pi, 0)

    # Plot colors
    ax.set_rlabel_position(ax.get_rlabel_position() + 135)  # Move the tics out of the way
    ax.tick_params(labelcolor="black")
    cs1 = ax.contourf(theta, r, data, levels, colors=colors, extend="both")
    cs1.cmap.set_under("#0000cd")
    cs1.cmap.set_over("#ff00ff")
    fig.colorbar(cs1)

    # Plot contours
    ax.contour(theta, r, data, levels, colors=("k",), linewidths=(1,))

    # Plot wind (remember we're plotting from N = 0 degrees, so sin and cos are switched)
    wind_dir_rad = np.pi * (record.UD + 90) / 180
    wind_u = record.UA * np.cos(wind_dir_rad)
    wind_v = record.UA * np.sin(wind_dir_rad)
    ax.quiver(0, 22, [wind_u], [wind_v], color=['r'], scale=80)

    # Set title
    date = time.strftime("%Y/%m/%d %H%z", localtime)
    ax.set_title(f"{date}      Hs = {record.hs:0.2f}m")

    # Save and close figure
    pathtime = time.strftime("%Y%m%d%H", localtime)
    outpath = os.path.join(outdir, f"{pathtime}.spec.png")
    plt.savefig(outpath)
    plt.close(fig)
