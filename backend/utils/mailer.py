"""Email alert utility using Gmail SMTP."""
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SENDER = os.getenv("EMAIL_SENDER", "")
PASSWORD = os.getenv("EMAIL_PASSWORD", "")
RECEIVER = os.getenv("EMAIL_RECEIVER", SENDER)

FRONTEND_URL = "https://pricehunter-pied.vercel.app"


def _format_price(price: float, currency: str) -> str:
    if currency == "ARS":
        return f"${price:,.0f}".replace(",", ".")
    return f"USD {price:.2f}"


def send_price_alert(
    title: str,
    source: str,
    product_id: int,
    current_price: float,
    original_price: float,
    drop_pct: float,
    currency: str,
) -> bool:
    """Send a price drop email alert. Returns True if sent successfully."""
    if not SENDER or not PASSWORD:
        print("[mailer] EMAIL_SENDER/EMAIL_PASSWORD not configured, skipping")
        return False

    source_label = "MercadoLibre" if source == "mercadolibre" else "Amazon"
    product_url = f"{FRONTEND_URL}/product/{product_id}"
    current_fmt = _format_price(current_price, currency)
    original_fmt = _format_price(original_price, currency)

    subject = f"PriceHunter 🔔 {title[:50]} bajó {drop_pct:.1f}%"

    html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#0f172a;font-family:sans-serif;">
  <div style="max-width:520px;margin:32px auto;background:#1e293b;border-radius:16px;overflow:hidden;border:1px solid #334155;">

    <!-- Header -->
    <div style="background:#3b82f6;padding:20px 28px;">
      <h1 style="margin:0;color:#fff;font-size:20px;">📉 Alerta de precio</h1>
      <p style="margin:4px 0 0;color:#bfdbfe;font-size:13px;">PriceHunter detectó una bajada en tu watchlist</p>
    </div>

    <!-- Content -->
    <div style="padding:24px 28px;">
      <p style="color:#94a3b8;font-size:12px;margin:0 0 6px;text-transform:uppercase;letter-spacing:.05em;">{source_label}</p>
      <p style="color:#f1f5f9;font-size:16px;font-weight:600;margin:0 0 20px;line-height:1.4;">{title}</p>

      <!-- Price comparison -->
      <div style="display:flex;gap:12px;margin-bottom:20px;">
        <div style="flex:1;background:#0f172a;border-radius:10px;padding:14px;text-align:center;">
          <p style="color:#64748b;font-size:11px;margin:0 0 4px;text-transform:uppercase;">Precio anterior</p>
          <p style="color:#94a3b8;font-size:18px;font-weight:700;margin:0;text-decoration:line-through;">{original_fmt}</p>
        </div>
        <div style="flex:1;background:#064e3b;border-radius:10px;padding:14px;text-align:center;border:1px solid #10b981;">
          <p style="color:#6ee7b7;font-size:11px;margin:0 0 4px;text-transform:uppercase;">Precio actual</p>
          <p style="color:#10b981;font-size:22px;font-weight:800;margin:0;">{current_fmt}</p>
        </div>
      </div>

      <!-- Drop badge -->
      <div style="background:#14532d;border:1px solid #16a34a;border-radius:8px;padding:10px 16px;margin-bottom:24px;text-align:center;">
        <span style="color:#4ade80;font-size:18px;font-weight:800;">▼ {drop_pct:.1f}% de bajada</span>
      </div>

      <!-- CTA -->
      <a href="{product_url}" style="display:block;background:#3b82f6;color:#fff;text-decoration:none;text-align:center;padding:14px;border-radius:10px;font-weight:700;font-size:15px;">
        Ver producto →
      </a>
    </div>

    <!-- Footer -->
    <div style="padding:16px 28px;border-top:1px solid #334155;">
      <p style="color:#475569;font-size:11px;margin:0;text-align:center;">
        Recibiste este correo porque tenés este producto en tu
        <a href="{FRONTEND_URL}/watchlist" style="color:#60a5fa;text-decoration:none;">watchlist de PriceHunter</a>.
      </p>
    </div>
  </div>
</body>
</html>
"""

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SENDER
        msg["To"] = RECEIVER
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER, PASSWORD)
            server.sendmail(SENDER, RECEIVER, msg.as_string())

        print(f"[mailer] Alert sent for product {product_id} ({drop_pct:.1f}% drop)")
        return True
    except Exception as e:
        print(f"[mailer] Failed to send email: {e}")
        return False
