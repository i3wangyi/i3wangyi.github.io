"""第 3 章 · ECDSA 签名，以及随机数为什么不能复用

对应书中第 3.4—3.5 节。
运行：python3 ch03_ecdsa.py
"""
from btclib import P, N, inv, padd, pmul, sign, verify, sha256

print("=" * 66)
print("1. 密钥对：私钥是随机数，公钥 = 私钥 × G")
print("=" * 66)
d = 1234567890
Q = pmul(d)
print(f"  私钥 d = {d}")
print(f"  公钥 Q = ({Q[0]:064x}")
print(f"           {Q[1]:064x})")
print()
print("  正向：私钥 → 公钥，用 pmul() 几毫秒")
print("  反向：公钥 → 私钥，用尽全世界算力也算不出（离散对数问题）")

print()
print("=" * 66)
print("2. 签名与验签")
print("=" * 66)
msg = b"I send 0.5 BTC to Bob"
z = int.from_bytes(sha256(msg), "big")
sig = sign(z, d)
print(f"  消息      : {msg.decode()}")
print(f"  z = sha256 : {z:064x}")
print(f"  签名 r     : {sig[0]:064x}")
print(f"  签名 s     : {sig[1]:064x}")
print()
print(f"  原消息验签      : {verify(z, sig, Q)}")

tampered_msg = b"I send 5 BTC to Bob"
z_bad = int.from_bytes(sha256(tampered_msg), "big")
print(f"  篡改后验签      : {verify(z_bad, sig, Q)}  <- 金额改了，签名立刻失效")

print()
print("=" * 66)
print("3. 经典事故：复用随机数 k 会直接泄露私钥")
print("=" * 66)
print("  2010 年索尼 PS3 的固件签名就是这么被破解的。")
print()

# 故意复用同一个 k 签两条不同消息
k = 0xCAFEBABE1234567890ABCDEF0123456789ABCDEF0123456789ABCDEF0123
z1 = int.from_bytes(sha256(b"message one"), "big")
z2 = int.from_bytes(sha256(b"message two"), "big")

r = pmul(k)[0] % N
s1 = (inv(k, N) * (z1 + r * d)) % N
s2 = (inv(k, N) * (z2 + r * d)) % N

print(f"  同一个 k 签了两笔，所以 r 相同: {r == pmul(k)[0] % N}")
print(f"  s1 = {s1:064x}")
print(f"  s2 = {s2:064x}")

# 攻击者已知 z1, z2, s1, s2, r，可以解出 k 和 d
# s1 - s2 = k^-1 (z1 - z2)   =>   k = (z1 - z2) / (s1 - s2)
k_recovered = ((z1 - z2) * inv(s1 - s2, N)) % N
# s1 = k^-1 (z1 + r*d)  =>  d = (s1*k - z1) / r
d_recovered = ((s1 * k_recovered - z1) * inv(r, N)) % N

print()
print(f"  攻击者解出的 k = {k_recovered:064x}   正确? {k_recovered == k}")
print(f"  攻击者解出的 d = {d_recovered}   正确? {d_recovered == d}")

print()
print("  >>> 私钥就这样被完整还原了。")
print("  >>> 所以书中那句'必须用 secrets 模块'不是客套话。")
print("  >>> 用 random 模块、或复用 k，等于把私钥公开。")
