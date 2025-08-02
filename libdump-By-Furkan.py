import subprocess
import sys
import os
import re
import time
from collections import defaultdict

def color(text, code): return f"\033[{code}m{text}\033[0m"

MESSAGES = {
    "banner": [
        "R|", "Ra|", "Rad|", "Rada|", "Radar|", "Radare|",
        "Radare2|", "Radare2 |", "Radare2 Du|", "Radare2 Dump|", "Radare2 Dumpe|",
        "Radare2 Dumper|", "Radare2 Dumper B", "Radare2 Dumper BY", "Radare2 Dumper BY F",
        "Radare2 Dumper BY FU", "Radare2 Dumper BY FUR", "Radare2 Dumper BY FURK",
        "Radare2 Dumper BY FURKA", "Radare2 Dumper BY FURKAN"
    ],
    "install_termux": "Installing binutils...",
    "extracting": "Extracting symbols:",
    "saved_to": "Dump saved:",
    "file_not_found": "File not found:",
    "termux_detected": "Termux ready",
    "grant_storage": "Run termux-setup-storage",
    "processing": "Processing...",
    "methods_found": "Methods:",
    "classes_found": "Classes:",
    "time_taken": "Time:",
    "output_dir_created": "Directory created:",
    "missing_binutils": "Binutils missing. Installing...",
    "invalid_path": "Invalid path",
    "storage_permission": "Storage permission needed",
    "select_lib": "Enter full path to .so file (or 'q' to quit): ",
    "press_enter": "Press Enter to exit"
}

def clear_screen():
    os.system('clear')

def banner():
    try:
        term_width = os.get_terminal_size().columns
    except OSError:
        term_width = 80
    for frame in MESSAGES["banner"]:
        clear_screen()
        padding = " " * ((term_width - len(frame)) // 2)
        print(padding + color(frame, "33;1"))
        time.sleep(0.1)

def check_command(cmd):
    try:
        return subprocess.run(['command', '-v', cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
    except:
        return False

def install_binutils_termux():
    print(color(MESSAGES["install_termux"], "30;1"))
    subprocess.run(['pkg', 'update', '-y'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(['pkg', 'install', 'binutils', '-y'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def get_user_input():
    try:
        user_input = input(color(MESSAGES["select_lib"], "35;1")).strip()
        if user_input.lower() == 'q':
            print("\nExiting...")
            sys.exit(0)
        if not os.path.isfile(user_input) or not user_input.endswith(".so"):
            print(color(MESSAGES["invalid_path"], "31;1"))
            return get_user_input()
        return user_input
    except (KeyboardInterrupt, EOFError):
        print("\nExiting...")
        sys.exit(0)

def generate_symbols(lib_path, output_file='symbolsDec.txt'):
    print(color(f"{MESSAGES['extracting']} {lib_path}", "30;1"))
    try:
        with open(output_file, 'w', encoding='utf-8') as f_out:
            p1 = subprocess.Popen(['readelf', '-Ws', lib_path], stdout=subprocess.PIPE)
            p2 = subprocess.Popen(['c++filt'], stdin=p1.stdout, stdout=f_out)
            p1.stdout.close()
            p2.communicate()
    except Exception as e:
        print(color(f"Symbol extraction failed: {str(e)}", "30;1"))
        sys.exit(1)

def parse_and_generate_dump(lib_path, symbols_file='symbolsDec.txt'):
    start_time = time.time()
    classes = defaultdict(list)

    pattern = re.compile(
        r'^\s*\d+:\s+([0-9a-fA-F]{8,16})\s+\d+\s+(?:FUNC|OBJECT)\s+(?:GLOBAL|WEAK).*?\s+'
        r'((?:[a-zA-Z0-9_]+::)*[a-zA-Z0-9_~]+(?:<[^>]+>)?::[a-zA-Z0-9_~]+\([^)]*\))'
    )

    try:
        with open(symbols_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(color(f"Symbols file missing: {symbols_file}", "30;1"))
        sys.exit(1)

    print(color(f"{MESSAGES['processing']} {len(lines)} symbols", "30;1"))
    total = len(lines)
    done = 0
    method_count = 0

    for line in lines:
        match = pattern.search(line)
        if match:
            offset, full_name = match.groups()
            if offset == "00000000" or offset == "0000000000000000":
                continue
            if "::" in full_name:
                try:
                    class_path, method_with_params = full_name.rsplit("::", 1)
                    method_name = method_with_params.split('(')[0]
                    params = method_with_params[len(method_name):]
                    classes[class_path].append((method_name, params, offset))
                    method_count += 1
                except:
                    continue
        done += 1
        progress_bar(done, total)

    clean_lib_name = os.path.splitext(os.path.basename(lib_path))[0].replace('lib', '', 1)
    output_dir = os.path.dirname(os.path.abspath(lib_path))
    output_path = os.path.join(output_dir, f"{clean_lib_name}@dump")
    os.makedirs(output_path, exist_ok=True)
    print(color(f"\n{MESSAGES['output_dir_created']} {output_path}", "30;1"))

    dump_file = os.path.join(output_path, f"{clean_lib_name}.cpp")
    with open(dump_file, "w", encoding="utf-8") as out:
        for cls in sorted(classes):
            out.write(f"class {cls} {{\n")
            for method_name, params, offset in sorted(set(classes[cls])):
                formatted_offset = f"0x{int(offset, 16):x}"
                out.write(f"      {method_name}{params}; //{formatted_offset}\n")
            out.write("};\n\n")

    raw_symbols_file = os.path.join(output_path, "raw_symbols.txt")
    if os.path.exists(symbols_file):
        os.rename(symbols_file, raw_symbols_file)

    print(color(f"{MESSAGES['methods_found']} {method_count}", "30;1"))
    print(color(f"{MESSAGES['classes_found']} {len(classes)}", "30;1"))
    print(color(f"{MESSAGES['saved_to']} {dump_file}", "30;1"))
    print(color(f"{MESSAGES['time_taken']} {time.time() - start_time:.2f}s", "30;1"))

def progress_bar(current, total, width=10):
    percent = current / total
    filled = int(width * percent)
    bar = color("▰" * filled, "95") + "▱" * (width - filled)
    if current == total:
        print(f"\r[{bar}] {int(percent * 100)}%\033[K")
    else:
        print(f"\r[{bar}] {int(percent * 100)}%", end='', flush=True)

def main():
    clear_screen()
    banner()

    lib_path = get_user_input()

    if not lib_path.startswith('/'):
        print(color(MESSAGES["invalid_path"], "30;1"))
        sys.exit(1)

    storage_test = os.path.join(os.environ['HOME'], 'storage', 'shared')
    if not os.path.exists(storage_test):
        print(color(MESSAGES["storage_permission"], "30;1"))
        print(color(MESSAGES["grant_storage"], "30;1"))
        sys.exit(1)

    if not os.path.isfile(lib_path):
        print(color(f"{MESSAGES['file_not_found']} {lib_path}", "30;1"))
        sys.exit(1)

    print(color(MESSAGES["termux_detected"], "30;1"))
    if not check_command('readelf') or not check_command('c++filt'):
        print(color(MESSAGES["missing_binutils"], "30;1"))
        install_binutils_termux()

    generate_symbols(lib_path)
    parse_and_generate_dump(lib_path)

    input(color(MESSAGES["press_enter"], "36"))

if __name__ == "__main__":
    main()
