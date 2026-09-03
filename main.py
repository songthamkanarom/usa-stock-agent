import base64
from flask import Flask, jsonify, render_template_string, request
from weasyprint import HTML

app = Flask(__name__)

# HTML Template สำหรับสร้างรายงาน PDF พร้อมรองรับโลโก้
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <style>
        @page {
            size: A4;
            margin: 15mm;
        }
        body {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #333333;
            background-color: #f8f9fa;
            margin: 0;
            padding: 0;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #1E1E1E;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .logo-container img {
            height: 45px;
            object-fit: contain;
        }
        .title-container {
            text-align: right;
        }
        .title-container h1 {
            margin: 0;
            font-size: 20px;
            color: #1E1E1E;
        }
        .title-container p {
            margin: 3px 0 0 0;
            font-size: 12px;
            color: #666666;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: #ffffff;
            border-radius: 6px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 10px 12px;
            text-align: left;
            font-size: 11px;
            border-bottom: 1px solid #eeeeee;
        }
        th {
            background-color: #1E1E1E;
            color: #ffffff;
            font-weight: bold;
            text-transform: uppercase;
        }
        tr:last-child td {
            border-bottom: none;
        }
        .text-right {
            text-align: right;
        }
        .text-center {
            text-align: center;
        }
        .text-green {
            color: #00B900;
            font-weight: bold;
        }
        .text-red {
            color: #FF334B;
            font-weight: bold;
        }
    </style>
</head>
<body>

    <div class="header">
        <div class="logo-container">
            {% if logo %}
                <img src="{{ logo }}" alt="Logo">
            {% else %}
                <h2>TANGMO ADVISOR</h2>
            {% endif %}
        </div>
        <div class="title-container">
            <h1>USA Stock Market Dashboard</h1>
            <p>ประจำวันที่: {{ date }}</p>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th>Symbol</th>
                <th class="text-right">Open</th>
                <th class="text-right">Close</th>
                <th class="text-right">Target Price</th>
                <th class="text-right">Yesterday Vol ($)</th>
                <th class="text-center">Trend (Price/Avg)</th>
            </tr>
        </thead>
        <tbody>
            {% for stock in stocks %}
            <tr>
                <td><strong>{{ stock.symbol }}</strong></td>
                <td class="text-right">{{ stock.open }}</td>
                <td class="text-right">
                    {{ stock.close }} 
                    <span style="font-size: 9px; {% if '-' in stock.closeOpenDiff %}color: #FF334B;{% else %}color: #00B900;{% endif %}">
                        ({{ stock.closeOpenDiff }})
                    </span>
                </td>
                <td class="text-right">
                    {{ stock.targetPrice }} 
                    <span style="font-size: 9px; color: #666666;">({{ stock.diff }})</span>
                </td>
                <td class="text-right">{{ stock.volume }}</td>
                <td class="text-center">
                    {% if 'Up' in stock.trendPrice or '+' in stock.trendPrice %}
                        <span class="text-green">🟢 {{ stock.trendPrice }}</span>
                    {% else %}
                        <span class="text-red">🔴 {{ stock.trendPrice }}</span>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </body>
    </table>

</body>
</html>
"""


@app.route("/", methods=["POST"])
def generate_pdf():
  try:
    data = request.get_json()
    if not data:
      return (
          jsonify({"status": "error", "message": "No JSON payload provided"}),
          400,
      )

    date_str = data.get("date", "")
    logo_base64 = data.get("logo", "")
    stocks = data.get("stocks", [])

    # เรนเดอร์ HTML ด้วยข้อมูลที่ส่งมา
    rendered_html = render_template_string(
        HTML_TEMPLATE, date=date_str, logo=logo_base64, stocks=stocks
    )

    # แปลง HTML เป็น PDF ด้วย WeasyPrint
    pdf_bytes = HTML(string=rendered_html).write_pdf()

    # แปลงไฟล์ PDF เป็น Base64 เพื่อส่งกลับไปให้ Google Apps Script
    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

    return jsonify({"status": "success", "pdf_base64": pdf_base64})

  except Exception as e:
    return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
