import qrcode
import io
import base64
from PIL import Image


def build_upi_uri(pa: str, pn: str, am: float, tn: str = '', cu: str = 'INR') -> str:
    """Build a UPI URI (deep link) e.g., upi://pay?pa=merchant@upi&pn=Name&am=10&cu=INR&tn=note"""
    pa_enc = pa
    pn_enc = pn
    tn_enc = tn
    return f"upi://pay?pa={pa_enc}&pn={pn_enc}&am={am}&cu={cu}&tn={tn_enc}"


def generate_qr_data_uri(data: str, box_size: int = 10, border: int = 4) -> str:
    """Generate a PNG QR and return as data URI (base64)"""
    qr = qrcode.QRCode(box_size=box_size, border=border)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode('ascii')
    return f"data:image/png;base64,{b64}"


def save_qr_to_file(data: str, filepath: str, box_size: int = 10, border: int = 4) -> str:
    qr = qrcode.QRCode(box_size=box_size, border=border)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filepath)
    return filepath
