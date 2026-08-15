# from traceback import FrameSummary
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from DFT import compute_dft
from epicycles import sort_by_amplitude, epicycle_positions
# import epicycles

def build_epicycles_from_points(points:np.ndarray, n_harmonics:int|None = None) -> list[list]:
    """
    Complete Pipeline: Get Points -> DFT (FFT) -> Ordered Epicycles by AMP.

    Parameters:
        points (np.ndarray): Numpy array of the complex points of draw.
        n_harmonics (np.ndarray): If given, it only takes the biggest
            n_harmonics epicycles (less circles = low approach but fastest).
    
    Return:
        ordered (list[list]): Ordered epicycles by amp.
    """
    raw = compute_dft(points)
    ordered = sort_by_amplitude(raw)

    if n_harmonics is not None:
        ordered = ordered[:n_harmonics]
    
    return ordered

class EpicycleAnimation:
    def __init__(
        self, epicycles:list[list],
        frames:int = 300,
        cycles_to_show:int = 1,
        show_circles:bool = True,
        trace_color:str = '#FF5A36',
        fig_size:tuple[float] = (6, 6)
    ):
        self.epicycles = epicycles
        self.frames = frames
        self.cycles_to_show = cycles_to_show
        self.show_circles = show_circles

        # Fix a limit on the chart according how far the circles chain can extend.
        self.max_extent = sum(e[1] for e in self.epicycles) * 1.15 + 1e-6

        self.fig, self.ax = plt.subplots(figsize = fig_size)
        # self.ax.set_xlim(-self.max_extent, self.max_extent)
        # self.ax.set_ylim(-self.max_extent, self.max_extent)
        self.ax.set_xlim(-300, 300)
        self.ax.set_ylim(-300, 300)
        self.ax.axis('off')
        self.fig.patch.set_facecolor('#0D1117')
        self.ax.set_facecolor('#0D1117')
        self.fig.subplots_adjust(left = 0, right = 1, bottom = 0, top = 1)

        # Assets reused in each frame (more efficient than redrawing)
        self.circle_patches = []
        if self.show_circles:
            for (freq, amp, phase) in self.epicycles:
                c = plt.Circle((0, 0), amp, fill = False, color = '#3D4451', linewidth = 0.8)
                self.ax.add_patch(c)
                self.circle_patches.append(c)
        
        (self.arm_line, ) = self.ax.plot([], [], color = '#7DD3FC', lw = 1.2, marker = 'o', ms = 2, alpha = 0.9)
        (self.trace_line, ) = self.ax.plot([], [], c = trace_color, lw = 2)
        (self.tip_dot, ) = self.ax.plot([], [], "o", c = trace_color, ms = 6)

        self.trace_x = []
        self.trace_y = []

        self.ts = np.linspace(0, 2*np.pi * self.cycles_to_show, self.frames)
    
    def _update(self, frame_idx:int):
        t = self.ts[frame_idx]
        positions = epicycle_positions(self.epicycles, t)

        if self.show_circles:
            for patch, center in zip(self.circle_patches, positions[:-1]):
                patch.center = (center.real, center.imag)
        
        tip = positions[-1]

        # Restarts the trace when a new full cycle begins
        if frame_idx == 0:
            self.trace_x.clear()
            self.trace_y.clear()
        self.trace_x.append(tip.real)
        self.trace_y.append(tip.imag)
        self.trace_line.set_data(self.trace_x, self.trace_y)
        self.tip_dot.set_data([tip.real], [tip.imag])

        return self.circle_patches + [self.arm_line, self.trace_line, self.tip_dot]
    
    def run(self, interval_ms:int = 20, save_path:str|None = None, fps:int = 30):
        """
        Executes the animation. If save_path is not None, it saves the animation
        in .gif or .mp4.

        Parameters:
            interval_ms (int): Delay between frames in milliseconds.
            save_path (str): Name of the animations with full path included (optional).
            fps (int): Resolution of the animation.
        
        Returns:
            anim (plt): if save_path given.
        """
        anim = FuncAnimation(
            self.fig, self._update, frames = self.frames,
            interval = interval_ms, blit = False, repeat = True
        )

        if save_path:
            if save_path.endswith('.gif'):
                anim.save(save_path, writer = 'pillow', fps = fps)
            else:
                anim.save(save_path, fps = fps)
        plt.show()

        return anim