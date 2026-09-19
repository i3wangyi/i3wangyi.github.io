"""第 15 章 · BIP39：随机熵 → 12 个单词

对应书中第 15.3 节。
运行：python3 ch15_bip39.py   （需要同目录下的 english.txt 词表）
"""
import secrets
from btclib import entropy_to_mnemonic, mnemonic_to_seed, load_wordlist, sha256

words = load_wordlist()
print(f"已加载 BIP39 英文词表：{len(words)} 个单词")

print()
print("=" * 68)
print("1. 熵 -> 校验和 -> 11 位分组 -> 单词")
print("=" * 68)
print("  熵位数    校验位    总位数    单词数")
for ent_bits, nwords in [(128, 12), (160, 15), (192, 18), (224, 21), (256, 24)]:
    cs = ent_bits // 32
    print(f"  {ent_bits:>6}  {cs:>8}  {ent_bits + cs:>8}  {nwords:>8}")
print()
print("  128 位熵 + 4 位校验 = 132 位 = 12 × 11 位，每一位组对应词表中的一个词")

print()
print("=" * 68)
print("2. 用官方测试向量验证（熵全为 0）")
print("=" * 68)
mnemonic = entropy_to_mnemonic(bytes(16), words)
print("  " + " ".join(mnemonic))
print()
print("  这是 BIP39 规范里最有名的一条：")
print("  11 个 abandon + 1 个 about。最后一个词由校验和决定，必须是 about。")
print("  >>> 抄错一个字母，钱包会直接提示'校验和错误'—— 就是那 4 位在起作用。")

print()
print("=" * 68)
print("3. 生成一个真实的助记词")
print("=" * 68)
entropy = secrets.token_bytes(16)
mn = entropy_to_mnemonic(entropy, words)
print(f"  熵     : {entropy.hex()}")
print(f"  助记词 : {' '.join(mn)}")
print()

seed = mnemonic_to_seed(" ".join(mn))
print(f"  种子   : {seed.hex()}")
print(f"           = PBKDF2-HMAC-SHA512，2048 轮，64 字节")

print()
print("=" * 68)
print("4. 密码短语（passphrase）的作用")
print("=" * 68)
phrase = "correct horse battery staple"
seed1 = mnemonic_to_seed(" ".join(mn))
seed2 = mnemonic_to_seed(" ".join(mn), phrase)
print(f"  无助记词短语: {seed1[:32].hex()}")
print(f"  有密码短语  : {seed2[:32].hex()}")
print(f"  相同? {seed1 == seed2}")
print()
print("  >>> 同一组助记词 + 不同密码短语 = 完全不同的钱包。")
print("  >>> 好处：拿到助记词也拿不到钱（ plausible deniability ）")
print("  >>> 风险：密码短语忘了 = 钱永久丢失，没有任何找回手段。")

print()
print("=" * 68)
print("5. 校验和到底校验了什么")
print("=" * 68)
good = list(mn)
bad = list(mn)
bad[-1] = "abandon" if bad[-1] != "abandon" else "zoo"
print(f"  正确的词  : {' '.join(good)}")
print(f"  改一个词  : {' '.join(bad)}")
print()
print("  真实钱包会重新计算校验和，发现不匹配就拒绝导入。")
print("  >>> 这也是为什么'手抄一遍然后做恢复测试'是必须的步骤（第 14 章）。")
