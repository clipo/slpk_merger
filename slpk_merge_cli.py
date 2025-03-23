import argparse
from slpk_merger import merge_slpks

def main():
    parser = argparse.ArgumentParser(description='Merge two Compact I3S SLPKs (e.g., Integrated Mesh layers).')
    parser.add_argument('slpk1', help='Path to the first SLPK')
    parser.add_argument('slpk2', help='Path to the second SLPK')
    parser.add_argument('output', help='Path to the output merged SLPK')
    args = parser.parse_args()
    merge_slpks(args.slpk1, args.slpk2, args.output)

if __name__ == "__main__":
    main()
