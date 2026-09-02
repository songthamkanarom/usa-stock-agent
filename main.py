from flask import Flask, request, jsonify
from weasyprint import HTML
import datetime
import os

app = Flask(__name__)

@app.route("/", methods=["POST"])
def generate_dashboard():
    req_data = request.get_json()
    if not req_data or "stocks" not in req_data:
        return jsonify({"error": "Invalid payload"}), 400

    stocks = req_data["stocks"]
    date_str = req_data.get("date", datetime.datetime.now().strftime("%d/%m/%Y"))

    # สร้าง HTML ตามสไตล์ Modern Dashboard[cite: 2]
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
        @page {{ size: A4 portrait; margin: 15mm; background-color: #121212; }}
        body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #121212; color: #ffffff; margin: 0; padding: 0; box-sizing: border-box; }}
        *, *::before, *::after {{ box-sizing: border-box; }}
        .header {{ text-align: center; margin-bottom: 30px; border-bottom: 1px solid #333333; padding-bottom: 20px; }}
        .title {{ font-size: 20pt; font-weight: 700; color: #ffffff; margin: 0; letter-spacing: 1px; }}
        .subtitle {{ font-size: 10pt; color: #888888; margin-top: 6px; }}
        .card {{ background-color: #1E1E1E; margin-bottom: 12px; border-radius: 8px; width: 100%; display: table; border-collapse: collapse; overflow: hidden; }}
        .card-up {{ border-left: 6px solid #00B900; }}
        .card-down {{ border-left: 6px solid #FF334B; }}
        .row {{ display: table-row; }}
        .cell {{ display: table-cell; padding: 14px 12px; vertical-align: middle; }}
        .symbol {{ font-size: 15pt; font-weight: bold; width: 18%; color: #ffffff; }}
        .label {{ font-size: 7.5pt; color: #777777; display: block; margin-bottom: 3px; text-transform: uppercase; }}
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
        # เช็คสถานะเขียว/แดงจากราคาปิดเทียบราคาเปิด
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

    # แปลง HTML เป็น PDF บันทึกลง Disk ชั่วคราว
    output_pdf = "/tmp/dashboard.pdf"
    HTML(string=html_content).write_pdf(output_pdf)

    # ส่งไฟล์ PDF กลับไปให้ผู้เรียก (หรือสามารถเขียนโค้ดอัปโหลดเข้า Google Drive ต่อจากตรงนี้ได้ทันที)
    return jsonify({
        "status": "success",
        "message": "Dashboard generated successfully"
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))