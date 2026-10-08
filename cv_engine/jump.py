import numpy as np
from scipy.signal import savgol_filter

def get_scale(data, fps, height_cm):
    standing = data[:int(fps * 1.5)]
    body_px = np.nanmedian(standing[:, 2] - standing[:, 1])
    body_cm = height_cm * 0.93
    return body_cm / body_px

def jump_height(data, fps, height_cm):
    hip = data[:, 0]
    hip = np.where(np.isnan(hip), np.nanmedian(hip), hip)
    hip = savgol_filter(hip, 9, 2)
    baseline = np.median(hip[:int(fps * 1.5)])
    peak = hip.min()
    scale = get_scale(data, fps, height_cm)
    return (baseline - peak) * scale