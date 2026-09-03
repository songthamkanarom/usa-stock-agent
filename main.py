import base64
from flask import Flask, jsonify, render_template_string, request
from weasyprint import HTML

app = Flask(__name__)

# HTML Template (Dark Theme Cards พร้อมใส่สีให้ % Target)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <style>
        @page {
            size: A4;
            margin: 10mm;
        }
        body {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background-color: #0d1117;
            color: #ffffff;
            margin: 0;
            padding: 20px;
        }
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #161b22;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid #30363d;
        }
        .logo-box img {
            height: 45px;
            object-fit: contain;
        }
        .title-box {
            text-align: right;
        }
        .title-box h1 {
            margin: 0;
            font-size: 22px;
            letter-spacing: 1px;
            color: #ffffff;
        }
        .title-box p {
            margin: 5px 0 0 0;
            font-size: 11px;
            color: #8b949e;
        }
        .card {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 12px 18px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: relative;
            overflow: hidden;
        }
        .card-left-border-up {
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 6px;
            background-color: #238636;
        }
        .card-left-border-down {
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 6px;
            background-color: #da3633;
        }
        .col-symbol {
            width: 22%;
        }
        .col-symbol .symbol-text {
            font-size: 15px;
            font-weight: bold;
            color: #ffffff;
            display: block;
        }
        .col-field {
            width: 15%;
            text-align: right;
        }
        .field-label {
            font-size: 8px;
            color: #8b949e;
            text-transform: uppercase;
            display: block;
            margin-bottom: 2px;
        }
        .field-value {
            font-size: 13px;
            font-weight: bold;
            color: #ffffff;
            display: block;
        }
        .text-green {
            color: #3fb950 !important;
        }
        .text-red {
            color: #f85149 !important;
        }
    </style>
</head>
<body>

    <div class="header-container">
        <div class="logo-box">
            {% if logo %}
                <img src="{{ logo }}" alt="Logo">
            {% else %}
                <h2 style="margin:0; color:#fff; font-size:16px;">TANGMO ADVISOR</h2>
            {% endif %}
        </div>
        <div class="title-box">
            <h1>USA MARKET DAILY DASHBOARD</h1>
            <p>{{ date }} • AUTOMATED TRADING AGENT</p>
        </div>
    </div>

    <div>
        {% for stock in stocks %}
        <div class="card">
            {% set is_up = true %}
            {% if '-' in stock.trendPrice or 'Down' in stock.trendPrice %}
                {% set is_up = false %}
            {% endif %}
            
            <div class="{% if is_up %}card-left-border-up{% else %}card-left-border-down{% endif %}"></div>

            <div class="col-symbol" style="padding-left: 10px;">
                <span class="symbol-text">{{ stock.symbol }}</span>
            </div>

            <div class="col-field">
                <span class="field-label">OPEN</span>
                <span class="field-value">{{ stock.open }}</span>
            </div>

            <div class="col-field">
                <span class="field-label">CLOSE</span>
                <span class="field-value">
                    {{ stock.close }}
                    <span style="font-size: 10px; font-weight: normal;" class="{% if '-' in stock.closeOpenDiff %}text-red{% else %}text-green{% endif %}">
                        ({{ stock.closeOpenDiff }})
                    </span>
                </span>
            </div>

            <div class="col-field" style="width: 18%;">
                <span class="field-label">TARGET_PRICE(TARGET/CLOSE)</span>
                <span class="field-value">
                    {{ stock.targetPrice }}
                    <span style="font-size: 10px; font-weight: normal;" class="{% if '-' in stock.diff %}text-red{% else %}text-green{% endif %}">
                        ({{ stock.diff }})
                    </span>
                </span>
            </div>

            <div class="col-field" style="width: 16%;">
                <span class="field-label">YESTERDAY_VOL</span>
                <span class="field-value" style="font-size: 12px;">{{ stock.volume }}</span>
            </div>

            <div class="col-field" style="width: 14%;">
                <span class="field-label">TREND_PRICE(CLOSE/AVG)</span>
                <span class="field-value {% if is_up %}text-green{% else %}text-red{% endif %}">
                    {% if is_up %}🟢{% else %}🔴{% endif %} {{ stock.trendPrice }}
                </span>
            </div>
        </div>
        {% endfor %}
    </div>

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

    rendered_html = render_template_string(
        HTML_TEMPLATE, date=date_str, logo=logo_base64, stocks=stocks
    )

    pdf_bytes = HTML(string=rendered_html).write_pdf()
    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

    return jsonify({"status": "success", "pdf_base64": pdf_base64})

  except Exception as e:
    return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
