#!/usr/bin/env python3

import numpy as np
import argparse
import experiment
import ast
import os


def main():
    np.seterr(all='raise')
    
    fmt_class = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=fmt_class)
    examples=[]
    class StoreDictKeyPair(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            my_dict = {}
            for kv in values:
#                print(kv)
                k,v = kv.split("=")
                my_dict[k] = ast.literal_eval(v)
            examples.append(my_dict)
            setattr(namespace, self.dest, examples)
            

    parser.add_argument("--example", dest="examples", 
                        action=StoreDictKeyPair, nargs="+", 
                        metavar="KEY1=VAL1 KEY2=VAL2...")


    parser.add_argument('--num_sum', type=int, default=1,
                        help='Maximum number of terms')
    parser.add_argument('--num_prod', type=int, default=2,
                        help='Maximum number of products in a term')
    parser.add_argument('--negation', type=int, default=0, choices=[0,1],
                        help='Should negation of tensors be considered')
    parser.add_argument('--negZ', type=int, default=1, choices=[0,1],
                        help='Should <= ineauality be considered')
    parser.add_argument('--folder', type=str, default=os.getcwd(),
                        help='Path to the output folder')
    parser.add_argument('--file_name', type=str, default='model',
                        help='Name for the output MiniZinc file')
    parser.add_argument( "--var", nargs="*", type=str)
    parser.add_argument( "--input_var", nargs="*", type=str)
    
    
    args = parser.parse_args()
    experiment.learn_constraints(args.folder,args.file_name,args.examples,
                                        args.var,args.input_var,args.num_sum,
                                        args.num_prod,args.negZ,args.negation)


if __name__ == '__main__':
    main()
