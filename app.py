#!/usr/bin/env python3
"""
Flask web server for M3U8 to MP4 conversion
"""

from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import csv
import subprocess
import threading
import time
import re
from pathlib import Path
import shutil

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
Path(app.config['OUTPUT_FOLDER']).mkdir(exist_ok=True)

conversion_status = {
    'is_running': False,
    'current': 0,
    'total': 0,
    'current_video': '',
    'completed': [],
    'failed': [],
    'progress': 0
}


def sanitize_filename(filename):
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = filename.strip('. ')
    return filename


def convert_m3u8_to_mp4(session_name, m3u8_url, output_dir, resolution=None, start_time=None, end_time=None):
    """Convert a single m3u8 URL to mp4."""
    safe_name = sanitize_filename(session_name)
    output_file = os.path.join(output_dir, f"{safe_name}.mp4")

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
        elif 'p' in resolution.lower():
            pass

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
            text=True,
            timeout=600  # 10 minute timeout per video
        )

        if result.returncode == 0 and os.path.exists(output_file):
            file_size = os.path.getsize(output_file) / (1024 * 1024)
            return True, f"{safe_name}.mp4", file_size
        else:
            print(f"Error for {safe_name}: {result.stderr}")
            return False, safe_name, 0

    except subprocess.TimeoutExpired:
        return False, session_name, 0
    except Exception as e:
        return False, session_name, 0


def process_conversions(conversions, output_dir, max_workers=3):
    """Process all conversions in background thread using explicit threading."""
    global conversion_status

    conversion_status['is_running'] = True
    conversion_status['current'] = 0
    conversion_status['total'] = len(conversions)
    conversion_status['completed'] = []  # type: ignore
    conversion_status['failed'] = []  # type: ignore
    
    status_lock = threading.Lock()
    
    def process_single(i, conv):
        global conversion_status
        with status_lock:
            conversion_status['current_video'] = conv['name']
            
        success, filename, file_size = convert_m3u8_to_mp4(
            conv['name'],
            conv['url'],
            output_dir,
            resolution=conv.get('resolution'),
            start_time=conv.get('start_time'),
            end_time=conv.get('end_time')
        )

        with status_lock:

            curr = int(conversion_status.get('current', 0)) + 1
            tot = int(conversion_status.get('total', 1))
            conversion_status['current'] = curr
            conversion_status['progress'] = int((curr / tot) * 100)
            
            if success:
                comp_list = conversion_status.get('completed', [])
                if isinstance(comp_list, list):
                    comp_list.append({
                        'name': conv['name'],
                        'filename': filename,
                        'size': f"{file_size:.2f} MB"
                    })
            else:
                fail_list = conversion_status.get('failed', [])
                if isinstance(fail_list, list):
                    fail_list.append(conv['name'])

    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_single, i, conv): conv for i, conv in enumerate(conversions, 1)}
        concurrent.futures.wait(futures)

    conversion_status['is_running'] = False
    conversion_status['progress'] = 100


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload and start conversion."""
    global conversion_status

    if conversion_status['is_running']:
        return jsonify({'error': 'Conversion already in progress'}), 400

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be a CSV'}), 400

    # Clear previous output
    if os.path.exists(app.config['OUTPUT_FOLDER']):
        shutil.rmtree(app.config['OUTPUT_FOLDER'])
    Path(app.config['OUTPUT_FOLDER']).mkdir(exist_ok=True)

    # Save uploaded file
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Parse CSV
    conversions = []
    tmp_path = None
    try:
        # Step 1: Detect and normalize delimiter if needed
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        delimiter = ','  # default
        if len(lines) >= 2:
            # Check first line (header) and second line (data)
            header = lines[0].strip()
            data_line = lines[1].strip() if len(lines) > 1 else ''

            # Count delimiters in header and data
            comma_in_header = header.count(',')
            tab_in_data = data_line.count('\t')
            comma_in_data = data_line.count(',')

            # If header has commas but data has tabs (mixed delimiter case - common when pasting from spreadsheets)
            if comma_in_header > 0 and tab_in_data > 0 and tab_in_data > comma_in_data:
                # Normalize: convert header commas to tabs
                delimiter = '\t'
                lines[0] = header.replace(',', '\t') + '\n'

                # Write normalized content to temp file
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.csv') as tmp:
                    tmp.writelines(lines)
                    tmp_path = tmp.name
                filepath = tmp_path
            # If data has more tabs than commas, use tabs
            elif tab_in_data > comma_in_data and tab_in_data > 0:
                delimiter = '\t'
            # Try CSV sniffer as fallback
            else:
                try:
                    sample = ''.join(lines[:5])
                    sniffer = csv.Sniffer()
                    delimiter = sniffer.sniff(sample).delimiter
                except:
                    delimiter = ','

        # Step 2: Read the CSV file with the detected delimiter
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=delimiter)

            # Strip whitespace from fieldnames to handle cases like " Title" or " Link"
            fieldnames = [str(x).strip() for x in reader.fieldnames] if reader.fieldnames else []
            reader.fieldnames = fieldnames

            # Check for simple format with single Topic column
            if fieldnames and 'Topic' in fieldnames and 'Link' in fieldnames and 'Topic 1' not in fieldnames:
                # Simple format: Course, Title, Topic, Link (one video per row)
                for row in reader:
                    # Strip all keys in the row dict to handle spacing
                    clean_row = {str(k).strip(): v for k, v in row.items()}
                    topic = clean_row.get('Topic', '').strip()
                    link = clean_row.get('Link', '').strip()
                    res = clean_row.get('Resolution', '').strip() or None
                    start = clean_row.get('Start Time', '').strip() or None
                    end = clean_row.get('End Time', '').strip() or None

                    if topic and link:
                        conversions.append({
                            'name': topic,
                            'url': link,
                            'resolution': res,
                            'start_time': start,
                            'end_time': end
                        })

            # Check for complex format with Topic 1, Topic 2
            elif fieldnames and 'Topic 1' in fieldnames:
                # New format: Course, Title, Track, POC, Topic 1, Link-1, Link-2, Topic 2, Link-1, Link-2
                for row in reader:
                    clean_row = {str(k).strip(): v for k, v in row.items()}
                    res = clean_row.get('Resolution', '').strip() or None
                    start = clean_row.get('Start Time', '').strip() or None
                    end = clean_row.get('End Time', '').strip() or None
                    
                    # Process Topic 1
                    topic1 = clean_row.get('Topic 1', '').strip()
                    if topic1:
                        # Get Link-1 for Topic 1 (column index after Topic 1)
                        link1_col = list(fieldnames).index('Topic 1') + 1
                        link2_col = link1_col + 1

                        link1 = row.get(reader.fieldnames[link1_col], '').strip() if link1_col < len(reader.fieldnames) else ''
                        link2 = row.get(reader.fieldnames[link2_col], '').strip() if link2_col < len(reader.fieldnames) else ''

                        if link1:
                            conversions.append({
                                'name': f"{topic1} 1",
                                'url': link1,
                                'resolution': res,
                                'start_time': start,
                                'end_time': end
                            })
                        if link2:
                            conversions.append({
                                'name': f"{topic1} 2",
                                'url': link2,
                                'resolution': res,
                                'start_time': start,
                                'end_time': end
                            })

                    # Process Topic 2
                    topic2 = clean_row.get('Topic 2', '').strip()
                    if topic2:
                        # Get Link-1 for Topic 2 (column index after Topic 2)
                        topic2_idx = list(fieldnames).index('Topic 2')
                        link1_col = topic2_idx + 1
                        link2_col = link1_col + 1

                        link1 = clean_row.get(fieldnames[link1_col], '').strip() if link1_col < len(fieldnames) else ''
                        link2 = clean_row.get(fieldnames[link2_col], '').strip() if link2_col < len(fieldnames) else ''

                        if link1:
                            conversions.append({
                                'name': f"{topic2} 1",
                                'url': link1,
                                'resolution': res,
                                'start_time': start,
                                'end_time': end
                            })
                        if link2:
                            conversions.append({
                                'name': f"{topic2} 2",
                                'url': link2,
                                'resolution': res,
                                'start_time': start,
                                'end_time': end
                            })

            # Check for old format
            elif fieldnames and 'session name' in fieldnames and 'session link' in fieldnames:
                for row in reader:
                    clean_row = {str(k).strip(): v for k, v in row.items()}
                    name = clean_row.get('session name', '').strip()
                    url = clean_row.get('session link', '').strip()
                    res = clean_row.get('Resolution', '').strip() or None
                    start = clean_row.get('Start Time', '').strip() or None
                    end = clean_row.get('End Time', '').strip() or None
                    
                    if name and url:
                        conversions.append({
                            'name': name, 'url': url,
                            'resolution': res, 'start_time': start, 'end_time': end
                        })

            else:
                # Fallback: Try using first two columns
                f.seek(0)
                reader = csv.reader(f, delimiter=delimiter)
                next(reader)  # Skip header

                for row in reader:
                    if len(row) >= 2 and row[1].strip():
                        # In fallback, try getting columns 2, 3, 4 for res, start, end if they exist
                        res = row[2].strip() if len(row) > 2 else None
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
        return jsonify({'error': f'Error reading CSV: {str(e)}'}), 400
    finally:
        # Clean up temp file if created
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass

    if not conversions:
        return jsonify({'error': 'No valid entries found in CSV'}), 400

    # Get concurrency setting from form, default to 3
    try:
        max_workers = int(request.form.get('concurrency', 3))
    except ValueError:
        max_workers = 3

    # Start conversion in background thread
    thread = threading.Thread(
        target=process_conversions,
        args=(conversions, app.config['OUTPUT_FOLDER'], max_workers)
    )
    thread.daemon = True
    thread.start()

    return jsonify({
        'message': 'Conversion started',
        'total': len(conversions)
    })


@app.route('/status')
def get_status():
    """Get current conversion status."""
    return jsonify(conversion_status)


@app.route('/download-template')
def download_template():
    """Download an example formatted CSV template."""
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['session name', 'session link', 'Resolution', 'Start Time', 'End Time'])
    writer.writerow(['Example Video', 'https://video.gumlet.io/.../main.m3u8', '1080p', '00:00:10', '00:00:15'])
    writer.writerow(['Full Local Stream', 'file://$(pwd)/local_playlist.m3u8', '', '', ''])
    
    # Needs to be a byte stream for send_file
    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8'))
    mem.seek(0)
    
    return send_file(
        mem,
        mimetype='text/csv',
        download_name='template_m3u8_converter.csv',
        as_attachment=True
    )


@app.route('/download/<filename>')
def download_file(filename):
    """Download a converted video file."""
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)

    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename
    )


@app.route('/download-all')
def download_all():
    """Create and download a zip of all converted videos."""
    import zipfile
    from io import BytesIO

    memory_file = BytesIO()

    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        output_dir = app.config['OUTPUT_FOLDER']
        for filename in os.listdir(output_dir):
            if filename.endswith('.mp4'):
                file_path = os.path.join(output_dir, filename)
                zf.write(file_path, filename)

    memory_file.seek(0)

    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='converted_videos.zip'
    )


if __name__ == '__main__':
    port = 8080
    print("\n" + "=" * 60)
    print("M3U8 to MP4 Converter Server")
    print("=" * 60)
    print(f"\nServer starting at: http://localhost:{port}")
    print("Upload your CSV file and start converting!")
    print("\nPress CTRL+C to stop the server\n")

    app.run(debug=True, host='0.0.0.0', port=port)
