from pynput.keyboard import Key

# 自动生成 key_map
key_map = {f"<{k.name}>": k for k in Key}

def str_to_key(s: str):
    s = s.strip().lower()
    # 优先查特殊键
    if s in key_map:
        return key_map[s]
    # F1 ~ F24 (Key 里也有，但单独支持更直观)
    if s.startswith("f") and s[1:].isdigit():
        try:
            return getattr(Key, s.lower())
        except AttributeError:
            pass
    # 单个字符
    if len(s) == 1:
        return s
    raise ValueError(f"未知的按键字符串: {s}")

if __name__ == "__main__":
    print(key_map)