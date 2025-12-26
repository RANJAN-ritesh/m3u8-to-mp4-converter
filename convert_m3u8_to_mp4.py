#!/usr/bin/env python3
"""
M3U8 to MP4 Converter
Converts multiple m3u8 video links to mp4 format from a CSV file.
"""

import csv
import subprocess
import os
import sys
from pathlib import Path
import re


def sanitize_filename(filename):
    """Remove or replace characters that are invalid in filenames."""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    return filename


def convert_m3u8_to_mp4(session_name, m3u8_url, output_dir='output'):
    """
    Convert a single m3u8 URL to mp4 using ffmpeg.

    Args:
        session_name: Name for the output file
        m3u8_url: URL of the m3u8 playlist
        output_dir: Directory to save the output files

    Returns:
        bool: True if successful, False otherwise
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Sanitize the session name for use as filename
    safe_name = sanitize_filename(session_name)
    output_file = os.path.join(output_dir, f"{safe_name}.mp4")

    # Check if file already exists
    if os.path.exists(output_file):
        print(f"⚠️  File already exists: {output_file}")
        user_input = input("Overwrite? (y/n): ").lower()
        if user_input != 'y':
            print(f"⏭️  Skipping {session_name}")
            return True

    print(f"\n🔄 Converting: {session_name}")
    print(f"   Source: {m3u8_url}")
    print(f"   Output: {output_file}")

    # ffmpeg command
    # -i: input URL
    # -c copy: copy codec (no re-encoding, faster)
    # -bsf:a aac_adtstoasc: fix AAC bitstream
    # -y: overwrite output file
    cmd = [
        'ffmpeg',
        '-i', m3u8_url,
        '-c', 'copy',
        '-bsf:a', 'aac_adtstoasc',
        '-y',
        output_file
    ]

    try:
        # Run ffmpeg with output suppressed (use stderr=subprocess.PIPE to see errors)
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode == 0:
            file_size = os.path.getsize(output_file) / (1024 * 1024)  # Size in MB
            print(f"✅ Success! File size: {file_size:.2f} MB")
            return True
        else:
            print(f"❌ Error converting {session_name}")
            print(f"   Error: {result.stderr[-500:]}")  # Print last 500 chars of error
            return False

    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return False


def process_csv(csv_file, output_dir='output'):
    """
    Process CSV file and convert all m3u8 links to mp4.

    Args:
        csv_file: Path to CSV file
        output_dir: Directory to save output files
    """
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        sys.exit(1)

    print(f"📋 Reading CSV file: {csv_file}")

    conversions = []

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            # Use csv.DictReader to handle header row
            reader = csv.DictReader(f)

            # Check if required columns exist
            if 'session name' not in reader.fieldnames or 'session link' not in reader.fieldnames:
                # Try alternative column names
                if len(reader.fieldnames) >= 2:
                    print(f"⚠️  Expected columns 'session name' and 'session link'")
                    print(f"   Found columns: {reader.fieldnames}")
                    print(f"   Using first two columns as name and link")

                    # Reset file pointer
                    f.seek(0)
                    reader = csv.reader(f)
                    next(reader)  # Skip header

                    for row in reader:
                        if len(row) >= 2 and row[1].strip():
                            conversions.append({
                                'name': row[0].strip(),
                                'url': row[1].strip()
                            })
                else:
                    print(f"❌ Invalid CSV format. Expected at least 2 columns.")
                    sys.exit(1)
            else:
                for row in reader:
                    name = row.get('session name', '').strip()
                    url = row.get('session link', '').strip()

                    if name and url:
                        conversions.append({'name': name, 'url': url})

    except Exception as e:
        print(f"❌ Error reading CSV file: {str(e)}")
        sys.exit(1)

    if not conversions:
        print("❌ No valid entries found in CSV file")
        sys.exit(1)

    print(f"\n📊 Found {len(conversions)} video(s) to convert")
    print(f"💾 Output directory: {output_dir}")
    print("=" * 60)

    # Process each conversion
    successful = 0
    failed = 0

    for i, conv in enumerate(conversions, 1):
        print(f"\n[{i}/{len(conversions)}] ", end='')

        if convert_m3u8_to_mp4(conv['name'], conv['url'], output_dir):
            successful += 1
        else:
            failed += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"✨ Conversion complete!")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print(f"   Total: {len(conversions)}")
    print(f"\n📁 Output files saved in: {os.path.abspath(output_dir)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_m3u8_to_mp4.py <csv_file> [output_directory]")
        print("\nExample:")
        print("  python convert_m3u8_to_mp4.py sessions.csv")
        print("  python convert_m3u8_to_mp4.py sessions.csv ./videos")
        sys.exit(1)

    csv_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'output'

    process_csv(csv_file, output_dir)
