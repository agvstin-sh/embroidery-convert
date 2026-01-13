# Embroidery Converter 🧵

A modern, web-based tool to convert embroidery files between different machine formats (DST, PES, JEF, EXP, etc.) and visualize them instantly.

## Features

- **Multi-format Support**: Convert between popular formats like `.dst`, `.pes`, `.jef`, `.exp`, `.vp3`, `.xxx`.
- **Instant Preview**: visualize your designs before converting.
- **Detailed Stats**: View stitch count, dimensions (mm/in), color count, and color changes.
- **Modern UI**: Drag & drop interface with a premium dark mode design.
- **Internationalization**: Full support for English and Spanish.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Start the server**:
    ```bash
    python app.py
    ```

2.  **Open your browser**:
    Navigate to `http://127.0.0.1:5000`

## Deployment

### Using Docker (Recommended)

1.  **Build the image**:
    ```bash
    docker build -t embroidery-app .
    ```

2.  **Run the container**:
    ```bash
    docker run -p 5000:5000 embroidery-app
    ```

## Technologies

- **Backend**: Flask (Python)
- **Embroidery Processing**: `pyembroidery`
- **Image Processing**: Pillow (PIL)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript

## License

[MIT License](LICENSE)
