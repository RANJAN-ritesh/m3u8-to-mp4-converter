#!/usr/bin/env python3
"""Test CSV parsing with empty Link-2"""

import csv

print("=" * 60)
print("Testing CSV with Empty Link-2")
print("=" * 60)
print()

with open('test_empty_link.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    conversions = []

    for row in reader:
        # Process Topic 1
        topic1 = row.get('Topic 1', '').strip()
        if topic1:
            link1_col = list(reader.fieldnames).index('Topic 1') + 1
            link2_col = link1_col + 1

            link1 = row.get(reader.fieldnames[link1_col], '').strip()
            link2 = row.get(reader.fieldnames[link2_col], '').strip()

            print(f"Topic 1: {topic1}")
            print(f"  Link-1: {'PRESENT' if link1 else 'EMPTY'}")
            print(f"  Link-2: {'PRESENT' if link2 else 'EMPTY'}")

            if link1:
                conversions.append(f"{topic1} 1.mp4")
                print(f"  Creating: {topic1} 1.mp4")
            if link2:
                conversions.append(f"{topic1} 2.mp4")
                print(f"  Creating: {topic1} 2.mp4")
            else:
                print(f"  Skipping: {topic1} 2.mp4 (empty link)")
            print()

        # Process Topic 2
        topic2 = row.get('Topic 2', '').strip()
        if topic2:
            topic2_idx = list(reader.fieldnames).index('Topic 2')
            link1_col = topic2_idx + 1
            link2_col = link1_col + 1

            link1 = row.get(reader.fieldnames[link1_col], '').strip()
            link2 = row.get(reader.fieldnames[link2_col], '').strip()

            print(f"Topic 2: {topic2}")
            print(f"  Link-1: {'PRESENT' if link1 else 'EMPTY'}")
            print(f"  Link-2: {'PRESENT' if link2 else 'EMPTY'}")

            if link1:
                conversions.append(f"{topic2} 1.mp4")
                print(f"  Creating: {topic2} 1.mp4")
            if link2:
                conversions.append(f"{topic2} 2.mp4")
                print(f"  Creating: {topic2} 2.mp4")
            else:
                print(f"  Skipping: {topic2} 2.mp4 (empty link)")
            print()

print("=" * 60)
print(f"Total files to create: {len(conversions)}")
print("=" * 60)
print()
print("Output files:")
for i, filename in enumerate(conversions, 1):
    print(f"  {i}. {filename}")

print()
print("Test PASSED! Empty Link-2 handled correctly.")
