from flask import Flask, request, jsonify
from weasyprint import HTML
import datetime
import os
import base64

app = Flask(__name__)

@app.route("/", methods=["POST"])
def generate_dashboard():
    req_data = request.get_json()
    if not req_data or "stocks" not in req_data:
        return jsonify({"error": "Invalid payload"}), 400

    stocks = req_data["stocks"]
    date_str = req_data.get("date", datetime.datetime.now().strftime("%d/%m/%Y"))

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
        @page {{ size: A4 portrait; margin: 15mm; background-color: #0b0f19; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #0b0f19; color: #f3f4f6; margin: 0; padding: 0; box-sizing: border-box; }}
        *, *::before, *::after {{ box-sizing: border-box; }}
        .header {{ text-align: center; margin-bottom: 25px; border-bottom: 1px solid #1f2937; padding-bottom: 18px; }}
        .title {{ font-size: 22pt; font-weight: 800; color: #ffffff; margin: 0; letter-spacing: 1.5px; }}
        .subtitle {{ font-size: 9.5pt; color: #9ca3af; margin-top: 8px; font-weight: 500; letter-spacing: 0.5px; }}
        .card {{ background: linear-gradient(135deg, #111827 0%, #1f2937 100%); margin-bottom: 12px; border-radius: 10px; width: 100%; display: table; border-collapse: collapse; overflow: hidden; border: 1px solid #374151; }}
        .card-up {{ border-left: 6px solid #10b981; }}
        .card-down {{ border-left: 6px solid #ef4444; }}
        .row {{ display: table-row; }}
        .cell {{ display: table-cell; padding: 14px 10px; vertical-align: middle; }}
        .symbol {{ font-size: 13.5pt; font-weight: bold; width: 20%; color: #ffffff; }}
        .label {{ font-size: 7pt; color: #9ca3af; display: block; margin-bottom: 3px; text-transform: uppercase; letter-spacing: 0.5px; }}
        .value {{ font-size: 11pt; font-weight: bold; color: #f9fafb; }}
        .value-up {{ color: #34d399; }}
        .value-down {{ color: #f87171; }}
        .footer {{ margin-top: 25px; text-align: center; font-size: 8pt; color: #6b7280; letter-spacing: 0.5px; }}
    </style>
    </head>
    <body>
        <div class="header">
            <h1 class="title">USA MARKET DAILY DASHBOARD</h1>
            <div class="subtitle">{date_str} • AUTOMATED TRADING AGENT</div>
        </div>
    """

    for s in stocks:
        try:
            close_val = float(str(s['close']).replace(',', ''))
            open_val = float(str(s['open']).replace(',', ''))
            is_up = close_val >= open_val
        except:
            is_up = True

        card_class = "card-up" if is_up else "card-down"
        val_class = "value-up" if is_up else "value-down"
        trend_text = s.get('trendPrice', 'UP')

        html_content += f"""
        <div class="card {card_class}">
            <div class="row">
                <div class="cell symbol">{s['symbol']}</div>
                <div class="cell">
                    <span class="label">OPEN</span>
                    <span class="value">{s['open']}</span>
                </div>
                <div class="cell">
                    <span class="label">CLOSE</span>
                    <span class="value">{s['value'] if 'value' in s else s['close']}</span>
                </div>
                <div class="cell">
                    <span class="label">TARGET</span>
                    <span class="value {val_class}">{s['diff']}</span>
                </div>
                <div class="cell">
                    <span class="label">VOLUME ($)</span>
                    <span class="value">{s['volume']}</span>
                </div>
                <div class="cell">
                    <span class="label">TREND</span>
                    <span class="value {val_class}">{trend_text}</span>
                </div>
            </div>
        </div>
        """

    html_content += """
        <div class="footer">CONFIDENTIAL & PROPRIETARY • QUANTITATIVE DASHBOARD SYSTEM</div>
    </body>
    </html>
    """

    output_pdf = "/tmp/dashboard.pdf"
    HTML(string=html_content).write_pdf(output_pdf)

    with open(output_pdf, "rb") as pdf_file:
        encoded_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')

    return jsonify({
        "status": "success",
        "pdf_base64": encoded_pdf
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
        .value {{ font-size: 12pt; font-weight: bold; color: #E0E0E0; }}
        .value-up {{ color: #00B900; }}
        .value-down {{ color: #FF334B; }}
        .footer {{ margin-top: 30px; text-align: center; font-size: 8.5pt; color: #555555; }}
    </style>
    </head>
    <body>
        <div class="header">
            <h1 class="title">USA MARKET DAILY DASHBOARD</h1>
            <div class="subtitle">ประจำวันที่ {date_str} • Automated Agent System</div>
        </div>
    """

    for s in stocks:
        try:
            close_val = float(str(s['close']).replace(',', ''))
            open_val = float(str(s['open']).replace(',', ''))
            is_up = close_val >= open_val
        except:
            is_up = True

        card_class = "card-up" if is_up else "card-down"
        val_class = "value-up" if is_up else "value-down"
        trend_text = s.get('trendPrice', 'UP')

        html_content += f"""
        <div class="card {card_class}">
            <div class="row">
                <div class="cell symbol">{s['symbol']}</div>
                <div class="cell">
                    <span class="label">OPEN</span>
                    <span class="value">{s['open']}</span>
                </div>
                <div class="cell">
                    <span class="label">CLOSE</span>
                    <span class="value">{s['close']}</span>
                </div>
                <div class="cell">
                    <span class="label">TARGET</span>
                    <span class="value {val_class}">{s['diff']}</span>
                </div>
                <div class="cell">
                    <span class="label">VOLUME ($)</span>
                    <span class="value">{s['volume']}</span>
                </div>
                <div class="cell">
                    <span class="label">TREND</span>
                    <span class="value {val_class}">{trend_text}</span>
                </div>
            </div>
        </div>
        """

    html_content += """
        <div class="footer">Confidential & Proprietary • Automated Stock Monitoring</div>
    </body>
    </html>
    """

    output_pdf = "/tmp/dashboard.pdf"
    HTML(string=html_content).write_pdf(output_pdf)

    # อ่านไฟล์ PDF แปลงเป็น Base64 ส่งผ่าน JSON
    with open(output_pdf, "rb") as pdf_file:
        encoded_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')

    return jsonify({
        "status": "success",
        "pdf_base64": encoded_pdf
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
