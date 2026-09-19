"""第 10 章 · 难度、目标值与挖矿概率

对应书中第 10.1—10.4 节。
运行：python3 ch10_difficulty.py
"""
from btclib import bits_to_target, target_to_difficulty

print("=" * 68)
print("1. bits 的压缩编码：4 字节表示 256 位目标值")
print("=" * 68)
print("  格式：target = 尾数 × 256^(指数 - 3)")
print("  首字节是指数，后 3 字节是尾数")
print()

samples = [
    (0x1D00FFFF, "创世块（2009），难度基准"),
    (0x172B8D1A, "2021 年前后"),
    (0x170355F0, "2023 年"),
    (0x17034219, "2026 年前后"),
]

for bits, note in samples:
    t = bits_to_target(bits)
    d = target_to_difficulty(t)
    print(f"  bits = 0x{bits:08X}   {note}")
    print(f"    target = {t:064x}")
    print(f"    难度   = {d:>22,.0f}")
    print()

print("  看这个数量级：现在的挖矿难度是最初的 86 万亿倍。")
print("  >>> 这个数字本身就是安全性的度量。")

print()
print("=" * 68)
print("2. 单次哈希成功的概率有多小")
print("=" * 68)
t = bits_to_target(0x17034219)
p = t / 2**256
print(f"  target / 2^256 = {p:.4e}")
print(f"  期望尝试次数   = {1/p:.4e}")
print()
leading_zero_bits = 256 - t.bit_length()
print("  换算成前导零：")
print(f"    需要约 {leading_zero_bits} 位前导零")
print(f"    十六进制下约 {leading_zero_bits // 4} 个 '0' 开头")

print()
print("=" * 68)
print("3. 全网算力与出块时间的关系")
print("=" * 68)
print(f"  {'算力':>12}  {'期望出块时间':>14}")
print("  " + "-" * 30)
for name, hr in [("100 EH/s", 100e18), ("600 EH/s", 600e18), ("1 ZH/s", 1e21)]:
    secs = 1 / (p * hr)
    print(f"  {name:>12}  {secs:>11.0f} 秒 ({secs/60:.1f} 分钟)")
print()
print("  目标出块时间是 10 分钟。")
print("  >>> 算力和时间对不上？那就是难度调整该起作用了（见第 11 章）。")

print()
print("=" * 68)
print("4. 难度调整：一个负反馈回路")
print("=" * 68)
print("  每 2016 个块（约两周）调整一次：")
print("    新难度 = 旧难度 × (实际用时 / 20160 分钟)")
print()
for actual_days, note in [(10, "算力暴涨，出块太快"),
                          (14, "理想情况"),
                          (20, "算力流失，出块太慢")]:
    actual_min = actual_days * 24 * 60
    factor = actual_min / 20160
    print(f"    实际用时 {actual_days} 天 -> 难度 × {factor:.3f}   ({note})")
print()
print("  算力上升 -> 难度上调；算力下降 -> 难度下调。")
print("  >>> 把不可控的算力波动，转化成可控的安全性指标。")
