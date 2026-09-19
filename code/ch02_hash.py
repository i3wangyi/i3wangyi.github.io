"""第 2 章 · 哈希 —— 单向性与雪崩效应

对应书中第 2.1—2.3 节。
运行：python3 ch02_hash.py
"""
from btclib import sha256

print("=" * 62)
print("1. 同一个输入，永远得到同一个输出（确定性）")
print("=" * 62)
print("sha256('hello')  =", sha256(b"hello").hex())
print("sha256('hello')  =", sha256(b"hello").hex(), " <- 再算一次，完全一样")

print()
print("=" * 62)
print("2. 改一个字母，输出面目全非（雪崩效应）")
print("=" * 62)
for s in [b"hello", b"hellp", b"hello!"]:
    print(f"  sha256({s.decode():8s}) = {sha256(s).hex()}")

print()
print("=" * 62)
print("3. 统计一下：改一个字母会翻转多少位？")
print("=" * 62)
a = int.from_bytes(sha256(b"hello"), "big")
b = int.from_bytes(sha256(b"hellp"), "big")
diff = bin(a ^ b).count("1")
print(f"  两个哈希有 {diff} 位不同（总共 256 位）")
print(f"  比例 {diff / 256:.1%} —— 理想值约 50%")

print()
print("=" * 62)
print("4. 为什么 2^256 是'不可能'的同义词")
print("=" * 62)
# 可观测宇宙原子总数约 10^80
import math
atoms = 1e80
print(f"  可观测宇宙原子总数 ≈ 10^80 = 2^{math.log2(atoms):.0f}")
print(f"  SHA-256 输出空间     = 2^256")
print(f"  也就是说：给宇宙里每个原子分配一个哈希，也只用到 2^{math.log2(atoms):.0f} 个")
print("  暴力破解一个 SHA-256，在物理上不可能。")
