import hashlib
import logging
import os
import sys
import base58
import ecdsa

logger = logging.getLogger("null")
logger.addHandler(logging.NullHandler())

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

processed_file = os.path.join(DATA_DIR, 'processed.txt')
found_file = os.path.join(DATA_DIR, 'found_file.txt')
high_val_addresses = os.path.join(DATA_DIR, 'high_val_addresses.txt')

BECH32_CONST = 1
BECH32M_CONST = 0x2bc830a3
CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def generate_legacy_address(ripemd160_hash, network_byte):
    ripemd160_with_network = network_byte + ripemd160_hash
    checksum = hashlib.sha256(hashlib.sha256(ripemd160_with_network).digest()).digest()[:4]
    return base58.b58encode(ripemd160_with_network + checksum).decode()

def generate_p2sh_address(redeem_script, network_byte):
    p2sh_with_network = network_byte + redeem_script
    checksum_p2sh = hashlib.sha256(hashlib.sha256(p2sh_with_network).digest()).digest()[:4]
    return base58.b58encode(p2sh_with_network + checksum_p2sh).decode()

def bech32_polymod(values):
    GEN = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
    chk = 1
    for v in values:
        b = chk >> 25
        chk = (chk & 0x1ffffff) << 5 ^ v
        for i in range(5):
            chk ^= GEN[i] if ((b >> i) & 1) else 0
    return chk

def bech32_hrp_expand(hrp):
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]

def bech32_create_checksum(hrp, data, spec):
    values = bech32_hrp_expand(hrp) + data
    polymod = bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ spec
    return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]

def bech32_encode(hrp, data, spec=BECH32_CONST):
    combined = data + bech32_create_checksum(hrp, data, spec)
    return hrp + '1' + ''.join([CHARSET[d] for d in combined])

def convertbits(data, frombits, tobits, pad=True):
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    max_acc = (1 << (frombits + tobits - 1)) - 1
    for value in data:
        if value < 0 or value >> frombits:
            return None
        acc = ((acc << frombits) | value) & max_acc
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad:
        if bits:
            ret.append((acc << (tobits - bits)) & maxv)
    elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
        return None
    return ret

def bech32_encode_custom(hrp, version, program, bech32m=False):
    converted_program = convertbits(program, 8, 5)
    if converted_program is None:
        raise ValueError("Invalid witness program for Bech32 encoding")
    if bech32m:
        return bech32_encode(hrp, [version] + converted_program, BECH32M_CONST)
    return bech32_encode(hrp, [version] + converted_program, BECH32_CONST)

def encode_wif(private_key_hex, compressed=False):
    extended_key = b'\x80' + bytes.fromhex(private_key_hex)
    if compressed:
        extended_key += b'\x01'
    checksum = hashlib.sha256(hashlib.sha256(extended_key).digest()).digest()[:4]
    extended_key += checksum
    return base58.b58encode(extended_key).decode()

def generate_keys_from_seed(seed):
    private_key = hashlib.sha256(seed.encode()).hexdigest()
    sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1)
    vk = sk.verifying_key
    # Uncompressed public key
    public_key_uncompressed = b'\x04' + vk.to_string()
    # Compressed public key
    public_key_compressed = b'\x02' + vk.to_string()[:32] if vk.pubkey.point.y() % 2 == 0 else b'\x03' + vk.to_string()[:32]
    # WIF encodings for both compressed and uncompressed private keys
    wif_uncompressed = encode_wif(private_key, compressed=False)
    wif_compressed = encode_wif(private_key, compressed=True)
    ### Cache SHA256 and RIPEMD160 hashes for reuse ###
    sha256_uncompressed = hashlib.sha256(public_key_uncompressed).digest()
    sha256_compressed = hashlib.sha256(public_key_compressed).digest()
    ripemd160_uncompressed = hashlib.new('ripemd160', sha256_uncompressed).digest()
    ripemd160_compressed = hashlib.new('ripemd160', sha256_compressed).digest()
    ### 1. Legacy (P2PKH) Address Generation - Uncompressed
    legacy_address_uncompressed = generate_legacy_address(ripemd160_uncompressed, network_byte=b'\x00')
    ### 2. Legacy (P2PKH) Address Generation - Compressed
    legacy_address_compressed = generate_legacy_address(ripemd160_compressed, network_byte=b'\x00')
    ### 3. SegWit v0 (P2WPKH) Bech32 Address Generation
    witness_program_v0 = ripemd160_compressed
    P2WPKH_address = bech32_encode_custom("bc", 0, witness_program_v0, bech32m=False)
    ### 4. SegWit v0 (P2WSH) Address Generation ###
    witness_script_v0 = sha256_compressed
    P2WSH_address = bech32_encode_custom("bc", 0, witness_script_v0, bech32m=False)
    ### 5. SegWit v1 (Taproot P2TR) Bech32m Address Generation ###
    taproot_witness_program = hashlib.sha256(vk.to_string()).digest()
    taproot_address = bech32_encode_custom("bc", 1, taproot_witness_program, bech32m=True)
    ### 6. P2SH Address Generation (Pay-to-Script-Hash) ###
    redeem_script = ripemd160_uncompressed
    p2sh_address = generate_p2sh_address(redeem_script, network_byte=b'\x05')
    return private_key, wif_uncompressed, wif_compressed, public_key_uncompressed.hex(), public_key_compressed.hex(), legacy_address_uncompressed, legacy_address_compressed, P2WPKH_address, P2WSH_address, taproot_address, p2sh_address

def load_addresses(filepath):
    global logger
    logger.info(f"Loading addresses from: {filepath}")
    addresses = set()
    with open(filepath, 'r') as f:
        for line in f:
            clean_line = line.strip()
            if clean_line:
                addresses.add(clean_line)
    return addresses

def load_main_data(filepath):
    global logger
    logger.info(f"load_main_data: {filepath}")
    main_seeds = set()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    seed = line.strip()
                    main_seeds.add(seed)
    except FileNotFoundError:
        logger.error(f"File {filepath} not found.")
    except UnicodeDecodeError as e:
        logger.error(f"Error decoding file: {e}")
    return main_seeds

def check_addresses(address_set, addresses_to_check):
    return any(address in address_set for address in addresses_to_check)

def run_keygen(process_amount=500000000,log=None):
    global logger
    logger = log
    logger.info(f"Starting BTC keygen task for {process_amount} seeds")
    main_seeds = load_main_data(processed_file)
    addresses = load_addresses(high_val_addresses)
    logger.info("Addresses have been loaded...")
    with open(processed_file, 'r', encoding='utf-8') as tmpfile:
        line_count = sum(1 for _ in tmpfile)
    processed_count = 0
    logger.info(f"Now checking balances for ({line_count}) items...")
    for seed in main_seeds:
        if processed_count >= process_amount:
            break
        if seed:
            private_key, wif_uncompressed, wif_compressed, public_key_uncompressed, public_key_compressed, legacy_address_uncompressed, legacy_address_compressed, P2WPKH_address, P2WSH_address, taproot_address, p2sh_address = generate_keys_from_seed(seed)
            addresses_to_check = [legacy_address_uncompressed, legacy_address_compressed, P2WPKH_address, P2WSH_address, taproot_address, p2sh_address]
            found_status = check_addresses(addresses, addresses_to_check)
            processed_count += 1
            if found_status:
                found_line = f"Seed: {seed}, Public Key (Uncompressed): {public_key_uncompressed}, Public Key (Compressed): {public_key_compressed}, Private Key (Hex): {private_key}, " \
                             f"WIF (Uncompressed): {wif_uncompressed}, WIF (Compressed): {wif_compressed}, " \
                             f"Legacy Address (Uncompressed): {legacy_address_uncompressed}, Legacy Address (Compressed): {legacy_address_compressed}, " \
                             f"P2WPKH Address: {P2WPKH_address}, P2WSH Address: {P2WSH_address}, TapRoot Address: {taproot_address}, P2SH Address: {p2sh_address}\n"
                logger.info("\n\n!!~~FOUND_BALANCE~~!!\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n" + found_line + "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")
                with open(found_file, 'a', encoding='utf-8') as found_file:
                    found_file.write(found_line)
            if processed_count % 100 == 0:
                sys.stdout.write(f"\rProcessed count: {processed_count}")
                sys.stdout.flush()
    logger.info("\nProcessing complete.")
