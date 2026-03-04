#!/usr/bin/env python3

import re
import sys
import ast
import math
import string
import binascii
import itertools

# ─── ANSI color helpers ────────────────────────────────────────────────────────
_RESET  = "\033[0m"
_BOLD   = "\033[1m"
_DIM    = "\033[2m"
_CYAN   = "\033[36m"
_GREEN  = "\033[32m"
_YELLOW = "\033[33m"
_RED    = "\033[31m"
_BLUE   = "\033[34m"
_MAGENTA= "\033[35m"

def c(text, *codes):
    return "".join(codes) + str(text) + _RESET


# ─── ASCII art ─────────────────────────────────────────────────────────────────
def display_art():
    art = r"""
                                                                ##              
   :##:    ####                          ##                     ##              
    ##     ####                  ##      ##                     ##              
   ####      ##                  ##      ##                                     
   ####      ##       .####:   #######   ##.####    .####:    ####      :####   
  :#  #:     ##      .######:  #######   #######   .######:   ####      ######  
   #::#      ##      ##:  :##    ##      ###  :##  ##:  :##     ##      #:  :## 
  ##  ##     ##      ########    ##      ##    ##  ########     ##       :##### 
  ######     ##      ########    ##      ##    ##  ########     ##     .####### 
 .######.    ##      ##          ##      ##    ##  ##           ##     ## .  ## 
 :##  ##:    ##:     ###.  :#    ##.     ##    ##  ###.  :#     ##     ##:  ### 
 ###  ###    #####   .#######    #####   ##    ##  .#######  ########  ######## 
 ##:  :##    .####    .#####:    .####   ##    ##   .#####:  ########    ###.## 
    """
    print(c(art, _CYAN, _BOLD))
    print(c("  Cipher toolkit — decode & brute-force classical ciphers\n", _DIM))


def print_section(title: str):
    width = 60
    bar = "─" * width
    print(f"\n{c(bar, _BLUE)}")
    print(f"  {c(title, _BOLD, _CYAN)}")
    print(f"{c(bar, _BLUE)}")


def print_result(label: str, value: str):
    print(f"  {c(label, _YELLOW)}  {c(value, _GREEN)}")


def print_hit(prefix: str, value):
    print(f"  {c('✔', _GREEN, _BOLD)}  {c(prefix, _YELLOW)} {c(value, _GREEN)}")


def print_info(msg: str):
    print(f"  {c('ℹ', _BLUE)}  {msg}")


def print_warn(msg: str):
    print(f"  {c('⚠', _YELLOW)}  {c(msg, _YELLOW)}", file=sys.stderr)


# ─── Byte helpers ──────────────────────────────────────────────────────────────
def to_bytes(s: str) -> bytes:
    """Convert hex / binary / list-literal / UTF-8 string to bytes."""
    s = s.strip()
    if s.startswith("[") and s.endswith("]"):
        return bytes(ast.literal_eval(s))
    if re.fullmatch(r"(?:[01]{8})+", s):
        return int(s, 2).to_bytes(len(s) // 8, "big")
    if re.fullmatch(r"(?:[0-9a-fA-F]{2})+", s):
        return binascii.unhexlify(s)
    return s.encode()


def xor_bytes(data: bytes, key: bytes) -> bytes:
    key_len = len(key)
    return bytes(b ^ key[i % key_len] for i, b in enumerate(data))


_PRINTABLE_SET = frozenset(bytes(string.printable, "ascii"))

def is_printable(bs: bytes) -> bool:
    return all(b in _PRINTABLE_SET for b in bs)


def format_xor_result(data: bytes) -> str:
    """
    Return a clean bytes-literal representation.
    Printable ASCII chars are shown as-is; others as \\xNN escapes.
    """
    parts = []
    for b in data:
        ch = chr(b)
        if ch in string.printable and ch not in "\t\n\r\x0b\x0c":
            parts.append(ch)
        else:
            parts.append(f"\\x{b:02x}")
    return "b'" + "".join(parts) + "'"


# ─── Ciphers ───────────────────────────────────────────────────────────────────
def atbash_decode(text: str) -> str:
    """Decode an Atbash-encoded string."""
    result = []
    for ch in text:
        if "A" <= ch <= "Z":
            result.append(chr(ord("Z") - (ord(ch) - ord("A"))))
        elif "a" <= ch <= "z":
            result.append(chr(ord("z") - (ord(ch) - ord("a"))))
        else:
            result.append(ch)
    return "".join(result)


def vigenere_decode(ciphertext: str, key: str) -> str:
    """Decode a Vigenère cipher given the key."""
    key = key.lower()
    key_len = len(key)
    result = []
    ki = 0
    for ch in ciphertext:
        if ch.isalpha():
            shift = ord(key[ki % key_len]) - ord("a")
            base  = ord("A") if ch.isupper() else ord("a")
            result.append(chr((ord(ch) - base - shift) % 26 + base))
            ki += 1
        else:
            result.append(ch)
    return "".join(result)


def rail_fence(ciphertext: str, key: int, offset: int = 0) -> str:
    """Decode a Rail-Fence cipher with optional offset (ghost columns)."""
    total_cols = len(ciphertext) + offset

    # Build zigzag marker matrix
    rail = [["*"] * total_cols for _ in range(key)]
    row, going_down = 0, True
    for col in range(total_cols):
        if col >= offset:
            rail[row][col] = "mkr"
        if row == 0:
            going_down = True
        elif row == key - 1:
            going_down = False
        row += 1 if going_down else -1

    # Fill ciphertext into markers
    idx = 0
    for r in range(key):
        for c in range(total_cols):
            if rail[r][c] == "mkr":
                rail[r][c] = ciphertext[idx]
                idx += 1

    # Read along zigzag
    plaintext = []
    row, going_down = 0, True
    for col in range(total_cols):
        if col >= offset and rail[row][col] != "*":
            plaintext.append(rail[row][col])
        if row == 0:
            going_down = True
        elif row == key - 1:
            going_down = False
        row += 1 if going_down else -1

    return "".join(plaintext)


def rot_n(text: str, n: int) -> str:
    """ROT-N (generalised ROT-13) over the 26-letter alphabet."""
    result = []
    for ch in text:
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            result.append(chr((ord(ch) - base + n) % 26 + base))
        else:
            result.append(ch)
    return "".join(result)


# Keep original name as alias for external callers
rot_13 = rot_n


def rot_47(text: str, n: int) -> str:
    """ROT-N over the printable ASCII range (33–126)."""
    result = []
    for ch in text:
        code = ord(ch)
        if 33 <= code <= 126:
            result.append(chr(33 + (code - 33 + n) % 94))
        else:
            result.append(ch)
    return "".join(result)


# Pre-compute valid 'a' values for affine cipher (gcd(a,26)==1)
_AFFINE_VALID_A = [a for a in range(1, 26) if math.gcd(a, 26) == 1]

def affine(text: str):
    """Brute-force all affine cipher keys and print every candidate."""
    for a in _AFFINE_VALID_A:
        for b in range(26):
            out = []
            for ch in text:
                if ch.isalpha():
                    base = ord("A") if ch.isupper() else ord("a")
                    x = ord(ch) - base
                    out.append(chr((a * (x - b)) % 26 + base))
                else:
                    out.append(ch)
            print(f"  {c(f'a={a:2}, b={b:2}', _YELLOW)} → {c(''.join(out), _GREEN)}")


def vigenere(ciphertext: str, n: int):
    """Brute-force Vigenère over all keys of the given length (max 5)."""
    if not 1 <= n <= 5:
        print_warn("Choose a key length between 1 and 5.")
        sys.exit(1)

    total = 26 ** n
    print_info(f"Testing {total:,} possible keys for length {n}…\n")

    for key_tuple in itertools.product(string.ascii_lowercase, repeat=n):
        key = "".join(key_tuple)
        result = []
        ki = 0
        for ch in ciphertext:
            if ch.isalpha():
                shift = ord(key[ki % n]) - ord("a")
                base  = ord("A") if ch.isupper() else ord("a")
                result.append(chr((ord(ch) - base - shift) % 26 + base))
                ki += 1
            else:
                result.append(ch)
        print(f"  {c(f'[key={key}]', _YELLOW)} {''.join(result)}")
