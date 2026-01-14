import os
import pyembroidery
import io
from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static', static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/convert', methods=['POST'])
def convert_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    target_format = request.form.get('format', '').lower()

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not target_format:
        return jsonify({'error': 'No target format specified'}), 400

    try:
        # Read the uploaded file
        original_ext = os.path.splitext(file.filename)[1].lower()
        if not original_ext:
            return jsonify({'error': 'File has no extension'}), 400
            
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdirname:
            safe_filename = secure_filename(file.filename)
            input_path = os.path.join(tmpdirname, safe_filename)
            file.save(input_path)
            
            # Read pattern
            try:
                emb_pattern = pyembroidery.read(input_path)
            except Exception as e:
                return jsonify({'error': f'Failed to read file: {str(e)}'}), 400
            
            if emb_pattern is None:
                 return jsonify({'error': 'Could not parse embroidery file'}), 400

            # Output path
            output_filename = os.path.splitext(safe_filename)[0] + '.' + target_format.upper()
            output_path = os.path.join(tmpdirname, output_filename)
            
            # Write pattern
            try:
                pyembroidery.write(emb_pattern, output_path)
            except Exception as e:
                 return jsonify({'error': f'Failed to write file: {str(e)}'}), 500

            # Read into memory to allow temp dir cleanup
            return_data = io.BytesIO()
            with open(output_path, 'rb') as f:
                return_data.write(f.read())
            return_data.seek(0)

            # Send back to user
            return send_file(
                return_data, 
                as_attachment=True, 
                download_name=output_filename,
                mimetype='application/octet-stream'
            )

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/preview', methods=['POST'])
def preview_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        import tempfile
        import base64
        
        with tempfile.TemporaryDirectory() as tmpdirname:
            safe_filename = secure_filename(file.filename)
            input_path = os.path.join(tmpdirname, safe_filename)
            file.save(input_path)
            
            try:
                emb_pattern = pyembroidery.read(input_path)
            except Exception as e:
                return jsonify({'error': f'Failed to read file: {str(e)}'}), 400

            if emb_pattern is None:
                 return jsonify({'error': 'Could not parse embroidery file'}), 400

            # --- Extract Metadata ---
            stitch_count = emb_pattern.count_stitches()
            bounds = emb_pattern.bounds()  # (min_x, min_y, max_x, max_y)
            
            # Dimensions in mm (1 unit = 0.1mm)
            width_mm = 0
            height_mm = 0
            if bounds:
                width_mm = (bounds[2] - bounds[0]) / 10.0
                height_mm = (bounds[3] - bounds[1]) / 10.0
            
            color_count = len(emb_pattern.threadlist)
            # count_color_changes is not always reliable in all versions/formats, 
            # but usually reliable enough or use len(threadlist) as proxy for "colors used"
            # let's try to get color changes if method exists, else imply from threadlist
            # Actually pyembroidery EmbPattern has count_color_changes()
            try:
                change_count = emb_pattern.count_color_changes()
            except:
                change_count = max(0, color_count - 1)

            # --- Generate Preview Data (Client-side rendering) ---
            # Instead of generating an image server-side (slow), we send the stitch data
            # to the client to render on a canvas (fast).
            
            pattern_data = []
            
            # Iterate through blocks (colors)
            for file_thread in emb_pattern.threadlist:
                # Find stitches for this thread
                # Note: pyembroidery structure can be complex, iterating blocks is safer if available
                pass

            # Alternative: Iterate stitches and group by color change
            # This is more manual but reliable across formats
            current_block = []
            current_color_idx = 0
            
            # Get color hex codes
            colors = []
            print(f"Debug: Threadlist size: {len(emb_pattern.threadlist)}")
            for i, t in enumerate(emb_pattern.threadlist):
                try:
                    vals = t.hex_color()
                    print(f"Debug: Thread {i} color: {vals}")
                    # hex_color() already returns string with # usually or just hex string
                    # let's be safe. Output of debug script was #ff0000 so it includes #
                    colors.append(vals)
                except Exception as e:
                    print(f"Debug: Thread {i} failed to get hex: {e}")
                    colors.append('#000000')
                
            # If no colors defined (some formats), provide defaults
            # Use standard Tajima 12-color cycle convention
            if not colors:
                 print("Debug: No colors found, using Tajima standard palette")
                 colors = [
                    "#0000FF", # 1. Blue
                    "#00FF00", # 2. Green
                    "#FF0000", # 3. Red
                    "#FFFF00", # 4. Yellow
                    "#FF00FF", # 5. Magenta
                    "#00FFFF", # 6. Cyan
                    "#FFA500", # 7. Orange
                    "#800080", # 8. Purple
                    "#FFC0CB", # 9. Pink
                    "#A52A2A", # 10. Brown
                    "#D3D3D3", # 11. Light Grey
                    "#000000"  # 12. Black
                 ]

            # Normalized stitch iteration
            stitches = emb_pattern.stitches
            
            current_color_index = 0
            block_stitches = []
            
            for stitch in stitches:
                # pyembroidery stitches are tuples (x, y, flags)
                x, y, flags = stitch
                
                # Check for color change or end
                # Use getattr to be safe with different pyembroidery versions
                COLOR_CHANGE = getattr(pyembroidery, 'COLOR_CHANGE', 5)
                END = getattr(pyembroidery, 'END', 6) # 6 is common for END? or maybe it's missing.
                # Actually, usually getting NORMAL=0 is safe.
                
                if flags == COLOR_CHANGE:
                    # Save current block
                    if block_stitches:
                        color_hex = colors[current_color_index % len(colors)]
                        pattern_data.append({
                            "color": color_hex,
                            "stitches": block_stitches
                        })
                    
                    # Start new block
                    block_stitches = []
                    current_color_index += 1
                    continue
                
                # If END exists and matches, break. Or if it's high value?
                # Just checking safe match.
                if flags == END:
                    break
                    
                # JUMP = 1, TRIM = 2. Normal = 0.
                # If pyembroidery.NORMAL doesn't exist, assume 0.
                if flags == 0:
                    block_stitches.append([x, y])
                
            # Append final block
            if block_stitches:
                color_hex = colors[current_color_index % len(colors)]
                pattern_data.append({
                    "color": color_hex,
                    "stitches": block_stitches
                })

            return jsonify({
                "mode": "vector", # Signal frontend to use canvas
                "pattern": pattern_data,
                "bounds": bounds,
                "stats": {
                    "stitches": stitch_count,
                    "width": width_mm,
                    "height": height_mm,
                    "colors": color_count,
                    "changes": change_count
                }
            })
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=False, port=5000)
