"""第 2 章 · 亲手挖一个矿

对应书中第 2.4 节。核心就一句话：不断改 nonce，直到哈希满足条件。
运行：python3 ch02_mine.py
"""
import time
from btclib import sha256


def mine(prefix_zeros: int, base: str = "block-data"):
    """要求哈希以 n 个 '0' 开头，返回 (nonce, 哈希, 耗时秒)"""
    target = "0" * prefix_zeros
    n = 0
    t0 = time.time()
    while True:
        h = sha256(f"{base}-{n}".encode()).hex()
        if h.startswith(target):
            return n, h, time.time() - t0
        n += 1


print("每多一个前导零，难度乘以 16。亲手感受一下这个指数增长：")
print()
print(f"{'前导零':>6}  {'期望尝试次数':>16}  {'实际 nonce':>10}  {'耗时':>8}")
print("-" * 52)

for zeros in range(1, 6):
    nonce, h, elapsed = mine(zeros)
    print(f"{zeros:>6}  {16**zeros:>16,}  {nonce:>10,}  {elapsed:>7.3f}s")

print()
print("-" * 52)
print("关键不对称性：")
print("  · 生产（挖矿）：平均要试 16^n 次，成本随难度指数上升")
print("  · 验证：只需要算一遍哈希，看开头有几个零")
print()
print("这就是第 2.5 节说的'生产贵、验证便宜'，整个共识机制的支点。")

# 展示一次真实的挖矿结果
nonce, h, _ = mine(4)
print()
print("一个具体的例子（难度 4）：")
print(f"  nonce = {nonce}")
print(f"  哈希  = {h}")
print(f"  验证  = 只需 sha256('block-data-{nonce}') 算一遍，确认开头是 4 个 0")
