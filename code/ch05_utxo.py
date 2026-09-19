"""第 5 章 · UTXO：账本里没有"余额"这个字段

对应书中第 5.2—5.5 节。
运行：python3 ch05_utxo.py
"""


class UTXOSet:
    """一个极简的 UTXO 集合。键是 "txid:vout"，值是 (金额聪, 归属)"""

    def __init__(self):
        self.utxo = {}

    def credit(self, txid, idx, amount, owner):
        self.utxo[f"{txid}:{idx}"] = (amount, owner)

    def spend(self, txid, idx):
        return self.utxo.pop(f"{txid}:{idx}", None)

    def balance(self, owner):
        """所谓余额，就是把这个人名下的 UTXO 加起来临时算出来的"""
        return sum(amt for amt, o in self.utxo.values() if o == owner)

    def coins(self, owner):
        return {k: v[0] for k, v in self.utxo.items() if v[1] == owner}

    def dump(self, owner):
        print(f"    {owner} 的 UTXO:")
        for k, amt in self.coins(owner).items():
            print(f"      {k}  ->  {amt:>12,} 聪")
        print(f"      合计     {self.balance(owner):>12,} 聪")


BTC = 100_000_000  # 1 BTC = 1 亿聪

ledger = UTXOSet()
ledger.credit("aaa1", 0, int(0.6 * BTC), "alice")
ledger.credit("bbb7", 1, int(0.5 * BTC), "alice")

print("=" * 66)
print("1. Alice 有两张'钞票'（UTXO），账本里没有'余额'字段")
print("=" * 66)
ledger.dump("alice")
print()
print(f"  账本原始数据：{ledger.utxo}")
print("  >>> 注意：没有任何一个地方写着 'alice: 110000000'")

print()
print("=" * 66)
print("2. Alice 要付 Bob 0.3 BTC —— 必须整张花掉，不能只花一半")
print("=" * 66)
PAY = int(0.3 * BTC)
FEE = 10_000

key = "aaa1:0"
src_txid, src_idx = key.split(":")
amount, _ = ledger.spend(src_txid, int(src_idx))
change = amount - PAY - FEE
print(f"  花掉 UTXO {key}  ({amount:,} 聪)")
print(f"  输出 1：给 Bob   {PAY:>12,} 聪")
print(f"  输出 2：找零自己 {change:>12,} 聪")
print(f"  手续费：         {FEE:>12,} 聪  <- 差额，不是独立字段")

ledger.credit("ccc9", 0, PAY, "bob")
ledger.credit("ccc9", 1, change, "alice")

print()
print("  转账后：")
ledger.dump("alice")
ledger.dump("bob")

print()
print("=" * 66)
print("3. 手续费的本质")
print("=" * 66)
print(f"  输入 {amount:,} - 输出 {PAY:,} - 找零 {change:,} = {amount - PAY - change:,} 聪")
print("  这笔差额没有对应的输出，实际上被矿工拿走了。")
print("  >>> 矿工会把这笔钱记在自己的 coinbase 交易里（见第 10 章）。")

print()
print("=" * 66)
print("4. 为什么协议内部只用整数聪")
print("=" * 66)
print(f"  0.1 + 0.2 = {0.1 + 0.2!r}   <- 浮点数，金融系统里是灾难")
print(f"  10000000 + 20000000 = {10000000 + 20000000}   <- 整数聪，精确")
print("  >>> 1 BTC = 100,000,000 聪，协议内部绝不使用浮点数。")
