import os
import time
import heapq
from collections import Counter
from tkinter import Tk, filedialog

# ---------------- Huffman Node ----------------
class Node:
    def __init__(self, char=None, count=0, left=None, right=None):
        self.char = char
        self.count = count
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.count < other.count

# ---------------- Utility ----------------
def get_file_size(filename):
    return os.path.getsize(filename)

def build_huffman_tree(freq):
    heap = [Node(char=char, count=count) for char, count in freq.items()]
    heapq.heapify(heap)
    if len(heap) == 1:
        only_node = heapq.heappop(heap)
        return Node(count=only_node.count, left=only_node)
    while len(heap) > 1:
        a = heapq.heappop(heap)
        b = heapq.heappop(heap)
        parent = Node(count=a.count + b.count, left=a, right=b)
        heapq.heappush(heap, parent)
    return heap[0]

def generate_codes(root, value="", code_map=None):
    if code_map is None:
        code_map = {}
    if root.left is None and root.right is None:
        code_map[root.char] = value
        return code_map
    if root.left:
        generate_codes(root.left, value + "0", code_map)
    if root.right:
        generate_codes(root.right, value + "1", code_map)
    return code_map

def generate_header(code_map, padding):
    header = bytearray()
    header.append(len(code_map) - 1)
    for char, code in code_map.items():
        header.append(char)
        header.append(len(code))
        header.extend(code.encode())  # storing ASCII "0"/"1"
    header.append(padding)
    return header

# ---------------- Compression ----------------
def compress_file(input_path, output_path):
    filesize = get_file_size(input_path)

    with open(input_path, "rb") as f:
        data = f.read()
    freq = Counter(data)

    root = build_huffman_tree(freq)
    code_map = generate_codes(root)

    predfilesize_bits = sum(len(code_map[byte]) * count for byte, count in freq.items())
    padding = (8 - (predfilesize_bits % 8)) % 8

    header = generate_header(code_map, padding)

    with open(input_path, "rb") as fin, open(output_path, "wb") as fout:
        fout.write(header)
        bit_str = ""
        while (byte := fin.read(1)):
            bit_str += code_map[byte[0]]
            while len(bit_str) >= 8:
                fout.write(int(bit_str[:8], 2).to_bytes(1, 'big'))
                bit_str = bit_str[8:]
        if bit_str:
            bit_str += "0" * padding
            fout.write(int(bit_str, 2).to_bytes(len(bit_str) // 8, 'big'))

    print(f"Original File: {filesize} bytes")
    print(f"Compressed File Size (without header): {(predfilesize_bits + 7) // 8} bytes")
    print(f"Padding size: {padding}")
    print(f"Compressed file saved to: {output_path}")

# ---------------- File Selection ----------------
def main():
    root_tk = Tk()
    root_tk.withdraw()  # hide main tkinter window

    # Select file to compress
    input_path = filedialog.askopenfilename(title="Select a file to compress")
    if not input_path:
        print("No file selected. Exiting...")
        return

    # Select save location
    output_path = filedialog.asksaveasfilename(
        title="Save compressed file as",
        defaultextension=".abiz",
        filetypes=[("Huffman Compressed", "*.abiz")]
    )
    if not output_path:
        print("No save location selected. Exiting...")
        return

    start = time.time()
    compress_file(input_path, output_path)
    end = time.time()
    print(f"Compression completed in {end - start:.4f} seconds")

if __name__ == "__main__":
    main()
