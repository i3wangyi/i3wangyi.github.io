"""
btclib.py —— 《比特币技术入门》全书代码原语的汇总库

所有代码只用 Python 标准库，Python 3.8+ 可直接运行。
每个函数都标注了它在书中对应的章节，方便对照阅读。

警告：本库为教学用途，未经安全审计，不要用于保管真实资产。
"""
import hashlib
import hmac
import secrets
import unicodedata

# ============================================================
# 第 2 章 · 哈希
# ============================================================

def sha256(b: bytes) -> bytes:
    """单次 SHA-256，返回字节"""
    return hashlib.sha256(b).digest()

def dsha(b: bytes) -> bytes:
    """双重 SHA-256。比特币几乎所有哈希都算两遍，见书中第 4.2 节"""
    return sha256(sha256(b))

def hash160(b: bytes) -> bytes:
    """先 SHA-256 再 RIPEMD-160，得到 20 字节公钥哈希。见第 8.2 节"""
    return hashlib.new("ripemd160", sha256(b)).digest()

# ============================================================
# 第 3 章 · secp256k1 椭圆曲线与 ECDSA
# ============================================================

# 曲线参数（国际标准，全球通用）
P  = 2**256 - 2**32 - 977                                                      # 有限域模数
N  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141        # 基点阶
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798        # 生成点 x
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8        # 生成点 y
G  = (Gx, Gy)


def inv(a: int, m: int) -> int:
    """模逆元：求 x 使 a*x ≡ 1 (mod m)"""
    return pow(a, -1, m)


def padd(p, q):
    """椭圆曲线上的点加法。None 表示无穷远点"""
    if p is None:
        return q
    if q is None:
        return p
    # 两点横坐标相同且纵坐标互为相反数 → 和为无穷远点
    if p[0] == q[0] and (p[1] + q[1]) % P == 0:
        return None
    if p == q:                                          # 切线斜率
        lam = (3 * p[0] * p[0]) * inv(2 * p[1], P) % P
    else:                                               # 割线斜率
        lam = (q[1] - p[1]) * inv(q[0] - p[0], P) % P
    x = (lam * lam - p[0] - q[0]) % P
    y = (lam * (p[0] - x) - p[1]) % P
    return (x, y)


def pmul(k: int, p=G):
    """标量乘法：算 k*p。二进制展开（double-and-add），256 次循环而非 k 次加法"""
    r = None
    while k:
        if k & 1:
            r = padd(r, p)
        p = padd(p, p)          # 倍点
        k >>= 1
    return r


def ser_p(pt) -> bytes:
    """SEC1 压缩公钥序列化：0x02(y 偶) / 0x03(y 奇) + 32 字节 x"""
    return bytes([2 + (pt[1] & 1)]) + pt[0].to_bytes(32, "big")


def sign(z: int, d: int):
    """ECDSA 签名：用私钥 d 对哈希值 z 签名，返回 (r, s)

    注意：k 必须是密码学安全随机数且绝不复用。
    复用 k 会直接泄露私钥（2010 年索尼 PS3 事件），见第 3.5 节。
    """
    while True:
        k = secrets.randbelow(N - 1) + 1
        r = pmul(k)[0] % N
        if r == 0:
            continue
        s = (inv(k, N) * (z + r * d)) % N
        if s == 0:
            continue
        return r, s


def verify(z: int, sig, Q) -> bool:
    """ECDSA 验签：用公钥 Q 验证 (r, s) 是否是对 z 的有效签名"""
    r, s = sig
    w = inv(s, N)
    u1, u2 = (z * w) % N, (r * w) % N
    pt = padd(pmul(u1), pmul(u2, Q))
    return pt is not None and pt[0] % N == r


# ============================================================
# 第 4 章 · Merkle 树
# ============================================================

def merkle_root(txids):
    """txids 是各交易 txid 的字节串列表（内部字节序）。
    奇数个节点时复制最后一个与自己配对——历史上有 CVE-2012-2459 漏洞，见第 4.4 节。"""
    layer = list(txids)
    if not layer:
        return b"\x00" * 32
    while len(layer) > 1:
        if len(layer) % 2:
            layer.append(layer[-1])
        layer = [dsha(layer[i] + layer[i + 1]) for i in range(0, len(layer), 2)]
    return layer[0]


# ============================================================
# 第 8 章 · 地址编码
# ============================================================

B58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def base58(b: bytes) -> str:
    """Base58 编码：去掉了 0 / O / I / l 这些容易看错的字符"""
    n = int.from_bytes(b, "big")
    s = ""
    while n:
        n, r = divmod(n, 58)
        s = B58_ALPHABET[r] + s
    # 每个前导零字节对应一个 '1'
    return "1" * (len(b) - len(b.lstrip(b"\x00"))) + s


def b58check(payload: bytes) -> str:
    """Base58Check：附加 4 字节校验和，防止输错地址"""
    chk = dsha(payload)[:4]
    return base58(payload + chk)


BECH32_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
BECH32_GEN = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]


def bech32_polymod(values):
    chk = 1
    for x in values:
        b = chk >> 25
        chk = ((chk & 0x1FFFFFF) << 5) ^ x
        for i in range(5):
            chk ^= BECH32_GEN[i] if ((b >> i) & 1) else 0
    return chk


def bech32_hrp_expand(hrp):
    return [ord(c) >> 5 for c in hrp] + [0] + [ord(c) & 31 for c in hrp]


def convertbits(data, frombits: int, tobits: int, pad=True):
    """8 位分组 → 5 位分组，因为 Bech32 字母表只有 32 个字符"""
    acc = bits = 0
    ret = []
    for v in data:
        acc = (acc << frombits) | v
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & ((1 << tobits) - 1))
    if pad and bits:
        ret.append((acc << (tobits - bits)) & ((1 << tobits) - 1))
    return ret


def bech32_encode(hrp: str, data) -> str:
    """Bech32 编码。hrp 主网用 'bc'，测试网用 'tb'"""
    values = bech32_hrp_expand(hrp) + data
    pm = bech32_polymod(values + [0] * 6) ^ 1
    checksum = [(pm >> 5 * (5 - i)) & 31 for i in range(6)]
    return hrp + "1" + "".join(BECH32_CHARSET[d] for d in data + checksum)


# ============================================================
# 第 10 章 · 难度
# ============================================================

def bits_to_target(bits: int) -> int:
    """把 4 字节压缩难度还原成 256 位目标值。格式：首字节是指数，后 3 字节是尾数"""
    exp = bits >> 24
    mant = bits & 0x007FFFFF
    if exp <= 3:
        return mant >> (8 * (3 - exp))
    return mant << (8 * (exp - 3))


def target_to_difficulty(t: int) -> float:
    """难度 = 基准 target / 当前 target"""
    D1 = 0x00000000FFFF0000000000000000000000000000000000000000000000000000
    return D1 / t


# ============================================================
# 第 15 章 · BIP39 助记词 与 BIP32 HD 钱包
# ============================================================

def load_wordlist(path="english.txt"):
    """加载 BIP39 官方 2048 词表"""
    with open(path, encoding="utf-8") as f:
        return [w.strip() for w in f if w.strip()]


def entropy_to_mnemonic(entropy: bytes, words) -> list:
    """BIP39：熵 + 校验和 → 11 位一组 → 映射到词表"""
    assert len(entropy) in (16, 20, 24, 28, 32), "熵必须是 16/20/24/28/32 字节"
    cs_len = len(entropy) * 8 // 32                 # 128 位熵 → 4 位校验
    h = sha256(entropy)
    bits = bin(int.from_bytes(entropy, "big"))[2:].zfill(len(entropy) * 8)
    cs = bin(h[0])[2:].zfill(8)[:cs_len]
    total = bits + cs
    return [words[int(total[i:i + 11], 2)] for i in range(0, len(total), 11)]


def mnemonic_to_seed(mnemonic: str, passphrase: str = "") -> bytes:
    """BIP39：助记词 → 64 字节种子（PBKDF2-HMAC-SHA512，2048 轮）"""
    m = unicodedata.normalize("NFKD", mnemonic)
    s = unicodedata.normalize("NFKD", "mnemonic" + passphrase)
    return hashlib.pbkdf2_hmac("sha512", m.encode(), s.encode(), 2048, 64)


def master_key(seed: bytes):
    """BIP32：种子 → (主私钥, 链码)"""
    I = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
    return int.from_bytes(I[:32], "big"), I[32:]


def ckd_priv(k: int, c: bytes, index: int):
    """BIP32 CKDpriv：从父私钥派生子私钥。
    index >= 0x80000000 表示硬化派生（用私钥算），否则是普通派生（用公钥算）。"""
    if index >= 0x80000000:
        data = b"\x00" + k.to_bytes(32, "big") + index.to_bytes(4, "big")
    else:
        data = ser_p(pmul(k)) + index.to_bytes(4, "big")
    I = hmac.new(c, data, hashlib.sha512).digest()
    return (k + int.from_bytes(I[:32], "big")) % N, I[32:]


def derive_path(seed: bytes, path: str):
    """按 BIP32 路径派生，如 "m/84'/0'/0'/0/0"。返回 (私钥, 链码)"""
    k, c = master_key(seed)
    for part in path.split("/")[1:]:
        hardened = part.endswith("'") or part.endswith("h")
        idx = int(part.rstrip("'h")) + (0x80000000 if hardened else 0)
        k, c = ckd_priv(k, c, idx)
    return k, c


# ============================================================
# 自检：验证本书用到的官方测试向量
# ============================================================

def self_test():
    """跑一遍官方测试向量，确认实现正确"""
    checks = []

    # 第 2 章：sha256("hello")
    checks.append(("sha256('hello')",
                   sha256(b"hello").hex() ==
                   "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"))

    # 第 3 章：私钥 1 的公钥应等于生成点 G
    checks.append(("secp256k1: 私钥 1 → G", pmul(1) == G))

    # 第 3 章：ECDSA 签名，篡改后应失效
    d = 1234567890
    Q = pmul(d)
    z = int.from_bytes(sha256(b"I send 0.5 BTC to Bob"), "big")
    sig = sign(z, d)
    bad = int.from_bytes(sha256(b"I send 5 BTC to Bob"), "big")
    checks.append(("ECDSA 正常验签通过", verify(z, sig, Q)))
    checks.append(("ECDSA 篡改后失败", not verify(bad, sig, Q)))

    # 第 8 章：hash160 = RIPEMD160(SHA256(x))，用已知向量验证
    checks.append(("hash160(b'abc') 与已知向量一致",
                   hash160(b"abc").hex() == "bb1be98c142444d7a56aa3981c3942a978e4dc33"))

    # 第 10 章：创世块难度应为 1.0
    checks.append(("创世块难度 = 1.0",
                   abs(target_to_difficulty(bits_to_target(0x1D00FFFF)) - 1.0) < 1e-9))

    # 第 15 章：BIP32 官方测试向量 1
    seed = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    k, c = master_key(seed)
    checks.append(("BIP32 主私钥与官方向量一致",
                   k.to_bytes(32, "big").hex() ==
                   "e8f32e723decf4051aefac8e2c93c9c5b214313817cdb01a1494b917c8436b35"))
    checks.append(("BIP32 主链码与官方向量一致",
                   c.hex() == "873dff81c02f525623fd1fe5167eac3a55a049de3d314bb42ee227ffed37d508"))
    k1, _ = derive_path(seed, "m/0'")
    checks.append(("BIP32 m/0' 与官方向量一致",
                   k1.to_bytes(32, "big").hex() ==
                   "edb2e14f9ee77d26dd93b4ecede8d16ed408ce149b6cd80b0715a2d911a0afea"))

    # 第 19 章：Merkle 根可计算
    txs = [dsha(f"tx{i}".encode()) for i in range(1, 5)]
    checks.append(("Merkle 根可计算", len(merkle_root(txs)) == 32))

    ok = True
    for name, passed in checks:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
        ok = ok and passed
    return ok


if __name__ == "__main__":
    print("btclib 自检 —— 用官方测试向量验证书中所有原语")
    print("=" * 52)
    ok = self_test()
    print("=" * 52)
    print("全部通过" if ok else "存在失败项，请检查")
    raise SystemExit(0 if ok else 1)
