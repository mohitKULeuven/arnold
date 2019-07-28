#!/usr/bin/env python3

import numpy as np
import argparse
import arnold
from pprint import pprint


def main():
    np.seterr(all='raise')

    fmt_class = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=fmt_class)
    parser.add_argument('num_sum', type=int,
                        help='Maximum number of terms')
    parser.add_argument('num_prod', type=int,
                        help='Maximum number of products in a term')
    parser.add_argument('slicing', type=int, default=0, choices=[0,1],
                        help='Should tensors be sliced')
    parser.add_argument('negation', type=int, default=0, choices=[0,1],
                        help='Should negation of tensors be considered')
    parser.add_argument('negZ', type=int, default=1, choices=[0,1],
                        help='Should <= ineauality be considered')
    parser.add_argument('folder', type=str,
                        help='Path to the output folder')
    parser.add_argument('file_name', type=str,
                        help='Name for the output MiniZinc file')
    args = parser.parse_args()

    pprint(arnold.learn_constraints(args.list_example,args.list_constants,args.num_sum,args.num_prod,args.slicing,args.negation,args.negZ,args.folder,args.file_name))


if __name__ == '__main__':
    main()
