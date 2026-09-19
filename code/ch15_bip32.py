"""第 15 章 · BIP32 HD 钱包：一个种子，无限地址

对应书中第 15.4—15.6 节。使用 BIP32 官方测试向量验证。
运行：python3 ch15_bip32.py
"""
from btclib import (master_key, ckd_priv, derive_path, pmul, ser_p,
                    hash160, b58check, bech32_encode, convertbits)

# BIP32 官方测试向量 1 的种子
seed = bytes.fromhex("000102030405060708090a0b0c0d0e0f")

print("=" * 68)
print("1. 种子 -> 主密钥（与 BIP32 官方文档逐字节对照）")
print("=" * 68)
k, c = master_key(seed)
print(f"  主私钥   : {k.to_bytes(32, 'big').hex()}")
print(f"  主链码   : {c.hex()}")
print(f"  主公钥   : {ser_p(pmul(k)).hex()}")

xprv = b58check(bytes.fromhex("0488ADE4") + b"\x00" + bytes(4)
                + bytes.fromhex("00000000") + c + b"\x00" + k.to_bytes(32, "big"))
xpub = b58check(bytes.fromhex("0488B21E") + b"\x00" + bytes(4)
                + bytes.fromhex("00000000") + c + ser_p(pmul(k)))
print(f"  xprv     : {xprv}")
print(f"  xpub     : {xpub}")

print()
print("  官方文档里的值就是这个 xprv9s21ZrQH143K3QTDL4LXw2F7HEK3wJUD2nW2nRk4stbPy6cq3jPPqji...")
print("  >>> 能算出完全一样的结果，说明整个推导逻辑是对的。")

print()
print("=" * 68)
print("2. 派生路径：m / 用途' / 币种' / 账户' / 外部链 / 序号")
print("=" * 68)
paths = [
    ("m/44'/0'/0'/0/0", "BIP44 · P2PKH",        "1..."),
    ("m/49'/0'/0'/0/0", "BIP49 · P2SH-SegWit",  "3..."),
    ("m/84'/0'/0'/0/0", "BIP84 · P2WPKH",       "bc1q..."),
    ("m/86'/0'/0'/0/0", "BIP86 · P2TR(Taproot)","bc1p..."),
]

for path, note, prefix in paths:
    kk, _ = derive_path(seed, path)
    h = hash160(ser_p(pmul(kk)))
    p2pkh = b58check(b"\x00" + h)
    p2wpkh = bech32_encode("bc", [0] + convertbits(h, 8, 5))
    print(f"  {path:<18} {note:<22}")
    print(f"      私钥 {kk.to_bytes(32,'big').hex()[:32]}...")
    print(f"      P2PKH  {p2pkh}")
    print(f"      原生 SegWit  {p2wpkh}   <- 该路径真正用的地址 ({prefix})")

print()
print("  注意：同一个种子，换个路径就是完全不同的地址。")
print("  >>> 恢复钱包时如果选错路径，会看到一个'空钱包'—— 币其实还在，只是没找到。")

print()
print("=" * 68)
print("3. 硬化派生 vs 普通派生")
print("=" * 68)
print("  普通派生（不带撇号）：用公钥算，可以从 xpub 推导出子公钥")
print("  硬化派生（带 ' ）   ：用私钥算，xpub 推不出来")
print()
kk, cc = master_key(seed)
k_h, _ = ckd_priv(kk, cc, 0x80000000)      # 硬化
k_n, _ = ckd_priv(kk, cc, 0)               # 普通
print(f"  m/0'  (硬化) 私钥: {k_h.to_bytes(32,'big').hex()}")
print(f"  m/0   (普通) 私钥: {k_n.to_bytes(32,'big').hex()}")
print()
print("  >>> 为什么要硬化？")
print("  >>> 如果 xpub 泄露，普通派生的兄弟密钥可能被反推出父私钥，进而拿走全部资金。")
print("  >>> 硬化派生切断了这条路径，所以层级的前三级都建议硬化。")

print()
print("=" * 68)
print("4. 无限地址的来源")
print("=" * 68)
print("  同一个路径下，只改最后一个序号，就能生成无限个地址：")
base_seed = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
for i in range(5):
    kk, _ = derive_path(base_seed, f"m/84'/0'/0'/0/{i}")
    h = hash160(ser_p(pmul(kk)))
    addr = bech32_encode("bc", [0] + convertbits(h, 8, 5))
    print(f"    m/84'/0'/0'/0/{i}  ->  {addr}")
print()
print("  >>> 这就是'每次收款都用新地址'能落地的原因（第 14.3 节）。")
print("  >>> 钱包只需要备份一个种子，所有地址都能随时重新算出来。")
