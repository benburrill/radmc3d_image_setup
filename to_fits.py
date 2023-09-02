from radmc3dPy import image
import argparse

to_fits = argparse.ArgumentParser()
to_fits.add_argument(
    'input',
    help='the input radmc3d image file (typically image.out)'
)

to_fits.add_argument(
    '-o', metavar='FILE', dest='output',
    help='output fits file [default: <input>.fits]'
)

to_fits.add_argument(
    '--dist', metavar='DISTANCE_PC',
    help='distance to source in pc [default 140]',
    type=float, default=140.0
)

to_fits.add_argument(
    '--ra', metavar='__h__m__s',
    help='right ascension [default 15h48m05s]',
    type=str, default='15h48m05s'
)

to_fits.add_argument(
    '--dec', metavar='__d__m__s',
    help='declination [default 24d00m00s]',
    type=str, default='24d00m00s'
)

to_fits.add_argument(
    '--bandwidth', metavar='BANDWIDTH_MHZ',
    help='bandwidth in MHz (ignored for multi-frequency) [default 2000]',
    type=float, default=2000.0
)

if __name__ == '__main__':
    args = to_fits.parse_args()
    im = image.readImage(args.input)
    output = args.output if args.output is not None else args.input + '.fits'
    im.writeFits(
        output, dpc=args.dist, bandwidthmhz=args.bandwidth,
        coord=f'{args.ra} {args.dec}'
    )

    if args.output is None:
        print(f'Output fits file written to {output}')
