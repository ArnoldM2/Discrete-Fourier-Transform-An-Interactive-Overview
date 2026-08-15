import numpy as np

def compute_dft(points: np.ndarray) -> list[list]:
    """
    Computes the Discrete Fourier Transform of a closed curve.

    Parameters:
        points (np.ndarray): Array of complex numbers (N,)
            Points of the curve, x_n = a_n + i*b_n
    
    Returns:
        Epicycles (list[list]): The N epicycles, without ordered yet.
            The frequencies are returned centered at 0 (..., -2, -1, 0, 1, 2, ...)
    """
    N = len(points)
    if N == 0:
        return []
    
    # x_k = (1/N) * sum(x_n * exp(-i*2*pi*k*n / N))
    coeffs = np.fft.fft(points) / N

    freqs = np.fft.fftfreq(N, d = 1 / N).astype(int)
    epicycles = [
        [int(freq), float(abs(coeff)), np.angle(coeff)] for freq, coeff in zip(freqs, coeffs)
    ]

    return epicycles

def inverse_dft(epicycles: list[list], t:float) -> complex:
    total = 0j
    for (freq, amp, phase) in epicycles:
        total += amp * np.exp(1j * (freq * t + phase))
    
    return total