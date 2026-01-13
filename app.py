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
            output_filename = os.path.splitext(safe_filename)[0] + '.' + target_format
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

            # --- Generate Preview Image ---
            output_filename = "preview.png"
            output_path = os.path.join(tmpdirname, output_filename)
            pyembroidery.write(emb_pattern, output_path)

            # Resize if Pillow available
            try:
                from PIL import Image
                with Image.open(output_path) as img:
                    img.thumbnail((400, 400))
                    img.save(output_path, optimize=True)
            except ImportError:
                pass
            except Exception as e:
                print(f"Resize failed: {e}")

            # Read image to base64
            with open(output_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            return jsonify({
                "image": f"data:image/png;base64,{encoded_string}",
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
