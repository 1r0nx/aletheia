#!/usr/bin/env python3

import argparse
import brute_force
import itertools
import string
import sys

# Set the main parser
parser = argparse.ArgumentParser(description="brute force of some substitution ciphers")
# Set the subparser
subparsers = parser.add_subparsers(dest="cipher", required=True)

# rot13 subparser
rot13_parser = subparsers.add_parser("rot13", help="brute force rot13 cipher")
rot13_parser.add_argument(
    "-s",
    "--string",
    type=str,
    metavar="string",
    required=True,
    help="the string to brute force",
)

# rot47 subparser
rot47_parser = subparsers.add_parser("rot47", help="brute force rot47 cipher")
rot47_parser.add_argument(
    "-s",
    "--string",
    type=str,
    metavar="string",
    required=True,
    help="the string to brute force",
)

# affine subparser
affine_parser = subparsers.add_parser("affine", help="brute force affine cipher")
affine_parser.add_argument(
    "-s",
    "--string",
    type=str,
    metavar="string",
    required=True,
    help="the string to brute force",
)

# vigenere subparser
vigenere_parser = subparsers.add_parser("vigenere", help="brute force vigenere cipher")
vigenere_parser.add_argument(
    "-s",
    "--string",
    type=str,
    metavar="string",
    required=True,
    help="the string to brute force",
)

vigenere_parser.add_argument(
    "-l",
    "--len",
    type=int,
    metavar="len",
    required=True,
    help="key len to brute force. 1 <= l <= 5. l=5 takes time. be sure to filter the results",
)

# railfence subparser
rail_fence_parser = subparsers.add_parser(
    "rail_fence", help="brute force rail fence cipher"
)
rail_fence_parser.add_argument(
    "-s",
    "--string",
    type=str,
    metavar="string",
    required=True,
    help="the string to brute force",
)

# Display help if the script is runned without a cipher mode
if len(sys.argv) == 1:
    brute_force.display_art()
    parser.print_help()
    sys.exit(0)

# Display help according to the cipher mode
if len(sys.argv) == 2:
    cmd = sys.argv[1]
    if cmd in subparsers.choices:
        subparsers.choices[cmd].print_help()
        sys.exit(0)

# Parse all the arguments
args = parser.parse_args()

if args.cipher == "rot13":
    for i in range(0, 26):
        res = brute_force.rot_13(args.string, i)
        print(f"{i:2}: {res}")

if args.cipher == "rot47":
    for i in range(0, 94):
        res = brute_force.rot_47(args.string, i)
        print(f"{i:2}: {res}")

if args.cipher == "affine":
    brute_force.affine(args.string)

if args.cipher == "vigenere":
    brute_force.vigenere(args.string, args.len)

if args.cipher == "rail_fence":
    for key in range(2, len(args.string)):
        period = 2 * (key - 1)
        for offset in range(period):
            res = brute_force.rail_fence(args.string, key, offset)
            print(f"key = {key:03} | period = {offset:03} || output = {res}")
        print("\n")
