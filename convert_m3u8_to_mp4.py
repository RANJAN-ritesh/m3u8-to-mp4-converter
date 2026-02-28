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
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = filename.replace(' ', '_')
    filename = filename.strip('. ')
    return filename


import concurrent.futures
import threading

def convert_m3u8_to_mp4(session_name, m3u8_url, output_dir='output', resolution=None, start_time=None, end_time=None):
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    safe_name = sanitize_filename(session_name)
    output_file = os.path.join(output_dir, f"{safe_name}.mp4")

    if os.path.exists(output_file):
        return True, "Already exists"

    cmd = ['ffmpeg']

    if start_time:
        cmd.extend(['-ss', str(start_time)])
    if end_time:
        if start_time:
            try:
                def to_sec(t):
                    parts = list(map(float, str(t).split(':')))
                    if len(parts) == 3: return parts[0]*3600 + parts[1]*60 + parts[2]
                    elif len(parts) == 2: return parts[0]*60 + parts[1]
                    return parts[0]
                dur = to_sec(end_time) - to_sec(start_time)
                if dur > 0:
                    cmd.extend(['-t', str(dur)])
            except:
                pass
        else:
            cmd.extend(['-to', str(end_time)])

    cmd.extend(['-i', m3u8_url])

    if resolution and resolution.lower() != 'highest':
        if resolution.lower() == 'lowest':
            cmd.extend(['-map', 'p:0'])

    cmd.extend([
        '-c', 'copy',
        '-bsf:a', 'aac_adtstoasc',
        '-y',
        output_file
    ])

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode == 0:
            return True, None
        else:
            return False, result.stderr[-500:]

    except Exception as e:
        return False, str(e)


def process_csv(csv_file, output_dir='output', max_workers=3, default_resolution=None):
    """
    Process CSV file and convert all m3u8 links to mp4.
    """
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        sys.exit(1)

    print(f"📋 Reading CSV file: {csv_file}")

    conversions = []

    try:
        # Try to dynamically detect delimiter based on first few lines
        with open(csv_file, 'r', encoding='utf-8') as f:
            sample = f.read(1024)
            f.seek(0)
            try:
                delimiter = csv.Sniffer().sniff(sample).delimiter
            except:
                delimiter = ',' if ',' in sample else '\t'
                
            reader = csv.DictReader(f, delimiter=delimiter)
            
            # Strip whitespace from fieldnames to handle cases like " Title" or " Link"
            fieldnames = [str(x).strip() for x in reader.fieldnames] if reader.fieldnames else []
            reader.fieldnames = fieldnames

            if 'session name' in fieldnames and 'session link' in fieldnames:
                for row in reader:
                    # Strip all keys in the row dict to handle spacing
                    clean_row = {str(k).strip(): v for k, v in row.items()}
                    name = clean_row.get('session name', '').strip()
                    url = clean_row.get('session link', '').strip()
                    res = clean_row.get('Resolution', '')
                    res = res.strip() if res else default_resolution
                    start = clean_row.get('Start Time', '')
                    start = start.strip() if start else None
                    end = clean_row.get('End Time', '')
                    end = end.strip() if end else None
                    if name and url:
                        conversions.append({'name': name, 'url': url, 'resolution': res, 'start_time': start, 'end_time': end})
            elif 'Topic' in fieldnames and 'Link' in fieldnames:
                for row in reader:
                    # Strip all keys in the row dict to handle spacing
                    clean_row = {str(k).strip(): v for k, v in row.items()}
                    name = clean_row.get('Topic', '').strip()
                    url = clean_row.get('Link', '').strip()
                    res = clean_row.get('Resolution', '')
                    res = res.strip() if res else default_resolution
                    start = clean_row.get('Start Time', '')
                    start = start.strip() if start else None
                    end = clean_row.get('End Time', '')
                    end = end.strip() if end else None
                    if name and url:
                        conversions.append({'name': name, 'url': url, 'resolution': res, 'start_time': start, 'end_time': end})
            else:
                # Fallback: Try using first columns
                f.seek(0)
                reader = csv.reader(f, delimiter=delimiter)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 2 and row[1].strip():
                        res = row[2].strip() if len(row) > 2 else default_resolution
                        start = row[3].strip() if len(row) > 3 else None
                        end = row[4].strip() if len(row) > 4 else None
                        conversions.append({
                            'name': row[0].strip(),
                            'url': row[1].strip(),
                            'resolution': res,
                            'start_time': start,
                            'end_time': end
                        })

    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        sys.exit(1)

    if not conversions:
        print("No valid entries found in CSV file")
        sys.exit(1)

    print(f"\nFound {len(conversions)} video(s) to convert using {max_workers} concurrent workers")
    print(f"Output directory: {output_dir}")
    print("=" * 60)

    counters = {'successful': 0, 'failed': 0, 'skipped': 0}
    
    lock = threading.Lock()
    
    def worker(conv, index, total):
        print(f"[{index}/{total}] Starting: {conv['name']}")
        
        success, error_msg = convert_m3u8_to_mp4(
            conv['name'], 
            conv['url'], 
            output_dir,
            resolution=conv.get('resolution'),
            start_time=conv.get('start_time'),
            end_time=conv.get('end_time')
        )
        
        with lock:
            if success:
                if error_msg == "Already exists":
                    print(f"[{index}/{total}] Skipped {conv['name']} (Already exists)")
                    counters['skipped'] += 1
                else:
                    print(f"[{index}/{total}] Success: {conv['name']}")
                    counters['successful'] += 1
            else:
                print(f"[{index}/{total}] Failed: {conv['name']}\n   Error: {error_msg}")
                counters['failed'] += 1

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(worker, conv, i, len(conversions)): conv for i, conv in enumerate(conversions, 1)}
        concurrent.futures.wait(futures)

    # Summary
    print("\n" + "=" * 60)
    print(f"Conversion complete!")
    print(f"   Successful: {counters['successful']}")
    print(f"   Skipped (Exists): {counters['skipped']}")
    print(f"   Failed: {counters['failed']}")
    print(f"   Total: {len(conversions)}")
    print(f"\nOutput files saved in: {os.path.abspath(output_dir)}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="M3U8 to MP4 Converter")
    parser.add_argument("csv_file", help="Path to the input CSV file")
    parser.add_argument("output_dir", nargs="?", default="output", help="Directory to save output files")
    parser.add_argument("--workers", type=int, default=3, help="Number of concurrent downloads (default: 3)")
    parser.add_argument("--resolution", help="Resolution to use (e.g. '1080p', 'Highest', 'Lowest')")

    args = parser.parse_args()
    process_csv(args.csv_file, args.output_dir, max_workers=args.workers, default_resolution=args.resolution)
