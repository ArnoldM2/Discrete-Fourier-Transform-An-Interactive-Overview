import cv2
import numpy as np

def resample_by_arclength(points:np.ndarray, n:int) -> np.ndarray:
    """
    Reparameterize a closed curve (an array of complex numbers) into 
    n points equally spaced according to arc length.

    Parameters:
        points (np.ndarray): Draw, image points.
        n (int): new points equally spaced.
    """
    points = np.asarray(points, dtype = complex)
    if len(points) < 2:
        raise ValueError('At least 2 points are needed to resample.')
    
    # We ensure that the curve is closed (the last point = the first)
    if points[0] != points[-1]:
        points = np.append(points, points[0])
    
    # Cumulative distance (arc length) at each original point
    deltas = np.abs(np.diff(points))
    arc = np.concatenate([[0.0], np.cumsum(deltas)])
    total_length = arc[-1]

    if total_length == 0:
        raise ValueError('The curve has zero length (are all the points the same?).')
    
    # n new points, equally spaced along the arc length, without repeating 
    # the last one (to avoid duplicating the closing point)
    target = np.linspace(0, total_length, n, endpoint = False)

    # Separate linear interpolation of the real and imaginary parts
    real_interp = np.interp(target, arc, points.real)
    imag_interp = np.interp(target, arc, points.imag)

    return real_interp + 1j*imag_interp

def normalize(points:np.ndarray, target_size:float = 200, flip_y:bool = True) -> np.ndarray:
    """
    Center the curve at the origin and scale it to fit comfortably within a 
    square of side length ~target_size. Also, invert the Y-axis (if using a 
    reference image), because in images the Y-axis increases downwards, whereas 
    in the standard mathematical plane it increases upwards. If drawing on screen, 
    it remains unchanged.

    Parameters:
        points (np.ndarray): Draw, image points.
        target_size (float): 
        flip_y (bool): Flip the y-axis in case we are using an image.
    
    Returns:
        scaled (np.ndarray): the points scaled in order to fit in a square.
    """
    points = np.asarray(points, dtype = complex)
    centroid = points.mean()
    centered = points - centroid

    span = max(
        centered.real.max() - centered.real.min(),
        centered.imag.max() - centered.imag.min()
    )

    if span == 0:
        span = 1
    
    scale = target_size / span
    scaled = centered * scale

    if flip_y:
        return scaled.real - 1j*scaled.imag # y-axis inverted
    
    return scaled


# ---------------------------------------------------------------------------
# Predefined forms
# ---------------------------------------------------------------------------

def square(n:int) -> np.ndarray:
    corners = np.array([2 + 2j, -2 + 2j, -2 - 2j, 2 - 2j, 2 + 2j])
    square = resample_by_arclength(corners, n)
    
    return square


def star(n:int, points:int = 5, r_out:float = 2.0, r_in:float = 0.8) -> np.ndarray:
    angles = np.linspace(0, 2 * np.pi, 2 * points, endpoint=False)
    radii = np.array([r_out if i % 2 == 0 else r_in for i in range(2 * points)])
    verts = radii * np.exp(1j * angles)
    verts = np.append(verts, verts[0])
    star = resample_by_arclength(verts, n)

    return star


def heart(n:int) -> np.ndarray:
    t = np.linspace(0, 2 * np.pi, 2000)
    x = 16 * np.sin(t) ** 3
    y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
    pts = x + 1j * y
    heart = resample_by_arclength(pts, n)

    return heart


def infinity(n: int) -> np.ndarray:
    t = np.linspace(0, 2 * np.pi, 2000)
    x = 3 * np.cos(t)
    y = np.sin(2 * t)
    pts = x + 1j * y
    inf = resample_by_arclength(pts, n)

    return inf


PRESETS = {
    "square": square,
    "star": star,
    "heart": heart,
    "infinity": infinity,
}


def from_preset(name:str, n:int) -> np.ndarray:
    if name not in PRESETS:
        raise ValueError(f"Forma '{name}' no reconocida. Opciones: {list(PRESETS)}")

    return PRESETS[name](n)


# ---------------------------------------------------------------------------
# From an image (silhouette / drawing with a clear outline)
# ---------------------------------------------------------------------------
def from_image(path:str, n:int, threshold:int = 128, invert:bool = False) -> np.ndarray:
    """
    It extracts the largest outline from an image and converts it into
    the input closed curve. It works best with simple line drawings or
    silhouettes that have good contrast against the background (e.g.,
    a logo, an icon, or a scanned hand-drawn sketch).
    
    Parameters:
        path (str): Path to image (png/jpg/etc.)
        n (int): number of points to which the contour is resampled
        thrseshold (int): Binarization threshold (0-255)
        invert (bool): If the object is dark against a light background,
            inversion is usually not necessary; if it is the other way
            around, set invert = True.
    
    Returns:
        complex_pts (np.ndarray): Points of the figure ordered.
    """
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f'Could not read the image: {path}')

    flag = cv2.THRESH_BINARY_INV if not invert else cv2.THRESH_BINARY
    _, binary = cv2.threshold(img, threshold, 255, flag)

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        raise ValueError('No contours were found in image. Try a different --threshold or set invert = True.')

    largest = max(contours, key = cv2.contourArea)
    pts = largest.squeeze().astype(float)
    if pts.ndim != 2:
        raise ValueError('The detected contour is degenerate (very few points).')

    complex_pts = pts[:, 0] + 1j * pts[:, 1]
    complex_pts = resample_by_arclength(complex_pts)

    return complex_pts


# ---------------------------------------------------------------------------
# From a generic list of (x, y) points, e.g., captured with mouse
# ---------------------------------------------------------------------------

def from_xy(xs:np.ndarray|list, ys:np.ndarray|list, n:int) -> np.ndarray:
    pts = np.asarray(xs, dtype = float) + 1j*np.asarray(ys, dtype = float)
    pts = resample_by_arclength(pts, n)

    return pts