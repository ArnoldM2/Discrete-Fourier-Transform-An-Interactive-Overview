import numpy as np

def sort_by_amplitude(epicycles: list[list]) -> list[list]:
    " Order epicylces from largest to smallest ratio (amp)"
    return sorted(epicycles, key = lambda e: e[1], reverse = True)

def epicycle_positions(epicycles:list[list], t:float) -> np.ndarray:
    """
    Given a t, calculates the position (complex) of EACH vextex in the
    epicycles chain.

    Parameters:
        epicycles (list[list]): The N epicycles, without ordered yet.
    
    Returns:
        positions (np.ndarray): 
    """
    n = len(epicycles)
    positions = np.empty(n + 1, dtype = complex)
    positions[0] = 0j
    acc = 0j
    for i, (freq, amp, phase) in enumerate(epicycles):
        acc += amp * np.exp(1j * (freq * t + phase))
        positions[i + 1] = acc
    
    return positions

def full_trace(epicycles:list[list], num_samples:int = 500) -> np.ndarray:
    freqs = np.array([e[0] for e in epicycles])
    amps = np.array([e[1] for e in epicycles])
    phases = np.array([e[2] for e in epicycles])

    ts = np.linspace(0, 2*np.pi, num_samples)
    angles = np.outer(ts, freqs) + phases
    values = amps * np.exp(1j * angles)

    return values.sum(axis = 1)