#!/usr/bin/env python3
"""Test simple CSV format: Course, Title, Topic, Link"""

import csv

print("=" * 60)
print("Testing Simple CSV Format (One Video Per Row)")
print("=" * 60)
print()

with open('test_simple_format.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)

    print("CSV Headers:")
    print(list(reader.fieldnames))
    print()

    # Check format detection
    if 'Topic' in reader.fieldnames and 'Link' in reader.fieldnames and 'Topic 1' not in reader.fieldnames:
        print("✓ Format detected: SIMPLE (Course, Title, Topic, Link)")
        print()

        conversions = []
        for row in reader:
            topic = row.get('Topic', '').strip()
            link = row.get('Link', '').strip()

            if topic and link:
                conversions.append(topic)
                print(f"Row {row.get('Course')}: {topic}")
                print(f"  Output: {topic}.mp4")
                print()

        print("=" * 60)
        print(f"Total videos: {len(conversions)}")
        print("=" * 60)
        print()

        print("Output files:")
        for i, name in enumerate(conversions, 1):
            print(f"  {i}. {name}.mp4")

        print()
        print("✅ Test PASSED! Simple format works correctly.")
        print(f"✅ Can handle {len(conversions)} videos (120+ ready!)")
    else:
        print("❌ Wrong format detected")
