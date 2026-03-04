#!/usr/bin/env python3

import argparse
import itertools
import string
import sys

import brute_force

# ─── Custom formatter for prettier help ───────────────────────────────────────
class _Fmt(argparse.HelpFormatter):
    """Coloured, slightly wider help formatter."""
    _W = 80

    def __init__(self, prog):
        super().__init__(prog, max_help_position=36, width=self._W)

    def _format_action_invocation(self, action):
        base = super()._format_action_invocation(action)
        return brute_force.c(base, brute_force._CYAN)

    def _format_usage(self, usage, actions, groups, prefix):
        if prefix is None:
            prefix = brute_force.c("Usage: ", brute_force._BOLD, brute_force._YELLOW)
        return super()._format_usage(usage, actions, groups, prefix)

    def start_section(self, heading):
        heading = brute_force.c(heading, brute_force._BOLD, brute_force._BLUE) if heading else heading
        super().start_section(heading)


# ─── Parsers ──────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(
    prog="aletheia",
    description=brute_force.c(
        "Decode or brute-force classical ciphers.\n"
        "  Supported: XOR · Atbash · Vigenère · Rail-Fence · ROT-13 · ROT-47 · Affine",
        brute_force._DIM,
    ),
    formatter_class=_Fmt,
    epilog=brute_force.c(
        "Tip: pipe brute-force output through grep to filter results.\n"
        "Example: aletheia xor_brute -s deadbeef -l 2 | grep 'flag'",
        brute_force._DIM,
    ),
)

subparsers = parser.add_subparsers(
    dest="cipher",
    required=True,
    title=brute_force.c("modes", brute_force._BOLD, brute_force._BLUE),
    metavar="<mode>",
)

# ── xor ────────────────────────────────────────────────────────────────────────
xor_p = subparsers.add_parser(
    "xor",
    help="decode an XOR-encrypted string with a known key",
    description="XOR-decrypt a ciphertext given the key. Both string and key accept hex, binary, UTF-8, or a list of bytes (e.g. [32,0,86]).",
    formatter_class=_Fmt,
)
xor_p.add_argument("-s", "--string", metavar="CIPHERTEXT", required=True,
                   help="ciphertext — hex / binary / UTF-8 / [bytes]")
xor_p.add_argument("-k", "--key",    metavar="KEY",        required=True,
                   help="XOR key — hex / binary / UTF-8")

# ── atbash ─────────────────────────────────────────────────────────────────────
atbash_p = subparsers.add_parser(
    "atbash",
    help="decode an Atbash cipher (A↔Z mirror substitution)",
    formatter_class=_Fmt,
)
atbash_p.add_argument("-s", "--string", metavar="CIPHERTEXT", required=True,
                      help="string to decode")

# ── vigenere ───────────────────────────────────────────────────────────────────
vig_p = subparsers.add_parser(
    "vigenere",
    help="decode a Vigenère cipher with a known key",
    formatter_class=_Fmt,
)
vig_p.add_argument("-s", "--string", metavar="CIPHERTEXT", required=True,
                   help="string to decode")
vig_p.add_argument("-k", "--key",    metavar="KEY",        required=True,
                   help="Vigenère key (letters only)")

# ── rail_fence ─────────────────────────────────────────────────────────────────
rf_p = subparsers.add_parser(
    "rail_fence",
    help="decode a Rail-Fence cipher with a known key",
    formatter_class=_Fmt,
)
rf_p.add_argument("-s", "--string", metavar="CIPHERTEXT", required=True,
                  help="string to decode")
rf_p.add_argument("-k", "--key",    metavar="RAILS", type=int, required=True,
                  help="number of rails (2 ≤ rails ≤ len(string))")
rf_p.add_argument("-o", "--offset", metavar="OFFSET", type=int, default=0,
                  help="ghost-column offset (default: 0)")

# ── xor_brute ──────────────────────────────────────────────────────────────────
xor_bf_p = subparsers.add_parser(
    "xor_brute",
    help="brute-force XOR keys up to length 4",
    description=(
        "Test every printable-ASCII key of the given length.\n"
        "Without --filter: all results are printed as raw bytes.\n"
        "With    --filter: only lines whose output contains the given string are shown."
    ),
    formatter_class=_Fmt,
    epilog="Example: aletheia xor_brute -s deadbeef -l 2 --filter flag",
)
xor_bf_p.add_argument("-s", "--string", metavar="CIPHERTEXT", required=True,
                      help="ciphertext — hex / binary / UTF-8")
xor_bf_p.add_argument("-l", "--length", metavar="LEN", type=int, required=True,
                      help="key length to test (max 4)")
xor_bf_p.add_argument("-f", "--filter", metavar="STRING", default=None,
                      help="only show results whose decoded output contains STRING")

# ── rot13_brute ────────────────────────────────────────────────────────────────
rot13_p = subparsers.add_parser(
    "rot13_brute",
    help="try all 26 ROT-N shifts (ROT-1 … ROT-25)",
    formatter_class=_Fmt,
)
rot13_p.add_argument("-s", "--string", metavar="CIPHERTEXT", required=True,
                     help="string to brute-force")

# ── rot47_brute ────────────────────────────────────────────────────────────────
rot47_p = subparsers.add_parser(
    "rot47_brute",
    help="try all 94 ROT-47 shifts over printable ASCII",
    formatter_class=_Fmt,
)
rot47_p.add_argument("-s", "--string", metavar="CIPHERTEXT", required=True,
                     help="string to brute-force")

# ── affine_brute ───────────────────────────────────────────────────────────────
affine_p = subparsers.add_parser(
    "affine_brute",
    help="brute-force all valid affine cipher keys",
    description="Tests all (a, b) pairs where gcd(a, 26) = 1 — 312 combinations total.",
    formatter_class=_Fmt,
)
affine_p.add_argument("-s", "--string", metavar="CIPHERTEXT", required=True,
                      help="string to brute-force")

# ── vigenere_brute ─────────────────────────────────────────────────────────────
vig_bf_p = subparsers.add_parser(
    "vigenere_brute",
    help="brute-force Vigenère keys of a given length (max 5)",
    description="Exhaustively tries all lowercase-letter keys of the given length.\nKey length 5 → 11 881 376 keys; redirect stdout and grep for results.",
    formatter_class=_Fmt,
)
vig_bf_p.add_argument("-s", "--string", metavar="CIPHERTEXT", required=True,
                      help="string to brute-force")
vig_bf_p.add_argument("-l", "--len",    metavar="LEN", type=int, required=True,
                      help="key length to test (max 5)")

# ── xor_kpa ────────────────────────────────────────────────────────────────────
kpa_p = subparsers.add_parser(
    "xor_kpa",
    help="XOR known-plaintext attack — recover key from a plaintext fragment",
    description=(
        "Known-Plaintext Attack against XOR.\n"
        "For each (key_len, offset):\n"
        "  key  = ciphertext[offset:offset+key_len] XOR known_plain[:key_len]\n"
        "  test = ciphertext XOR key  →  shown if output meets printability threshold."
    ),
    formatter_class=_Fmt,
    epilog=(
        "Examples:\n"
        "  aletheia xor_kpa -s <hex> -p 'CTF{'\n"
        "  aletheia xor_kpa -s <hex> -p 'flag{' --key-len 8\n"
        "  aletheia xor_kpa -s <hex> -p 'MZ'   --min 4 --max 32\n"
        "  aletheia xor_kpa -s <hex> -p 'flag' --threshold 0.9 --limit 5"
    ),
)
kpa_p.add_argument("-s", "--string",    metavar="CIPHERTEXT", required=True,
                   help="ciphertext — hex / binary / UTF-8")
kpa_p.add_argument("-p", "--plaintext", metavar="KNOWN_PT",   required=True,
                   help="known plaintext fragment — hex / UTF-8")
kpa_grp = kpa_p.add_mutually_exclusive_group()
kpa_grp.add_argument("--key-len",   metavar="N",   type=int,
                     help="fixed key length to test")
kpa_grp.add_argument("--min",       metavar="N",   type=int,
                     help="minimum key length (default: 1)")
kpa_p.add_argument("--max",         metavar="N",   type=int,
                   help="maximum key length (default: len(known_plain))")
kpa_p.add_argument("--threshold",   metavar="0-1", type=float, default=1.0,
                   help="printable-ASCII ratio required (default: 1.0 = strict)")
kpa_p.add_argument("--limit",       metavar="N",   type=int,   default=0,
                   help="stop after N hits (0 = unlimited)")


rf_bf_p = subparsers.add_parser(
    "rail_fence_brute",
    help="brute-force Rail-Fence key and offset",
    description="Tests every (rails, offset) combination. Filter output with grep.",
    formatter_class=_Fmt,
)
rf_bf_p.add_argument("-s", "--string", metavar="CIPHERTEXT", required=True,
                     help="string to brute-force")


# ─── Show help when called with no args or just a sub-command name ─────────────
if len(sys.argv) == 1:
    brute_force.display_art()
    parser.print_help()
    sys.exit(0)

if len(sys.argv) == 2 and sys.argv[1] in subparsers.choices:
    brute_force.display_art()
    subparsers.choices[sys.argv[1]].print_help()
    sys.exit(0)

args = parser.parse_args()


# ─── Dispatch ─────────────────────────────────────────────────────────────────

if args.cipher == "atbash":
    brute_force.print_section("Atbash  —  decode")
    res = brute_force.atbash_decode(args.string)
    brute_force.print_result("Plaintext →", res)
    print()

elif args.cipher == "vigenere":
    brute_force.print_section(f"Vigenère  —  decode  (key: {args.key})")
    res = brute_force.vigenere_decode(args.string, args.key)
    brute_force.print_result("Plaintext →", res)
    print()

elif args.cipher == "rail_fence":
    brute_force.print_section(f"Rail-Fence  —  decode  (rails={args.key}, offset={args.offset})")
    res = brute_force.rail_fence(args.string, args.key, args.offset)
    brute_force.print_result("Plaintext →", res)
    print()

elif args.cipher == "xor":
    brute_force.print_section("XOR  —  decode")
    cipher_bytes = brute_force.to_bytes(args.string)
    key_bytes    = brute_force.to_bytes(args.key)
    result       = brute_force.xor_bytes(cipher_bytes, key_bytes)
    brute_force.print_result("Raw bytes  →", brute_force.format_xor_result(result))
    try:
        decoded = result.decode("utf-8")
        brute_force.print_result("UTF-8 text →", decoded)
    except UnicodeDecodeError:
        pass
    print()

elif args.cipher == "xor_brute":
    if args.length > 4:
        brute_force.print_warn("Maximum key length is 4.")
        sys.exit(1)

    cipher_bytes = brute_force.to_bytes(args.string)
    charset      = bytes(range(256))
    total        = 256 ** args.length
    needle       = args.filter  # None or a string to match

    filter_desc = f"  filter: {brute_force.c(needle, brute_force._MAGENTA)}" if needle else "  no filter — showing all results"
    brute_force.print_section(f"XOR  —  brute-force  (key length: {args.length})")
    brute_force.print_info(f"Total keys to test: {total:,}")
    brute_force.print_info(filter_desc + "\n")

    val_label = brute_force.c("Raw bytes  →", brute_force._CYAN)
    for key_tuple in itertools.product(charset, repeat=args.length):
        key_bytes   = bytes(key_tuple)
        xored       = brute_force.xor_bytes(cipher_bytes, key_bytes)
        display_val = brute_force.format_xor_result(xored)

        if needle and needle not in display_val:
            continue

        key_label = brute_force.c(f"key=0x{key_bytes.hex()}", brute_force._YELLOW)
        print(f"  {key_label}  {val_label}  {brute_force.c(display_val, brute_force._GREEN)}")

    print()

elif args.cipher == "rot13_brute":
    brute_force.print_section("ROT-N  —  brute-force  (all 26 shifts)")
    for i in range(26):
        res = brute_force.rot_n(args.string, i)
        shift_label = brute_force.c(f"ROT-{i:>2}", brute_force._YELLOW)
        print(f"  {shift_label}  {brute_force.c(res, brute_force._GREEN)}")
    print()

elif args.cipher == "rot47_brute":
    brute_force.print_section("ROT-47  —  brute-force  (all 94 shifts)")
    for i in range(94):
        res = brute_force.rot_47(args.string, i)
        shift_label = brute_force.c(f"ROT-{i:>2}", brute_force._YELLOW)
        print(f"  {shift_label}  {brute_force.c(res, brute_force._GREEN)}")
    print()

elif args.cipher == "affine_brute":
    brute_force.print_section("Affine  —  brute-force  (312 key pairs)")
    brute_force.affine(args.string)
    print()

elif args.cipher == "vigenere_brute":
    brute_force.print_section(f"Vigenère  —  brute-force  (key length: {args.len})")
    brute_force.vigenere(args.string, args.len)
    print()

elif args.cipher == "rail_fence_brute":
    brute_force.print_section("Rail-Fence  —  brute-force  (all rails × offsets)")
    text = args.string
    for key in range(2, len(text)):
        period = 2 * (key - 1)
        header = brute_force.c(f"  ── rails={key:03}  period={period:03} ──", brute_force._BLUE)
        print(header)
        for offset in range(period):
            res = brute_force.rail_fence(text, key, offset)
            print(
                f"    {brute_force.c(f'offset={offset:03}', brute_force._YELLOW)}"
                f"  {brute_force.c(res, brute_force._GREEN)}"
            )
        print()
elif args.cipher == "xor_kpa":
    cipher_bytes = brute_force.to_bytes(args.string)
    known_bytes  = brute_force.to_bytes(args.plaintext)

    if args.key_len:
        kl_min = kl_max = args.key_len
    else:
        kl_min = args.min if args.min else 1
        kl_max = args.max if args.max else len(known_bytes)

    if kl_min > kl_max:
        brute_force.print_warn("--min must be ≤ --max")
        sys.exit(1)

    limit_str = "unlimited" if not args.limit else str(args.limit)
    brute_force.print_section("XOR  —  Known-Plaintext Attack")
    brute_force.print_info(f"ciphertext  : {len(cipher_bytes)} bytes  ({cipher_bytes[:16].hex(' ')}{'…' if len(cipher_bytes) > 16 else ''})")
    brute_force.print_info(f"known plain : {known_bytes!r}  ({len(known_bytes)} bytes)")
    brute_force.print_info(f"key length  : {kl_min}..{kl_max}")
    brute_force.print_info(f"threshold   : {args.threshold:.0%}")
    brute_force.print_info(f"limit       : {limit_str}\n")

    hits = 0
    for hit in brute_force.xor_kpa(cipher_bytes, known_bytes, kl_min, kl_max, args.threshold):
        hits += 1
        brute_force.print_kpa_hit(hit, hits)
        if args.limit and hits >= args.limit:
            print()
            brute_force.print_warn(f"Limit of {args.limit} hit(s) reached.")
            break

    print()
    if hits == 0:
        brute_force.print_warn("No results — try --threshold 0.9 or widen --min/--max.")
    else:
        brute_force.print_info(brute_force.c(f"{hits} result(s) found.", brute_force._BOLD))
    print()
