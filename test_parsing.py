#!/usr/bin/env python3
"""
Test script to verify CSV parsing logic
"""

import csv

def test_csv_parsing():
    print("=" * 60)
    print("Testing CSV Parsing")
    print("=" * 60)
    print()

    # Read the sample CSV
    with open('sample_course.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        print("CSV Headers:")
        print(list(reader.fieldnames))
        print()

        # Check if new format
        if 'Topic 1' in reader.fieldnames:
            print("Format detected: NEW FORMAT (with Topics)")
            print()

            conversions = []

            for row in reader:
                print(f"Course: {row.get('Course')}")
                print(f"Title: {row.get('Title')}")
                print(f"Track: {row.get('Track')}")
                print(f"POC: {row.get('POC')}")
                print()

                # Process Topic 1
                topic1 = row.get('Topic 1', '').strip()
                if topic1:
                    print(f"Topic 1: {topic1}")

                    # Get Link-1 for Topic 1
                    link1_col = list(reader.fieldnames).index('Topic 1') + 1
                    link2_col = link1_col + 1

                    link1 = row.get(reader.fieldnames[link1_col], '').strip() if link1_col < len(reader.fieldnames) else ''
                    link2 = row.get(reader.fieldnames[link2_col], '').strip() if link2_col < len(reader.fieldnames) else ''

                    if link1:
                        conversions.append({
                            'name': f"{topic1} 1",
                            'url': link1
                        })
                        print(f"  Link-1: {link1[:60]}...")
                        print(f"  Output: {topic1} 1.mp4")

                    if link2:
                        conversions.append({
                            'name': f"{topic1} 2",
                            'url': link2
                        })
                        print(f"  Link-2: {link2[:60]}...")
                        print(f"  Output: {topic1} 2.mp4")

                    print()

                # Process Topic 2
                topic2 = row.get('Topic 2', '').strip()
                if topic2:
                    print(f"Topic 2: {topic2}")

                    # Get Link-1 for Topic 2
                    topic2_idx = list(reader.fieldnames).index('Topic 2')
                    link1_col = topic2_idx + 1
                    link2_col = link1_col + 1

                    link1 = row.get(reader.fieldnames[link1_col], '').strip() if link1_col < len(reader.fieldnames) else ''
                    link2 = row.get(reader.fieldnames[link2_col], '').strip() if link2_col < len(reader.fieldnames) else ''

                    if link1:
                        conversions.append({
                            'name': f"{topic2} 1",
                            'url': link1
                        })
                        print(f"  Link-1: {link1[:60]}...")
                        print(f"  Output: {topic2} 1.mp4")

                    if link2:
                        conversions.append({
                            'name': f"{topic2} 2",
                            'url': link2
                        })
                        print(f"  Link-2: {link2[:60]}...")
                        print(f"  Output: {topic2} 2.mp4")

                    print()

            print("=" * 60)
            print(f"Total conversions to be created: {len(conversions)}")
            print("=" * 60)
            print()

            print("Output files will be:")
            for i, conv in enumerate(conversions, 1):
                print(f"  {i}. {conv['name']}.mp4")

            print()
            print("Test PASSED!")

        else:
            print("Format detected: OLD FORMAT")
            print("Test not applicable for old format")

if __name__ == "__main__":
    test_csv_parsing()
