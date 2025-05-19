from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import cv2
import numpy as np
import requests

app = Flask(__name__)

def leer_qr_desde_pixmap(pix):
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if pix.n == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img)
    return data.strip()

@app.route('/extraer', methods=['GET'])
def extraer_qr():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Falta el parámetro url'}), 400
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        with open("temp.pdf", "wb") as f:
            f.write(r.content)

        doc = fitz.open("temp.pdf")
        pagina = doc.load_page(0)
        pix = pagina.get_pixmap(dpi=150)
        qr = leer_qr_desde_pixmap(pix)
        return jsonify({'qr': qr})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
