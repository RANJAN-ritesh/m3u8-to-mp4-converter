#!/usr/bin/env python3
"""Test CSV parsing WITHOUT POC column"""

import csv

print("=" * 60)
print("Testing CSV WITHOUT POC Column")
print("=" * 60)
print()

with open('test_no_poc.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)

    print("CSV Headers:")
    print(list(reader.fieldnames))
    print()

    conversions = []

    for row in reader:
        print(f"Course: {row.get('Course')}")
        print(f"Title: {row.get('Title')}")
        print(f"Track: {row.get('Track')}")
        print(f"POC: {row.get('POC', 'NOT PRESENT')}")
        print()

        # Process Topic 1
        topic1 = row.get('Topic 1', '').strip()
        if topic1:
            print(f"Topic 1: {topic1}")

            # Get Link-1 for Topic 1 (column index after Topic 1)
            link1_col = list(reader.fieldnames).index('Topic 1') + 1
            link2_col = link1_col + 1

            print(f"  Link-1 column index: {link1_col}")
            print(f"  Link-2 column index: {link2_col}")
            print(f"  Link-1 column name: {reader.fieldnames[link1_col]}")
            print(f"  Link-2 column name: {reader.fieldnames[link2_col]}")

            link1 = row.get(reader.fieldnames[link1_col], '').strip()
            link2 = row.get(reader.fieldnames[link2_col], '').strip()

            if link1:
                conversions.append(f"{topic1} 1.mp4")
                print(f"  ✓ Creating: {topic1} 1.mp4")
            if link2:
                conversions.append(f"{topic1} 2.mp4")
                print(f"  ✓ Creating: {topic1} 2.mp4")
            print()

        # Process Topic 2
        topic2 = row.get('Topic 2', '').strip()
        if topic2:
            print(f"Topic 2: {topic2}")

            topic2_idx = list(reader.fieldnames).index('Topic 2')
            link1_col = topic2_idx + 1
            link2_col = link1_col + 1

            print(f"  Link-1 column index: {link1_col}")
            print(f"  Link-2 column index: {link2_col}")
            print(f"  Link-1 column name: {reader.fieldnames[link1_col]}")
            print(f"  Link-2 column name: {reader.fieldnames[link2_col]}")

            link1 = row.get(reader.fieldnames[link1_col], '').strip()
            link2 = row.get(reader.fieldnames[link2_col], '').strip()

            if link1:
                conversions.append(f"{topic2} 1.mp4")
                print(f"  ✓ Creating: {topic2} 1.mp4")
            if link2:
                conversions.append(f"{topic2} 2.mp4")
                print(f"  ✓ Creating: {topic2} 2.mp4")
            print()

print("=" * 60)
print(f"Total files to create: {len(conversions)}")
print("=" * 60)
print()
print("Output files:")
for i, filename in enumerate(conversions, 1):
    print(f"  {i}. {filename}")

print()
if len(conversions) == 4:
    print("✅ Test PASSED! Format WITHOUT POC works correctly.")
else:
    print("❌ Test FAILED!")
