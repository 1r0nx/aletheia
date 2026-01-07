#!/usr/bin/env python3

import sys
import string
import argparse
import itertools
import brute_force

# Set the main parser
parser = argparse.ArgumentParser(description="decode or brute force some ciphers")
# Set the subparser
subparsers = parser.add_subparsers(dest="cipher", required=True)

# xor subparser
xor_parser = subparsers.add_parser("xor", help="decode xor cipher")
xor_parser.add_argument(
    "-s", "--string",
    metavar="string",
    type=str,
    required=True,
    help="string or ciphertext in hex/bin/utf-8/list_of_bytes(\"[32,32,0,0,86,11,5,4]\") format"
)
xor_parser.add_argument(
    "-k", "--key",
    metavar="key",
    type=str,
    required=True,
    help="XOR key in hex/bin/utf-8 format"
)

# atbash subparser
atbash_parser = subparsers.add_parser("atbash", help="decode atbash cipher")
atbash_parser.add_argument(
    "-s",
    "--string",
    type=str,
    metavar="string",
    required=True,
    help="the string to decode",
)

# vigenere subparser
vigenere_parser = subparsers.add_parser("vigenere", help="decode vigenere cipher")
vigenere_parser.add_argument(
    "-s",
    "--string",
    type=str,
    metavar="string",
    required=True,
    help="the string to decode",
)
vigenere_parser.add_argument(
    "-k",
    "--key",
    type=str,
    metavar="key",
    required=True,
    help="the key to decode vigenere",
)

# rail_fence subparser
rail_fence = subparsers.add_parser("rail_fence", help="decode rail fence cipher")
rail_fence.add_argument(
    "-s",
    "--string",
    type=str,
    metavar="string",
    required=True,
    help="the string to decode",
)
rail_fence.add_argument(
    "-k",
    "--key",
    type=int,
    metavar="key",
    required=True,
    help="the key [2, len(string)]",
)

rail_fence.add_argument(
    "-o",
    "--offset",
    type=int,
    default=0,
    metavar="offset",
    help="the offset. by default it's 0",
)

# xor_bruteforce
xor_bruteforce_parser = subparsers.add_parser("xor_brute", help="brute force xor cipher")
xor_bruteforce_parser.add_argument(
    "-s", "--string",
    metavar="string",
    type=str,
    required=True,
    help="ciphertext in hex / bin / utf-8 format"
)
xor_bruteforce_parser.add_argument(
    "-l", "--length",
    type=int,
    metavar="len",
    required=True,
    help="XOR key length to brute-force (max=4). be sure to filter the results with grep"
)

# rot13 subparser
rot13_parser = subparsers.add_parser("rot13_brute", help="brute force rot13 cipher")
rot13_parser.add_argument(
    "-s",
    "--string",
    type=str,
    metavar="string",
    required=True,
    help="the string to brute force",
)

# rot47 subparser
rot47_parser = subparsers.add_parser("rot47_brute", help="brute force rot47 cipher")
rot47_parser.add_argument(
    "-s",
    "--string",
    type=str,
    metavar="string",
    required=True,
    help="the string to brute force",
)


# affine subparser
affine_parser = subparsers.add_parser("affine_brute", help="brute force affine cipher")
affine_parser.add_argument(
    "-s",
    "--string",
    type=str,
    metavar="string",
    required=True,
    help="the string to brute force",
)

# vigenere brute force subparser
vigenere_brute_force_parser = subparsers.add_parser(
    "vigenere_brute", help="brute force vigenere cipher"
)
vigenere_brute_force_parser.add_argument(
    "-s",
    "--string",
    type=str,
    metavar="string",
    required=True,
    help="the string to brute force",
)

vigenere_brute_force_parser.add_argument(
    "-l",
    "--len",
    type=int,
    metavar="len",
    required=True,
    help="key len to brute force. (max=5). be sure to filter the results with grep",
)

# railfence brute force subparser
rail_fence_bruteforce_parser = subparsers.add_parser(
    "rail_fence_brute", help="brute force rail fence cipher"
)
rail_fence_bruteforce_parser.add_argument(
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

if args.cipher == "atbash":
    res = brute_force.atbash_decode(args.string)
    print(res)

if args.cipher == "vigenere":
    res = brute_force.vigenere_decode(args.string, args.key)
    print(res)

if args.cipher == "rail_fence":
    res = brute_force.rail_fence(args.string, args.key, args.offset)
    print(res)

if args.cipher == "xor":
    cipher_bytes = brute_force.to_bytes(args.string)
    key_bytes = brute_force.to_bytes(args.key)
    res = brute_force.xor_bytes(cipher_bytes, key_bytes)
    print(f"\nXOR Result: {res.decode(errors="ignore")}")

if args.cipher == "xor_brute":
    cipher_bytes = brute_force.to_bytes(args.string)
    key_length = args.length
    if key_length > 4:
        print("max key len is 4.")
        sys.exit(0)
    charset = string.printable.encode()
    total_keys = len(charset) ** key_length
    print(f"[+] Total keys to test: {total_keys:,}")
    print(f"[+] Bruteforcing XOR keys of length {key_length}...\n")

    for i, key in enumerate(itertools.product(charset, repeat=key_length)):
        key_bytes = bytes(key)
        decoded = brute_force.xor_bytes(cipher_bytes, key_bytes)

        if brute_force.is_printable(decoded):
            try:
                text = decoded.decode("ascii")
                print(f"{i} KEY = {key_bytes}  ->  {text.encode()}")
            except UnicodeDecodeError:
                pass

if args.cipher == "rot13_brute":
    for i in range(0, 26):
        res = brute_force.rot_13(args.string, i)
        print(f"{i:2}: {res}")

if args.cipher == "rot47_brute":
    for i in range(0, 94):
        res = brute_force.rot_47(args.string, i)
        print(f"{i:2}: {res}")

if args.cipher == "affine_brute":
    brute_force.affine(args.string)

if args.cipher == "vigenere_brute":
    brute_force.vigenere(args.string, args.len)

if args.cipher == "rail_fence_brute":
    for key in range(2, len(args.string)):
        period = 2 * (key - 1)
        for offset in range(period):
            res = brute_force.rail_fence(args.string, key, offset)
            print(f"key = {key:03} | period = {offset:03} || output = {res}")
        print("\n")
