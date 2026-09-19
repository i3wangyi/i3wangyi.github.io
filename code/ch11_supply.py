"""第 11 章 · 减半与 2100 万上限

对应书中第 11.2—11.3 节。
运行：python3 ch11_supply.py
"""

BLOCKS_PER_EPOCH = 210_000
FIRST_SUBSIDY = 50  # BTC

print("=" * 68)
print("1. 区块补贴：每 210,000 个块减半一次（约 4 年）")
print("=" * 68)
print(f"  {'次数':>4}  {'区块高度':>12}  {'区块补贴':>12}  {'该期发行量':>14}")
print("  " + "-" * 48)

running = 0
for i in range(7):
    height = BLOCKS_PER_EPOCH * i
    subsidy = FIRST_SUBSIDY / (2**i)
    issued = BLOCKS_PER_EPOCH * subsidy
    running += issued
    print(f"  {i:>4}  {height:>12,}  {subsidy:>12.8f}  {issued:>14,.0f}")
    print(f"                               累计 {running:>14,.0f} BTC")

    if subsidy < 0.00000001:
        print(f"                               ^ 补贴已小于 1 聪，到此结束")
        break

print()
print("=" * 68)
print("2. '2100 万' 是怎么来的：一个收敛的等比数列")
print("=" * 68)
total = sum(BLOCKS_PER_EPOCH * FIRST_SUBSIDY / (2**i) for i in range(64))
print(f"  无穷级数求和 = {total:.8f} BTC")
print()
print("  它不是某个圆整的数字，而是等比数列收敛的结果：")
print("    210000 × (50 + 25 + 12.5 + 6.25 + ...)")
print()
print(f"  由于最小单位是 1 聪（1e-8 BTC），实际总量会停在")
print(f"  {total:.8f} BTC 附近 —— 略小于 21,000,000。")

print()
print("=" * 68)
print("3. 为什么上限改不了")
print("=" * 68)
print("  要修改 2100 万，必须修改共识规则，而这需要几乎全网节点同时接受。")
print()
print("  >>> 不是'有法律禁止增发'，而是'技术上做不到'。")
print("  >>> 这种'制度硬约束'才是稀缺性的真正来源。")

print()
print("=" * 68)
print("4. 2140 年之后：矿工收入全靠手续费")
print("=" * 68)
print("  区块空间是固定供给，用户按 sat/vB 竞价，价高者先上车。")
print()
print("  这是一个真实的长期问题，两种读法：")
print()
print("  【乐观】市值和使用量增长 -> 手续费自然补上区块补贴的空缺")
print("  【悲观】链上交易量不足 -> 矿工退出 -> 算力下降 -> 安全性降低")
print()
print("  >>> 目前无法证伪，都在预测几十年后的市场。")
print("  >>> 这也解释了为什么'区块空间该用来存什么'（铭文之争）不是纯技术问题")
print("      —— 它直接关系到安全预算（见第 22、25 章）。")
