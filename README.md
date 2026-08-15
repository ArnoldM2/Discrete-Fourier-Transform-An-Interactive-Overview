# Fourier Epicycles

Draw (almost) any figure using rotating circles (epicycles), from **_Discrete Fourier Transform_** - the idea was take from the blog 
[*La órbita de Homero Simpson*](https://bestiariotopologico.blogspot.com/2020/05/la-orbita-de-homero-simpson-una.html).

## The idea with DFT
1. Any closed curve in the plane can be viewed as a list of points $(a_n, b_n)$, and these as complex numbers $x_n = a_n + ib_n$.
2. The DFT of that list yields complex coefficients $x_k$. Each one defines an **epicycle**: cirlce of radius $R_k = |x_k|$ that rotates at an angular velocity ($\omega_k$ or simply $k$) and starts at the angle (phase) $\phi_k = \text{arg}(x_k)$.
3. IF we link all these circle together (with the center of a new circle moving right behind the tip of the previous one) and arrange them in order of radius from largest to smallest, the tip of the last circle traces -exactly- the original curve. That is the inverse DFT, geometrically speaking.
4. If we use few circles (those with the largest radius) we get a rougher but still recognizable approximation.

## Project structure

```
├── DFT.py                  # Calculates the DFT
├── epicycles.py            # Order by amplitude + positions in the chan of circles
├── shapes.py               # Predefined forms / image / raw points
├── animate.py              # Matplotlib animation (circles + arrow + trace)
├── drawing_board.py        # Window to draw your own figure with the mouse
├── main.py
├── requirements.txt 
```

## Installation

```bash
git clone https://github.com/ArnoldM2/Discrete-Fourier-Transform-An-Interactive-Overview.git
pip install -r requirements.txt
```

`opencv-python-headless` is only if you use `--image`

## Usage

```bash
# Predefined forms (square, star, heart, infinty), interactve window
python main.py --shape heart

# Save as GIF
python main.py --shape infinty --save imgs/infinity.gif

# Draw your own figure with the mouse and save the animation
python main.py --draw --save imgs/my_draw.gif

# From an image (silhoutte/line drawing with good contrast)
python main.py --image my_image.png --save imgs/my_image.gif

# Use only the 20 largest epicycles (approximation; faster to "plot")
python main.py --shape star --harmonics 20

# Without circles
python main.py --shape square --no-circles

python main.py --shape heart --cycles 2
```

- ### Examples
![til](./imgs/infinity.gif)

### Useful parameters
|Flag                   |Usage                                            |
|-----------------------|-------------------------------------------------|
|`--points N`           |How many points is the input curve resampled to (default: 200)|
|`--harmonics N`        |Use only the N largest epicycles (default: all)|
|`frames N`             |Frames per second in the animation (more: smoother, takes longer to render)|
|`--cycles N`           |How many complete revolutions before restarting the path|
|`--save PATH`          |Save as `.gif` (using Pillow) or `.mp4` (requires `ffmpeg` to be installes)|
|`--fps N`              |FPS when saving|

## Notes about `--image`

It works best with images that have **simple outlines and good contrast**: a logo, an icon, a line drawing, or cut-out silhouette. Complex photos or those with many objects will result in noisy outlines. If the result comes out empty or upside down, try adjusting `--threshold` (0-255) or adding `--invert`.

## About `--draw`

A `matplotlib` window will open: hold down the left mouse button and drag to draw; when you release the button, the curve will automatically close by connecting the end to the beginning. Press `ESC` (or close the window) when you're satisfied with the drawing so that the animation will start.

## A Little More Math (the funniest part)
- The blog used as reference derives all of this "by hand" using GeoGebra, and explains very well the geometric interpretaion of $R\sin{(\omega x + \varphi)}$ as a point rotating on a circle of radius $R$ at speed $\omega$. It's well worth taking a time to read it carefully.
- Here we use `numpy.fft.fft`, which is the *fast* (FFT) version of the same formula that appears in the blog (you can also derive it if you wish); in this project, I'm already using it directly for efficiency (recommended if `--points` is large).
- `dft.compute_dft` returns coefficients with frequencies centered a zero (`..., -2, -1, 0, 1, 2, ...`), which is the natural convention for thinking of "epicycles rotating in one direction or the other" (negative frequencies = rotating in the opposite direction).