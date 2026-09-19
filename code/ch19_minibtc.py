"""第 19 章 · 迷你比特币：150 行的完整实现

包含书中第 19.2 节的完整代码，以及第 19.3 节的演示
和第 19.4 节的篡改测试。

运行：python3 ch19_minibtc.py
"""
"""迷你比特币 —— 一个可运行的区块链实现（教学用）"""
import hashlib, json, time

# ============ 1. 密码学原语 ============
def sha256(b): return hashlib.sha256(b).digest()
def dsha(b):   return sha256(sha256(b))          # 双重 SHA256
def b2h(x):    return x.hex() if isinstance(x, bytes) else x

# ============ 2. 交易 ============
class Tx:
    def __init__(self, inputs, outputs, timestamp=None):
        self.inputs  = inputs      # [{"txid":…, "vout":…}]
        self.outputs = outputs     # [{"value":…, "to":…}]
        self.timestamp = timestamp or int(time.time())

    def payload(self, with_sig=True):
        """签名覆盖的内容；算 txid 时不包含签名"""
        ins = [{"txid": i["txid"], "vout": i["vout"],
                "sig": i.get("sig", "")} for i in self.inputs]
        return json.dumps({"in": ins, "out": self.outputs,
                           "ts": self.timestamp},
                          sort_keys=True, separators=(',', ':')).encode()

    @property
    def txid(self):
        return b2h(dsha(self.payload(with_sig=False)))

    def sign(self, secret):
        """简化签名：真实系统用 ECDSA，见第 3 章"""
        import hmac
        for i in self.inputs:
            i["sig"] = hmac.new(secret, self.payload(), hashlib.sha256).hexdigest()

    def verify(self, secret):
        import hmac
        for i in self.inputs:
            want = hmac.new(secret, self.payload(), hashlib.sha256).hexdigest()
            if i.get("sig") != want:
                return False
        return True

# ============ 3. 区块 ============
class Block:
    def __init__(self, index, prev_hash, txs,
                 timestamp=None, nonce=0, difficulty=3):
        self.index = index
        self.prev_hash = prev_hash
        self.txs = txs
        self.timestamp = timestamp or int(time.time())
        self.nonce = nonce
        self.difficulty = difficulty

    @property
    def merkle_root(self):
        layer = [bytes.fromhex(t.txid) for t in self.txs] or [b"\x00"*32]
        while len(layer) > 1:
            if len(layer) % 2: layer.append(layer[-1])
            layer = [dsha(layer[i] + layer[i+1])
                     for i in range(0, len(layer), 2)]
        return b2h(layer[0])

    def header(self):
        return (f"{self.index}|{self.prev_hash}|{self.merkle_root}|"
                f"{self.timestamp}|{self.difficulty}|{self.nonce}").encode()

    @property
    def hash(self):
        return b2h(dsha(self.header()))

    def mine(self):
        """工作量证明：不断改 nonce 直到哈希满足前导零要求"""
        target = "0" * self.difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
        return self

# ============ 4. 链 ============
class Chain:
    def __init__(self, difficulty=3):
        self.difficulty = difficulty
        self.blocks = []
        self.utxo = {}          # "txid:vout" -> {"value":…, "to":…}
        self._genesis()

    def _genesis(self):
        cb = Tx([], [{"value": 50_00000000, "to": "satoshi"}])
        g = Block(0, "0"*64, [cb], difficulty=self.difficulty).mine()
        self.blocks.append(g)
        self._apply(g)

    def _apply(self, block):
        for tx in block.txs:
            for i in tx.inputs:                  # 消耗输入
                self.utxo.pop(f"{i['txid']}:{i['vout']}", None)
            for n, o in enumerate(tx.outputs):   # 创建输出
                self.utxo[f"{tx.txid}:{n}"] = {"value": o["value"], "to": o["to"]}

    def balance(self, addr):
        """余额 = 该地址名下所有 UTXO 之和（账本里没有这个字段）"""
        return sum(u["value"] for u in self.utxo.values() if u["to"] == addr)

    def add_block(self, txs):
        prev = self.blocks[-1]
        b = Block(len(self.blocks), prev.hash, txs,
                  difficulty=self.difficulty).mine()
        assert b.prev_hash == prev.hash          # 哈希链校验
        self.blocks.append(b)
        self._apply(b)
        return b

    def is_valid(self):
        for i in range(1, len(self.blocks)):
            cur, prev = self.blocks[i], self.blocks[i-1]
            if cur.prev_hash != prev.hash: return False
            if not cur.hash.startswith("0" * cur.difficulty):
                return False
        return True


# ============ 5. 演示 ============
if __name__ == "__main__":
    print("=" * 68)
    print("迷你比特币 —— 30 行代码的区块链核心")
    print("=" * 68)

    c = Chain(difficulty=3)
    print(f"创世块哈希 : {c.blocks[0].hash}")
    print(f"satoshi 余额: {c.balance('satoshi'):,} 聪")
    print()

    # 挖一个块，给矿工 50 BTC 的 coinbase 奖励
    cb = Tx([], [{"value": 50_00000000, "to": "miner"}])
    b1 = c.add_block([cb])
    print(f"块 1 哈希  : {b1.hash}  | nonce: {b1.nonce}")
    print(f"             (难度 3 → 平均要试 16^3 = {16**3:,} 次)")

    # 矿工付 10 BTC 给 alice，找零 39.999 BTC，0.001 作为手续费
    pay = Tx([{"txid": cb.txid, "vout": 0}],
             [{"value": 10_00000000, "to": "alice"},
              {"value": 39_99900000, "to": "miner"}])
    b2 = c.add_block([pay])
    print(f"块 2 哈希  : {b2.hash}  | nonce: {b2.nonce}")
    print()

    print(f"alice 余额 : {c.balance('alice'):,} 聪")
    print(f"miner 余额 : {c.balance('miner'):,} 聪")
    print(f"链有效     : {c.is_valid()}")
    print(f"块数       : {len(c.blocks)}")
    print()

    # ---------- 篡改测试 ----------
    print("=" * 68)
    print("篡改测试：偷偷把矿工奖励从 50 BTC 改成 99 BTC")
    print("=" * 68)
    c.blocks[1].txs[0].outputs[0]["value"] = 99_00000000
    c.blocks[1].nonce += 1
    print(f"篡改后链有效: {c.is_valid()}")
    print()
    print("失败原因链条：")
    print("  1. 改了 coinbase 金额 -> 交易内容变了 -> txid 变了")
    print("  2. txid 变了         -> merkle_root 变了")
    print("  3. merkle_root 变了  -> 区块头变了   -> 块 1 的哈希变了")
    print("  4. 块 1 哈希变了     -> 块 2 里的 prev_hash 对不上了")
    print()
    print("  在真实比特币里，攻击者还需要重新挖出块 1 之后的所有区块，")
    print("  并且要跑得比全网诚实算力更快。")
    print()
    print("  >>> 这就是第 2 章说的'生产贵、验证便宜'在起作用。")

    # ---------- 难度演示 ----------
    print()
    print("=" * 68)
    print("难度对 nonce 的影响")
    print("=" * 68)
    print(f"  {'难度':>4}  {'期望尝试次数':>16}")
    print("  " + "-" * 24)
    for d in range(2, 6):
        print(f"  {d:>4}  {16**d:>16,}")
