import argparse
from slpk_merger import merge_slpks

def main():
    parser = argparse.ArgumentParser(description='Merge two SLPK files into one.')
    parser.add_argument('slpk1', help='Path to the first SLPK file')
    parser.add_argument('slpk2', help='Path to the second SLPK file')
    parser.add_argument('output', help='Path for the output merged SLPK file')
    args = parser.parse_args()
    merge_slpks(args.slpk1, args.slpk2, args.output)

if __name__ == "__main__":
    main()
