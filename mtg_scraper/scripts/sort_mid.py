#sort_mid.py
#Claire Tinati
#January 23, 2018
"""Script to display the sorted mid-price results of the input file."""

import sys
import json


def main():
    l= json.load(open(sys.argv[1]))
    l.sort(key=(lambda x: float(x["Mid"][1:])))
    for i in l:
        print "%s (%s): %s" % (i["Name"], i["Code"], i["Mid"])



if __name__ == "__main__":
    main()
