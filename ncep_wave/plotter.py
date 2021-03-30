from io import BytesIO
import time

import numpy as np
import matplotlib.pyplot as plt

import ncep_wave.terminal as term
from .cache import create_spectrum_path


def write_hs_into_png(pngdata, hs):
    hs = np.array([hs]).view(dtype=np.uint8)
    tEXt = pngdata.getvalue().find(b"tEXt") + 4
    pngdata.getbuffer()[tEXt:tEXt + 8] = hs.tobytes()


def plot_record(record, outdir=".", for_web=True):
    localtime = time.localtime(record.rtime)

    # Normalize directions and add 0 and 2pi to remove gap in plot
    dirs = (2 * np.pi) - (record.dirs - np.pi/2) % (2 * np.pi)
    dirs = np.concatenate(([0], dirs, [2 * np.pi]))

    # Create 0 and 2pi values by averaging beginning and end of the data on the direction axis
    zero_dir = np.atleast_2d(0.5 * (record.data[0] + record.data[-1]))
    data = np.concatenate((zero_dir, record.data, zero_dir), axis=0)
    r, theta = np.meshgrid(record.freqs, dirs)

    levels = np.logspace(-5, np.log2(data.max()), num=17, base=2, endpoint=False)
    colors = ("#0066ff", "#00b7ff", "#00e0ff", "#00ffff", "#00ffcc",
              "#00ff99", "#00ff00", "#99ff00", "#ccff00", "#ffff00", "#ffcc00",
              "#ff9900", "#ff6600", "#ff0000", "#b03060", "#d02090")

    # Create Axis and Figure
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='polar'))
    ax.set_rlim(0, 0.35)

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
    if for_web:
        plt.tight_layout()
    else:
        date = time.strftime("%Y/%m/%d %H%z", localtime)
        ax.set_title(f"{date}      Hs = {record.hs:0.2f}m")

    # Generate the png data
    png = BytesIO()
    plt.savefig(png, format="png")
    write_hs_into_png(png, record.hs)

    # Save and close figure
    outpath = create_spectrum_path(outdir, localtime)
    with open(outpath, "wb") as f:
        f.write(png.getbuffer())
    plt.close(fig)

    term.info(outpath)
