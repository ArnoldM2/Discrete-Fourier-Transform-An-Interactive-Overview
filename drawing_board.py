import numpy as np
import matplotlib.pyplot as plt

class DrawingBoard:
    def __init__(self, fig_size: tuple[float] = (6, 6)):
        self.fig, self.ax = plt.subplots(figsize = fig_size)
        self.fig.patch.set_facecolor('black')
        self.ax.set_xlim(-300, 300)
        self.ax.set_ylim(-300, 300)
        self.ax.set_facecolor('black')
        self.ax.set_title(
            'Drawing Board: Click and drag to draw. Release to finish.\n'
            'Press ESC or close the window when you are satisfied.',
            fontsize=10,
            color = '#FFFFFF'
        )
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        self.fig.subplots_adjust(left = 0, right = 1, bottom = 0)

        self.xs = []
        self.ys = []
        self.drawing = False
        (self.line,) = self.ax.plot([], [], '-o', c = '#FFFFFF', ms = 2, lw = 1.5)

        self.fig.canvas.mpl_connect('button_press_event', self._on_press)
        self.fig.canvas.mpl_connect('motion_notify_event', self._on_move)
        self.fig.canvas.mpl_connect('button_release_event', self._on_release)
        self.fig.canvas.mpl_connect('key_press_event', self._on_close)

    def _on_press(self, event):
        if event.inaxes != self.ax:
            return
        
        self.drawing = True
        self.xs, self.ys = [event.xdata], [event.ydata]
        
    def _on_move(self, event):
        if not self.drawing or event.inaxes != self.ax:
            return
        
        self.xs.append(event.xdata)
        self.ys.append(event.ydata)
        self.line.set_data(self.xs, self.ys)
        self.fig.canvas.draw_idle()
        
    def _on_release(self, event):
        self.drawing = False
        if len(self.xs) > 2:
            # Close the curve
            self.xs.append(self.xs[0])
            self.ys.append(self.ys[0])
            self.line.set_data(self.xs, self.ys)
    
    def _on_close(self, event):
        if event.key == 'escape':
            plt.close(self.fig)
    
    def get_points(self) -> np.ndarray:
        plt.show()
        if len(self.xs) < 3:
            raise RuntimeError('You did not draw any figure (you need to draw at least 3 points).')
        
        return np.array(self.xs, dtype = float) + 1j * np.array(self.ys, dtype = float)

def draw_shape() -> np.ndarray:
    drawer = DrawingBoard()

    return drawer.get_points()

if __name__ == '__main__':
    pts = draw_shape()
    print(f'{len(pts)} points captured.')