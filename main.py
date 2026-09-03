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
        @page {{ size: A4 portrait; margin: 12mm; background-color: #0b0f19; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #0b0f19; color: #f3f4f6; margin: 0; padding: 0; box-sizing: border-box; }}
        *, *::before, *::after {{ box-sizing: border-box; }}
        .header {{ text-align: center; margin-bottom: 20px; border-bottom: 1px solid #1f2937; padding-bottom: 15px; }}
        .title {{ font-size: 20pt; font-weight: 800; color: #ffffff; margin: 0; letter-spacing: 1.5px; }}
        .subtitle {{ font-size: 9pt; color: #9ca3af; margin-top: 6px; font-weight: 500; letter-spacing: 0.5px; }}
        
        /* ใช้ Flexbox จัดเรียงการ์ด ป้องกันข้อมูลหลุดบรรทัด */
        .card {{ background: linear-gradient(135deg, #111827 0%, #1f2937 100%); margin-bottom: 10px; border-radius: 8px; width: 100%; display: flex; align-items: center; overflow: hidden; border: 1px solid #374151; padding: 10px 14px; }}
        .card-up {{ border-left: 6px solid #10b981; }}
        .card-down {{ border-left: 6px solid #ef4444; }}
        
        .cell-symbol {{ width: 22%; font-size: 12pt; font-weight: bold; color: #ffffff; padding-right: 5px; }}
        .cell-item {{ width: 15.5%; padding: 0 4px; }}
        .cell-trend {{ width: 16%; padding-left: 4px; text-align: right; }}

        .label {{ font-size: 5.5pt; color: #9ca3af; display: block; margin-bottom: 2px; text-transform: uppercase; letter-spacing: 0.3px; }}
        .value {{ font-size: 9.5pt; font-weight: bold; color: #f9fafb; }}
        .value-up {{ color: #34d399; }}
        .value-down {{ color: #f87171; }}
        .footer {{ margin-top: 20px; text-align: center; font-size: 7.5pt; color: #6b7280; letter-spacing: 0.5px; }}
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
            close_val = float(str(s.get('close', '0')).replace(',', ''))
            open_val = float(str(s.get('open', '0')).replace(',', ''))
        except:
            close_val = 0
            open_val = 0

        # เงื่อนไขสีของ Close: ถ้าต่ำกว่า Open เป็นแดง, ถ้าสูงกว่าหรือเท่ากับเป็นเขียว
        close_color_class = "value-down" if close_val < open_val else "value-up"

        trend_text = str(s.get('trendPrice', 'UP'))
        t_lower = trend_text.lower()
        is_up = ("up" in t_lower) or ("+" in trend_text)

        card_class = "card-up" if is_up else "card-down"
        val_class = "value-up" if is_up else "value-down"
        
        symbol_val = str(s.get('symbol', '-'))
        open_val_str = str(s.get('open', '-'))
        close_price_val = str(s.get('close', '-'))
        target_price_val = str(s.get('targetPrice', '-'))
        diff_val = str(s.get('diff', '0.00%'))
        volume_val = str(s.get('volume', '-'))

        is_diff_positive = diff_val.startswith("+")
        diff_color_class = "value-down" if is_diff_positive else "value-up"

        html_content += f"""
        <div class="card {card_class}">
            <div class="cell-symbol">{symbol_val}</div>
            <div class="cell-item">
                <span class="label">OPEN</span>
                <span class="value">{open_val_str}</span>
            </div>
            <div class="cell-item">
                <span class="label">CLOSE</span>
                <span class="value {close_color_class}">{close_price_val}</span>
            </div>
            <div class="cell-item" style="width: 21%;">
                <span class="label">TARGET_PRICE(TARGET/CLOSE)</span>
                <span class="value">{target_price_val} <span class="{diff_color_class}" style="font-size: 8pt;">({diff_val})</span></span>
            </div>
            <div class="cell-item" style="width: 18%;">
                <span class="label">YESTERDAY_VOL</span>
                <span class="value">{volume_val}</span>
            </div>
            <div class="cell-trend">
                <span class="label">TREND_PRICE(CLOSE/AVG)</span>
                <span class="value {val_class}">{trend_text}</span>
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
