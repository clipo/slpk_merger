import argparse
from slpk_merger import merge_slpks

def main():
    parser = argparse.ArgumentParser(description='Merge two SLPKs supporting Compact I3S folder-based structure.')
    parser.add_argument('slpk1', help='Path to the first SLPK')
    parser.add_argument('slpk2', help='Path to the second SLPK')
    parser.add_argument('output', help='Path for the output merged SLPK (with or without .slpk extension)')
    parser.add_argument('--force', action='store_true', help='Skip version check and force merge')
    args = parser.parse_args()
    merge_slpks(args.slpk1, args.slpk2, args.output, force=args.force)

if __name__ == "__main__":
    main()
