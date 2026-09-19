"""第 4 章 · Merkle 树与 Merkle 证明

对应书中第 4.3—4.4 节。
运行：python3 ch04_merkle.py
"""
from btclib import dsha, merkle_root

print("=" * 66)
print("1. 把 n 笔交易压成一个 32 字节的根哈希")
print("=" * 66)

for count in [4, 8, 100, 4000]:
    txs = [dsha(f"tx{i}".encode()) for i in range(count)]
    root = merkle_root(txs)
    import math
    proof_size = math.ceil(math.log2(count))
    print(f"  {count:>5} 笔交易 -> Merkle 根 {root[:8].hex()}...  "
          f"证明只需 {proof_size:>2} 个哈希 ≈ {proof_size * 32:>4} 字节")

print()
print("  对比：不用 Merkle 树，验证一笔交易要下载整个区块（1 MB+）")
print("  这也是手机轻钱包（SPV）能工作的原因。")

print()
print("=" * 66)
print("2. 亲手做一次 Merkle 证明（证明 Tx1 确实在区块里）")
print("=" * 66)

# 4 笔交易
txs = [dsha(f"tx{i}".encode()) for i in range(1, 5)]
h1, h2, h3, h4 = txs
h12 = dsha(h1 + h2)
h34 = dsha(h3 + h4)
root = dsha(h12 + h34)

print(f"  区块里有 4 笔交易，Merkle 根 = {root.hex()}")
print()

# 轻钱包只有：Tx1 本身 + 兄弟节点 h2 + 上层兄弟 h34 + 区块头里的 root
proof = [h2, h34]
print("  轻钱包手上的东西：")
print(f"    · 要验证的交易 Tx1 = {h1[:12].hex()}...")
print(f"    · 第 1 个证明节点  = {proof[0][:12].hex()}...  (兄弟)")
print(f"    · 第 2 个证明节点  = {proof[1][:12].hex()}...  (上一层的兄弟)")
print(f"    · 区块头里的根     = {root[:12].hex()}...  (本来就信)")
print()

# 只用这些信息重算根
step = dsha(h1 + proof[0])
computed = dsha(step + proof[1])
print(f"  第 1 步：H(Tx1 ‖ 兄弟) = {step[:12].hex()}...")
print(f"  第 2 步：H(上面的 ‖ 兄弟) = {computed[:12].hex()}...")
print()
print(f"  重算出的根 == 区块头里的根 ? {computed == root}")
print()
print("  只用了 2 个哈希（64 字节）就证明了 Tx1 在这个区块里。")

print()
print("=" * 66)
print("3. 篡改一笔交易，根立刻改变")
print("=" * 66)
evil_txs = [dsha(b"evil-tx")] + txs[1:]
print(f"  原根 = {merkle_root(txs).hex()}")
print(f"  改后 = {merkle_root(evil_txs).hex()}")
print(f"  相同? {merkle_root(txs) == merkle_root(evil_txs)}")
print()
print("  >>> 区块头里存着 Merkle 根，所以改任何一笔交易都会让区块哈希失效。")
