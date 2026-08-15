import sys
import shapes
import argparse
from drawing_board import draw_shape
from animate import build_epicycles_from_points, EpicycleAnimation

def parse_arg():
    p = argparse.ArgumentParser(description = 'Draw figures using Fourier epicycles.')
    source = p.add_mutually_exclusive_group(required = True)
    source.add_argument('--shape', choices = list(shapes.PRESETS.keys()),
                        help = 'Use a predefined shape.')
    source.add_argument('--draw', action = 'store_true',
                        help = 'Draw your own figure with the mouse.')
    source.add_argument('--image', type = str,
                        help = 'Path to an image (silhouette/drawing) to extract its outline.')

    p.add_argument('--points', type = int, default = 200,
                   help = 'Number of points to which the curve is resampled (default: 200).')
    p.add_argument('--normalize', action = 'store_false',
                   help = 'Do not normalize the points to re-scale the figure.')
    p.add_argument('--harmonics', type = int, default = None,
                   help = 'Use only the N largest epicycles (default: all = points).')
    p.add_argument('--cycles', type = float, default = 1.0,
                   help = 'How many complete turns it traces before restarting the stroke.')
    p.add_argument('--frames', type = int, default = 300,
                   help = 'Animation frames per revolution (default: 300).')
    p.add_argument('--no-circles', action = 'store_true',
                   help = 'Do not draw the circles; only the arm and the stroke.')
    p.add_argument('--save', type = str, default = None,
                   help = 'Ouput path (.gif or .mp4).')
    p.add_argument('--fps', type = int, default = 30,
                   help = 'FPS when saving video/GIF.')
    p.add_argument('--threshold', type = int, default = 128,
                   help = 'Binarization threshold for --image (0-255).')
    p.add_argument('--invert', action = 'store_true',
                   help = 'Invert black/white when processing --image.')

    return p.parse_args()

def main():
    args = parse_arg()

    # 1. Obtain the raw curve (a_n, b_n) based on the chosen source
    if args.shape:
        raw_points = shapes.from_preset(args.shape, args.points)
        if not args.normalize:
            raw_points = shapes.normalize(raw_points, flip_y = False)

    elif args.draw:
        raw = draw_shape()
        raw_points = shapes.resample_by_arclength(raw, args.points)
        if not args.normalize:
            print('accedio')
            raw_points = shapes.normalize(raw_points, flip_y = False)

    elif args.image:
        raw_points = shapes.from_image()
        pass

    else:
        print('You must specify --shape, --draw or --image', file = sys.stderr)
        sys.exit(1)

    # 2. DFT -> Ordered epicycles by amplitude
    epicycles = build_epicycles_from_points(raw_points, n_harmonics = args.harmonics)
    print(f'Curve with {len(raw_points)} points -> {len(epicycles)} epicycles used.')

    # 3. Animation
    anim = EpicycleAnimation(
        epicycles,
        args.frames,
        args.cycles,
        not args.no_circles
    )
    anim.run(save_path = args.save, fps = args.fps)
    if args.save:
        print(f'Animation saved in {args.save}')


if __name__ == '__main__':
    main()