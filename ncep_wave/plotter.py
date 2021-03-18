import os
import time

import numpy as np
import matplotlib.pyplot as plt

import ncep_wave.terminal as term
from .cache import create_spectrum_path


def plot_record(record, outdir="."):
    localtime = time.localtime(record.rtime)

    dirs = np.flip(np.append(record.dirs, record.dirs[0]) - np.pi/2)
    periods = record.freqs
    data = np.append(record.data, np.atleast_2d(record.data[0]), axis=0)
    r, theta = np.meshgrid(periods, dirs)

    levels = np.logspace(-5, np.log2(data.max()), num=17, base=2, endpoint=False)
    colors = ("#0066ff", "#00b7ff", "#00e0ff", "#00ffff", "#00ffcc",
              "#00ff99", "#00ff00", "#99ff00", "#ccff00", "#ffff00", "#ffcc00",
              "#ff9900", "#ff6600", "#ff0000", "#b03060", "#d02090")

    # Create Axis and Figure
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    ax.set_rlim(0, 0.35)
    ax.set_thetalim(2*np.pi, 0)

    # Plot colors
    ax.set_rlabel_position(ax.get_rlabel_position() + 245)  # Move the tics out of the way
    ax.tick_params(labelcolor="white")
    ticks = ax.get_yticks()
    ax.set_yticks(ticks)
    ax.set_yticklabels([f"{1/f:0.1f}" for f in ticks])
    cs1 = ax.contourf(theta, r, data, levels, colors=colors, extend="both")
    cs1.cmap.set_under("#0000cd")
    cs1.cmap.set_over("#ff00ff")

    # Plot contours
    ax.contour(theta, r, data, levels, colors=("k",), linewidths=(1,))

    # Plot wind vector (scaled so each radial tick is 10mph)
    # Translated from oceanographer's direction convention
    wind_dir_rad = np.pi * (90 - record.UD) / 180
    wind_u = -record.UA * np.cos(wind_dir_rad)
    wind_v = -record.UA * np.sin(wind_dir_rad)
    ax.quiver(0, 0, [wind_u], [wind_v],
              color=['r'],
              zorder=3,
              scale=140/2.237)  # 140 (10m/s/tick) * 2.237 (mph/m/s)

    # Set title
    date = time.strftime("%Y/%m/%d %H%z", localtime)
    ax.set_title(f"{date}      Hs = {record.hs:0.2f}m")

    # Save and close figure
    outpath = create_spectrum_path(outdir, localtime)
    plt.savefig(outpath)
    plt.close(fig)

    term.info(outpath)
