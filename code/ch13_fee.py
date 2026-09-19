"""第 13 章 · 手续费按字节算，不按金额算

对应书中第 13.3—13.5 节。
运行：python3 ch13_fee.py
"""

print("=" * 68)
print("1. 同样一笔转账，输入越多越贵")
print("=" * 68)
print("  费用 = 虚拟字节数 (vB) × 费率 (sat/vB)，与转账金额完全无关")
print()

# 典型交易的虚拟字节数（书中第 13.3 节表格）
tx_types = [
    ("1 输入 2 输出 · P2PKH",      226),
    ("1 输入 2 输出 · P2WPKH",     141),
    ("1 输入 2 输出 · P2TR",       111),
    ("10 输入 2 输出 · P2PKH",    1480),
]

for rate in [5, 50]:
    print(f"  费率 = {rate} sat/vB")
    for name, vsize in tx_types:
        print(f"    {name:<26} {vsize:>5} vB  ->  {vsize * rate:>7,} 聪 "
              f"({vsize * rate / 1e8:.8f} BTC)")
    print()

print("  >>> 转 1 BTC 和转 0.001 BTC，如果输入输出结构相同，手续费完全一样。")
print("  >>> 用 bc1q / bc1p 地址能省约 40% —— 这就是 SegWit 的直接好处。")

print()
print("=" * 68)
print("2. 算一笔具体的账")
print("=" * 68)


def analyze(inputs_sat, outputs_sat, vsize_vb):
    fee = sum(inputs_sat) - sum(outputs_sat)
    return fee, fee / vsize_vb


inputs = [100_000_000]                    # 1 BTC
outputs = [30_000_000, 69_990_000]        # 0.3 + 0.6999
fee, rate = analyze(inputs, outputs, 225)
print(f"  输入  : {inputs[0]:>12,} 聪")
print(f"  输出  : {outputs[0]:>12,} 聪")
print(f"          {outputs[1]:>12,} 聪")
print(f"  手续费: {fee:>12,} 聪")
print(f"  大小  : {225:>12} vB")
print(f"  费率  : {rate:>12.2f} sat/vB")

print()
print("=" * 68)
print("3. 卡住了怎么加价（RBF / CPFP）")
print("=" * 68)
target_rate = 100
need = target_rate * 225
print(f"  如果想提到 {target_rate} sat/vB：")
print(f"    需要的手续费 = {need:,} 聪")
print(f"    差额         = {need - fee:,} 聪")
print(f"    找零应改为   = {outputs[1] - (need - fee):,} 聪")
print()
print("  两种方式：")
print("    RBF  : 付款方用更高费用重发一笔，替换掉原来的（前提是标记了可替换）")
print("    CPFP : 收款方花掉卡住的输出，发一笔高费率的子交易，把父交易一起拉上车")

print()
print("=" * 68)
print("4. 卡住的代价：确认时间随费率变化")
print("=" * 68)
print("  mempool 里待确认的交易按费率排序，矿工从高到低挑。")
print()
for r, note in [(1, "可能被拒收（低于最小中继费率）"),
                (5, "空闲时段可确认"),
                (20, "正常时段可确认"),
                (100, "拥堵时也能较快确认")]:
    print(f"    {r:>4} sat/vB  {note}")
print()
print("  >>> 0 确认交易不安全，因为可以被 RBF 替换掉。")
