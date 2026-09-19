"""第 8 章 · 从私钥一路算到地址

对应书中第 8.1—8.4 节。完整链路：
    私钥 -> 公钥(×G) -> hash160 -> +版本字节和校验和 -> Base58Check / Bech32
运行：python3 ch08_address.py
"""
from btclib import pmul, ser_p, hash160, b58check, bech32_encode, convertbits

BTC = 100_000_000

print("=" * 66)
print("从私钥 1234567890 出发，一路算到地址")
print("=" * 66)

priv = 1234567890
print(f"  1. 私钥           : {priv}  (32 字节随机数)")
print(f"                     {priv:064x}")

x, y = pmul(priv)
print(f"  2. 公钥 (未压缩)  : 04{x:064x}")
print(f"                     {y:064x}")
print(f"                     = 65 字节")

comp = ser_p((x, y))
print(f"  3. 压缩公钥       : {comp.hex()}")
print(f"                     = 33 字节（0x02 表示 y 为偶数，0x03 表示 y 为奇数）")

h = hash160(comp)
print(f"  4. hash160        : {h.hex()}")
print(f"                     = SHA256 再 RIPEMD160，20 字节")

print()
print("-" * 66)
print("  5. 编码成地址")
print("-" * 66)

p2pkh = b58check(b"\x00" + h)
print(f"     P2PKH   (1...)  : {p2pkh}")
print(f"                       版本字节 0x00 + hash160 + 4 字节校验和 -> Base58")

w = convertbits(h, 8, 5)
p2wpkh = bech32_encode("bc", [0] + w)
print(f"     P2WPKH  (bc1q..): {p2wpkh}")
print(f"                       HRP 'bc' + witness v0 + hash160 -> Bech32")

print()
print("=" * 66)
print("为什么压缩公钥只用 33 字节？")
print("=" * 66)
print("  曲线方程 y^2 = x^3 + 7，给定 x，y 只有两个可能值：y 和 P-y。")
print("  所以只需要 1 个比特记录 y 的奇偶性，就能完整还原这个点。")
print(f"  65 字节 -> 33 字节，省了近一半。")
print()
print("  验证一下：从压缩公钥还原 y，应该能对上")
print(f"    还原出的 y   = {y:064x}")
print(f"    另一个可能值 = {(y * -1) % (2**256 - 2**32 - 977):064x}")

print()
print("=" * 66)
print("不同网络前缀 = 完全不同地址")
print("=" * 66)
for hrp in ["bc", "tb", "bcrt"]:
    print(f"  {hrp:>5}: {bech32_encode(hrp, [0] + w)}")
print()
print("  >>> 把测试网地址当主网用，币就丢了。")

print()
print("=" * 66)
print("关于地址的两个常见误解")
print("=" * 66)
print("  × '地址就是账号'      -> 地址只是锁定脚本的编码，可以无限生成")
print("  × '看到地址能推私钥'  -> 地址连公钥都推不出来，更别说私钥")
print("  √ 每次收款用新地址，是保护隐私的基本功（见第 14 章）")
