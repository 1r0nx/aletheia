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


def xor_repeat(data: bytes, key: bytes) -> bytes:
    """XOR data with key repeated cyclically."""
    key_len = len(key)
    return bytes(data[i] ^ key[i % key_len] for i in range(len(data)))


def is_fully_printable(data: bytes, threshold: float = 1.0) -> bool:
    """Return True if the ratio of printable ASCII bytes meets the threshold."""
    printable = sum(0x20 <= b <= 0x7E or b in (0x09, 0x0A, 0x0D) for b in data)
    return (printable / len(data)) >= threshold if data else False


def xor_kpa(
    ciphertext:  bytes,
    known_plain: bytes,
    key_len_min: int,
    key_len_max: int,
    threshold:   float = 1.0,
):
    """
    XOR Known-Plaintext Attack.

    For each (key_len, offset):
      key_candidate = ciphertext[offset:offset+key_len] XOR known_plain[:key_len]
      plaintext     = ciphertext XOR key_candidate (repeated)
    Yields dicts for every hit that meets the printability threshold.
    """
    ct_len = len(ciphertext)
    kp_len = len(known_plain)

    for key_len in range(key_len_min, key_len_max + 1):
        # Extend known_plain if shorter than key_len
        if kp_len >= key_len:
            kp_chunk = known_plain[:key_len]
        else:
            kp_chunk = (known_plain * (key_len // kp_len + 1))[:key_len]

        max_offset = ct_len - key_len
        if max_offset < 0:
            continue

        for offset in range(max_offset + 1):
            ct_chunk      = ciphertext[offset: offset + key_len]
            key_candidate = xor_bytes(ct_chunk, kp_chunk)

            if not key_candidate:
                continue

            plaintext = xor_repeat(ciphertext, key_candidate)

            if is_fully_printable(plaintext, threshold):
                yield {
                    "key_len":   key_len,
                    "offset":    offset,
                    "key":       key_candidate,
                    "plaintext": plaintext,
                }


def print_kpa_hit(hit: dict, index: int):
    """Display a single xor_kpa hit with ANSI colours."""
    key     = hit["key"]
    pt      = hit["plaintext"]
    offset  = hit["offset"]
    key_len = hit["key_len"]

    key_hex = key.hex(" ")
    key_asc = "".join(chr(b) if 0x20 <= b <= 0x7E else "·" for b in key)
    pt_str  = format_xor_result(pt)

    width = 60
    bar   = c("─" * width, _GREEN)
    print(f"\n  {bar}")
    print(f"  {c(f'hit #{index}', _BOLD, _GREEN)}")
    print(f"  {c('─' * width, _GREEN)}")
    print(f"  {c('key len  :', _DIM)}  {c(str(key_len), _BOLD)}")
    print(f"  {c('offset   :', _DIM)}  {c(f'{offset:#06x}  ({offset})', _BOLD)}")
    print(f"  {c('key hex  :', _DIM)}  {c(key_hex, _CYAN)}")
    print(f"  {c('key asc  :', _DIM)}  {c(key_asc, _MAGENTA)}")
    print(f"  {c('Raw bytes:', _DIM)}  {c(pt_str, _GREEN)}")
    print(f"  {bar}")


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
