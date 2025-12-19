#!/usr/bin/ven python3

import sys
import math
import string
import itertools


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
    print(art)


def atbash_decode(string: str):
    out = []
    for ch in string:
        if "A" <= ch <= "Z":
            out.append(chr(ord("Z") - (ord(ch) - ord("A"))))
        elif "a" <= ch <= "z":
            out.append(chr(ord("z") - (ord(ch) - ord("a"))))
        else:
            out.append(ch)
    return "".join(out)


def vigenere_decode(ciphertext: str, key: str) -> str:
    plaintext = ""
    key_index = 0
    key = key.lower()

    for ch in ciphertext:
        if ch.isalpha():
            shift = ord(key[key_index % len(key)]) - ord("a")
            if ch.isupper():
                decoded = chr((ord(ch) - ord("A") - shift) % 26 + ord("A"))
            else:
                decoded = chr((ord(ch) - ord("a") - shift) % 26 + ord("a"))
            plaintext += decoded
            key_index += 1
        else:
            plaintext += ch

    return plaintext


def rail_fence(ciphertext, key, offset=0):
    L = len(ciphertext)
    total_cols = L + offset  # offset = ghost columns

    # Step 1: create empty rail matrix
    rail = [["*" for _ in range(total_cols)] for _ in range(key)]

    # Step 2: trace zigzag path (including ghost columns)
    row = 0
    col = 0
    direction_down = True

    for _ in range(total_cols):
        # mark only real columns (those >= offset)
        if col >= offset:
            rail[row][col] = "mkr"

        col += 1

        if row == 0:
            direction_down = True
        elif row == key - 1:
            direction_down = False

        row = row + 1 if direction_down else row - 1

    # Step 3: fill ciphertext into markers left→right, top→bottom
    idx = 0
    for r in range(key):
        for c in range(total_cols):
            if rail[r][c] == "mkr":
                rail[r][c] = ciphertext[idx]
                idx += 1

    # Step 4: read plaintext along zigzag
    plaintext = []
    row = 0
    col = 0
    direction_down = True

    for _ in range(total_cols):
        if col >= offset and rail[row][col] != "*":
            plaintext.append(rail[row][col])

        col += 1

        if row == 0:
            direction_down = True
        elif row == key - 1:
            direction_down = False

        row = row + 1 if direction_down else row - 1

    return "".join(plaintext)


def rot_13(text: str, n: int) -> str:
    result = ""
    for char in text:
        if char.isalpha():
            base = ord("A") if char.isupper() else ord("a")
            result += chr((ord(char) - base + n) % 26 + base)
        else:
            result += char
    return result


def rot_47(text: str, n: int) -> str:
    result = []
    for ch in text:
        code = ord(ch)
        if 33 <= code <= 126:
            result.append(chr(33 + ((code - 33 + n) % 94)))
        else:
            result.append(ch)
    return "".join(result)


def affine(text: str):
    result = ""
    modulus = 26
    valid_a = [a for a in range(1, modulus) if math.gcd(a, modulus) == 1]
    valid_n = [n for n in range(0, 26)]

    for a in valid_a:
        if a is None:
            continue
        for b in range(modulus):
            out_chars = []
            for ch in text:
                if ch.isalpha():
                    base = ord("A") if ch.isupper() else ord("a")
                    x = ord(ch) - base
                    dec = (a * (x - b)) % modulus
                    out_chars.append(chr(dec + base))
                else:
                    out_chars.append(ch)
            plaintext = "".join(out_chars)
            print(f"a = {a:2}, b = {b:2} -> {plaintext}")


def vigenere_decrypt(ciphertext, key):
    plaintext = []
    key_len = len(key)
    key_index = 0

    for c in ciphertext:
        if c.isalpha() and c.lower() >= "a" and c.lower() <= "z":
            offset = ord("a")
            c_idx = ord(c.lower()) - offset
            k_idx = ord(key[key_index % key_len]) - offset
            p = (c_idx - k_idx) % 26
            plaintext.append(chr(p + offset))
            key_index += 1
        else:
            plaintext.append(c)

    return "".join(plaintext)


def vigenere(ciphertext, n):
    if n < 1 or n > 5:
        print(
            "Choose a key len between 1 and 5. key len = 6 gives 11 881 376 possible keys! think about your processor"
        )
        sys.exit(0)

    alphabet = string.ascii_lowercase
    total_keys = 26**n
    print(f"[+] Test of {total_keys} possible keys...")

    for key_tuple in itertools.product(alphabet, repeat=n):
        key = "".join(key_tuple)
        result = []
        key_index = 0

        for char in ciphertext:
            if char.isalpha():
                shift = ord(key[key_index % len(key)]) - ord("a")

                if char.isupper():
                    base = ord("A")
                else:
                    base = ord("a")

                decrypted_char = chr((ord(char) - base - shift) % 26 + base)
                result.append(decrypted_char)
                key_index += 1
            else:
                result.append(char)

        print(f"[possible_key={key}] {''.join(result)}")


def rail_fence(ciphertext, key, offset=0):
    L = len(ciphertext)
    total_cols = L + offset  # offset = ghost columns

    # Step 1: create empty rail matrix
    rail = [["*" for _ in range(total_cols)] for _ in range(key)]

    # Step 2: trace zigzag path (including ghost columns)
    row = 0
    col = 0
    direction_down = True

    for _ in range(total_cols):
        # mark only real columns (those >= offset)
        if col >= offset:
            rail[row][col] = "mkr"

        col += 1

        if row == 0:
            direction_down = True
        elif row == key - 1:
            direction_down = False

        row = row + 1 if direction_down else row - 1

    # Step 3: fill ciphertext into markers left→right, top→bottom
    idx = 0
    for r in range(key):
        for c in range(total_cols):
            if rail[r][c] == "mkr":
                rail[r][c] = ciphertext[idx]
                idx += 1

    # Step 4: read plaintext along zigzag
    plaintext = []
    row = 0
    col = 0
    direction_down = True

    for _ in range(total_cols):
        if col >= offset and rail[row][col] != "*":
            plaintext.append(rail[row][col])

        col += 1

        if row == 0:
            direction_down = True
        elif row == key - 1:
            direction_down = False

        row = row + 1 if direction_down else row - 1

    return "".join(plaintext)
