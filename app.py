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

# Ensure folders exist
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
Path(app.config['OUTPUT_FOLDER']).mkdir(exist_ok=True)

# Global variable to track conversion status
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
    """Remove or replace characters that are invalid in filenames."""
    # Remove only truly invalid characters, keep spaces
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = filename.strip('. ')
    return filename


def convert_m3u8_to_mp4(session_name, m3u8_url, output_dir):
    """Convert a single m3u8 URL to mp4."""
    safe_name = sanitize_filename(session_name)
    output_file = os.path.join(output_dir, f"{safe_name}.mp4")

    cmd = [
        'ffmpeg',
        '-i', m3u8_url,
        '-c', 'copy',
        '-bsf:a', 'aac_adtstoasc',
        '-y',
        output_file
    ]

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
            return False, safe_name, 0

    except subprocess.TimeoutExpired:
        return False, session_name, 0
    except Exception as e:
        return False, session_name, 0


def process_conversions(conversions, output_dir):
    """Process all conversions in background thread."""
    global conversion_status

    conversion_status['is_running'] = True
    conversion_status['current'] = 0
    conversion_status['total'] = len(conversions)
    conversion_status['completed'] = []
    conversion_status['failed'] = []

    for i, conv in enumerate(conversions, 1):
        conversion_status['current'] = i
        conversion_status['current_video'] = conv['name']
        conversion_status['progress'] = int((i / len(conversions)) * 100)

        success, filename, file_size = convert_m3u8_to_mp4(
            conv['name'],
            conv['url'],
            output_dir
        )

        if success:
            conversion_status['completed'].append({
                'name': conv['name'],
                'filename': filename,
                'size': f"{file_size:.2f} MB"
            })
        else:
            conversion_status['failed'].append(conv['name'])

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

            # Check for simple format with single Topic column
            if 'Topic' in reader.fieldnames and 'Link' in reader.fieldnames and 'Topic 1' not in reader.fieldnames:
                # Simple format: Course, Title, Topic, Link (one video per row)
                for row in reader:
                    topic = row.get('Topic', '').strip()
                    link = row.get('Link', '').strip()

                    if topic and link:
                        conversions.append({
                            'name': topic,
                            'url': link
                        })

            # Check for complex format with Topic 1, Topic 2
            elif 'Topic 1' in reader.fieldnames:
                # New format: Course, Title, Track, POC, Topic 1, Link-1, Link-2, Topic 2, Link-1, Link-2
                for row in reader:
                    # Process Topic 1
                    topic1 = row.get('Topic 1', '').strip()
                    if topic1:
                        # Get Link-1 for Topic 1 (column index after Topic 1)
                        link1_col = list(reader.fieldnames).index('Topic 1') + 1
                        link2_col = link1_col + 1

                        link1 = row.get(reader.fieldnames[link1_col], '').strip() if link1_col < len(reader.fieldnames) else ''
                        link2 = row.get(reader.fieldnames[link2_col], '').strip() if link2_col < len(reader.fieldnames) else ''

                        if link1:
                            conversions.append({
                                'name': f"{topic1} 1",
                                'url': link1
                            })
                        if link2:
                            conversions.append({
                                'name': f"{topic1} 2",
                                'url': link2
                            })

                    # Process Topic 2
                    topic2 = row.get('Topic 2', '').strip()
                    if topic2:
                        # Get Link-1 for Topic 2 (column index after Topic 2)
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
                        if link2:
                            conversions.append({
                                'name': f"{topic2} 2",
                                'url': link2
                            })

            # Check for old format
            elif 'session name' in reader.fieldnames and 'session link' in reader.fieldnames:
                for row in reader:
                    name = row.get('session name', '').strip()
                    url = row.get('session link', '').strip()
                    if name and url:
                        conversions.append({'name': name, 'url': url})

            else:
                # Fallback: Try using first two columns
                f.seek(0)
                reader = csv.reader(f, delimiter=delimiter)
                next(reader)  # Skip header

                for row in reader:
                    if len(row) >= 2 and row[1].strip():
                        conversions.append({
                            'name': row[0].strip(),
                            'url': row[1].strip()
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

    # Start conversion in background thread
    thread = threading.Thread(
        target=process_conversions,
        args=(conversions, app.config['OUTPUT_FOLDER'])
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
    print("🎥 M3U8 to MP4 Converter Server")
    print("=" * 60)
    print(f"\n🌐 Server starting at: http://localhost:{port}")
    print("📂 Upload your CSV file and start converting!")
    print("\n⚠️  Press CTRL+C to stop the server\n")

    app.run(debug=True, host='0.0.0.0', port=port)
