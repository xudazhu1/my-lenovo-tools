for i in range(1, 27):  # Ctrl+A 到 Ctrl+Z
    print(f"Ctrl+{chr(64+i)} -> hex: {hex(i)}  dec: {i}  repr: {repr(chr(i))}")