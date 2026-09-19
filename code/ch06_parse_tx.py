"""第 6 章 · 拆开一笔交易的原始字节

对应书中第 6.2—6.4 节。
运行：python3 ch06_parse_tx.py
"""
import struct
from btclib import dsha


# ---------- 序列化辅助 ----------
def varint(n):
    """比特币的变长整数：按首字节决定长度"""
    if n < 0xFD:
        return bytes([n])
    if n <= 0xFFFF:
        return b"\xFD" + struct.pack("<H", n)
    if n <= 0xFFFFFFFF:
        return b"\xFE" + struct.pack("<I", n)
    return b"\xFF" + struct.pack("<Q", n)


def le(n, size):
    """小端序整数字节"""
    return n.to_bytes(size, "little")


# ---------- 构造一笔 P2PKH 交易 ----------
# 一个典型的 P2PKH 解锁脚本：<签名(71B)> <公钥(33B)>
sig = bytes.fromhex("30" + "44" + "02" + "20" + "11" * 32 + "02" + "20" + "22" * 32 + "01")
pub = bytes.fromhex("02" + "33" * 32)
script_sig = bytes([len(sig)]) + sig + bytes([len(pub)]) + pub

# P2PKH 锁定脚本：OP_DUP OP_HASH160 <20B> OP_EQUALVERIFY OP_CHECKSIG
lock_a = bytes.fromhex("76a914" + "47" * 20 + "88ac")
lock_b = bytes.fromhex("76a914" + "88" * 20 + "88ac")

prev_txid_be = "a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90"

raw = (
    le(2, 4)                                   # version
    + varint(1)                                # 输入数量
    + bytes.fromhex(prev_txid_be)[::-1]        # prev_txid（小端存储）
    + le(0, 4)                                 # prev_vout
    + varint(len(script_sig)) + script_sig
    + le(0xFFFFFFFF, 4)                        # sequence
    + varint(2)                                # 输出数量
    + le(30_000_000, 8) + varint(len(lock_a)) + lock_a
    + le(69_990_000, 8) + varint(len(lock_b)) + lock_b
    + le(0, 4)                                 # locktime
)

print("=" * 66)
print("1. 原始字节（序列化后的交易，共 %d 字节）" % len(raw))
print("=" * 66)
h = raw.hex()
for i in range(0, len(h), 64):
    print("  " + h[i:i + 64])

# ---------- 解析器 ----------
class Reader:
    def __init__(self, data):
        self.d, self.i = data, 0

    def take(self, n):
        b = self.d[self.i:self.i + n]
        self.i += n
        return b

    def u32(self):
        return int.from_bytes(self.take(4), "little")

    def u64(self):
        return int.from_bytes(self.take(8), "little")

    def varint(self):
        n = self.take(1)[0]
        if n < 0xFD:
            return n
        if n == 0xFD:
            return int.from_bytes(self.take(2), "little")
        if n == 0xFE:
            return self.u32()
        return self.u64()


def parse_tx(data):
    r = Reader(data)
    tx = {"version": r.u32(), "vin": [], "vout": []}
    for _ in range(r.varint()):
        tx["vin"].append({
            "prev_txid": r.take(32)[::-1].hex(),   # 转回大端给人看
            "prev_vout": r.u32(),
            "script_sig_len": r.varint(),
        })
        tx["vin"][-1]["script_sig"] = r.take(tx["vin"][-1]["script_sig_len"]).hex()
        tx["vin"][-1]["sequence"] = r.u32()
    for _ in range(r.varint()):
        tx["vout"].append({
            "value_sat": r.u64(),
            "script_len": r.varint(),
        })
        tx["vout"][-1]["script_pubkey"] = r.take(tx["vout"][-1]["script_len"]).hex()
    tx["locktime"] = r.u32()
    return tx


def txid(data):
    """txid = 双重 SHA-256 后反转字节序"""
    return dsha(data)[::-1].hex()


print()
print("=" * 66)
print("2. 解析结果")
print("=" * 66)
tx = parse_tx(raw)
print(f"  version  : {tx['version']}")
for i, vin in enumerate(tx["vin"]):
    print(f"  vin[{i}]   : prev_txid = {vin['prev_txid']}")
    print(f"             prev_vout = {vin['prev_vout']}")
    print(f"             script    = {vin['script_sig'][:40]}... ({vin['script_sig_len']} 字节)")
    print(f"             sequence  = 0x{vin['sequence']:08x}")
for i, out in enumerate(tx["vout"]):
    btc = out["value_sat"] / 100_000_000
    print(f"  vout[{i}]  : {out['value_sat']:>12,} 聪 ({btc:.8f} BTC)")
    print(f"             script    = {out['script_pubkey']}")
print(f"  locktime : {tx['locktime']}")
print(f"  size     : {len(raw)} 字节")

print()
print("=" * 66)
print("3. txid 为什么和原始字节长得不像")
print("=" * 66)
print(f"  原始字节前 32 个 hex 字符: {h[:32]}")
print(f"  txid                     : {txid(raw)}")
print()
print("  两个坑：")
print("    ① 要算两遍 SHA-256，不是一遍")
print("    ② 要反转字节序 —— 协议里用小端，展示给人类用大端")
print()
print("  90% 的人自己算 txid 对不上浏览器，都是忘了第 ② 步。")

print()
print("=" * 66)
print("4. 关键设计：输入里不写金额")
print("=" * 66)
print("  看上面的 vin[0]，它只写了'我要花哪张 UTXO'，没有写'那张有多少钱'。")
print("  金额必须由验证者自己去账本里查。")
print("  >>> 如果输入能自己声明金额，攻击者就能谎报'我这张有 100 万 BTC'。")
