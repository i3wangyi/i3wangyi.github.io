"""一键运行全部示例，并报告通过情况

运行：python3 run_all.py
"""
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).parent
SCRIPTS = [
    "btclib.py",           # 原语库 + 官方测试向量自检
    "ch02_hash.py",        # 哈希：单向性与雪崩效应
    "ch02_mine.py",        # 亲手挖一个矿
    "ch03_ecdsa.py",       # ECDSA 签名 + 随机数复用事故
    "ch04_merkle.py",      # Merkle 树与 Merkle 证明
    "ch05_utxo.py",        # UTXO：账本里没有"余额"
    "ch06_parse_tx.py",    # 拆开一笔交易的原始字节
    "ch08_address.py",     # 从私钥一路算到地址
    "ch10_difficulty.py",  # 难度、目标值与挖矿概率
    "ch11_supply.py",      # 减半与 2100 万上限
    "ch13_fee.py",         # 手续费按字节算
    "ch15_bip39.py",       # 助记词
    "ch15_bip32.py",       # HD 钱包
    "ch19_minibtc.py",     # 150 行的完整区块链
]


def main():
    print("《比特币技术入门》代码示例 — 全部运行")
    print("=" * 62)

    passed, failed = [], []
    for name in SCRIPTS:
        path = HERE / name
        if not path.exists():
            print(f"  MISSING  {name}")
            failed.append(name)
            continue
        t0 = time.time()
        r = subprocess.run([sys.executable, str(path)],
                           capture_output=True, text=True, cwd=HERE)
        dt = time.time() - t0
        if r.returncode == 0:
            print(f"  PASS     {name:<22} ({dt:.2f}s)")
            passed.append(name)
        else:
            print(f"  FAIL     {name:<22} ({dt:.2f}s)")
            failed.append(name)
            for line in (r.stderr or r.stdout).strip().splitlines()[-6:]:
                print(f"             {line}")

    print("=" * 62)
    print(f"通过 {len(passed)} / {len(SCRIPTS)}" + (f"，失败：{failed}" if failed else "，全部通过"))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
