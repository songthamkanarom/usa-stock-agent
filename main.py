import base64
from flask import Flask, jsonify, render_template_string, request
from weasyprint import HTML

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <style>
        @page {
            size: 1920px 2400px; /* 📌 ปรับขนาดให้เหมาะกับหน้าจอคอมพิวเตอร์ ไม่ต้องซูม 250% */
            margin: 0;
        }
        body {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background-color: #0d1117;
            color: #ffffff;
            margin: 0;
            padding: 30px;
        }
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #161b22;
            padding: 35px 45px;
            border-radius: 14px;
            margin-bottom: 30px;
            border: 2px solid #30363d;
        }
        .logo-box img {
            height: 140px;
            object-fit: contain;
        }
        .title-box {
            text-align: right;
        }
        .title-box h1 {
            margin: 0;
            font-size: 52px;
            letter-spacing: 2px;
            color: #ffffff;
        }
        .title-box p {
            margin: 10px 0 0 0;
            font-size: 26px;
            color: #8b949e;
        }
        .card {
            background-color: #161b22;
            border: 2px solid #30363d;
            border-radius: 14px;
            padding: 28px 35px;
            margin-bottom: 20px;
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
            width: 14px;
            background-color: #238636;
        }
        .card-left-border-down {
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 14px;
            background-color: #da3633;
        }
        .col-symbol {
            width: 13%;
        }
        .col-symbol .symbol-text {
            font-size: 34px;
            font-weight: bold;
            color: #ffffff;
            display: block;
        }
        .col-field {
            text-align: right;
        }
        .field-label {
            font-size: 20px;
            color: #8b949e;
            display: block;
            margin-bottom: 8px;
            text-align: right;
        }
        .field-value {
            font-size: 30px;
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
        .btn-link {
            font-size: 26px;
            color: #58a6ff;
            text-decoration: none;
            font-weight: bold;
        }
    </style>
</head>
<body>

    <div class="header-container">
        <div class="logo-box">
            {% if logo %}
                <img src="{{ logo }}" alt="Logo">
            {% else %}
                <h2 style="margin:0; color:#fff; font-size:40px;">TANGMO ADVISOR</h2>
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
            {% if '-' in stock.trendPrice %}
                {% set is_up = false %}
            {% endif %}
            
            <div class="{% if is_up %}card-left-border-up{% else %}card-left-border-down{% endif %}"></div>

            <!-- 1. SYMBOL -->
            <div class="col-symbol" style="padding-left: 15px;">
                <span class="symbol-text">{{ stock.symbol }}</span>
            </div>

            <!-- 2. TRADINGVIEW LINK -->
            <div class="col-field" style="width: 8%;">
                <span class="field-label">TradingView</span>
                <span class="field-value">
                    {% if stock.tvUrl %}
                        <a href="{{ stock.tvUrl }}" class="btn-link">Chart</a>
                    {% else %}
                        -
                    {% endif %}
                </span>
            </div>

            <!-- 3. OPEN -->
            <div class="col-field" style="width: 8%;">
                <span class="field-label">Open</span>
                <span class="field-value">{{ stock.open }}</span>
            </div>

            <!-- 4. CLOSE -->
            <div class="col-field" style="width: 13%;">
                <span class="field-label">Close</span>
                <span class="field-value">
                    {{ stock.close }}
                    <span style="font-size: 22px; font-weight: normal;" class="{% if '-' in stock.closeOpenDiff %}text-red{% else %}text-green{% endif %}">
                        ({{ stock.closeOpenDiff }})
                    </span>
                </span>
            </div>

            <!-- 5. TARGET PRICE -->
            <div class="col-field" style="width: 14%;">
                <span class="field-label">Target Price/Close</span>
                <span class="field-value">
                    {{ stock.targetPrice }}
                    <span style="font-size: 22px; font-weight: normal;" class="{% if '-' in stock.diff %}text-red{% else %}text-green{% endif %}">
                        ({{ stock.diff }})
                    </span>
                </span>
            </div>

            <!-- 6. YESTERDAY VOL -->
            <div class="col-field" style="width: 11%;">
                <span class="field-label">Yesterday Vol</span>
                <span class="field-value" style="font-size: 26px;">{{ stock.volume }}</span>
            </div>

            <!-- 7. TREND PRICE -->
            <div class="col-field" style="width: 11%;">
                <span class="field-label">Close Price/Avg(30D)</span>
                <span class="field-value {% if '-' in stock.trendPrice %}text-red{% else %}text-green{% endif %}">
                    {% if '-' in stock.trendPrice %}▼{% else %}▲{% endif %} {{ stock.trendPrice }}
                </span>
            </div>

            <!-- 8. SLOPE PRICE -->
            <div class="col-field" style="width: 8%;">
                <span class="field-label">Slope Price(30D)</span>
                <span class="field-value {% if '-' in stock.slopePrice %}text-red{% else %}text-green{% endif %}">
                    {{ stock.slopePrice }}
                </span>
            </div>

            <!-- 9. SLOPE VOL -->
            <div class="col-field" style="width: 8%;">
                <span class="field-label">Slope Vol(30D)</span>
                <span class="field-value {% if '-' in stock.slopeVol %}text-red{% else %}text-green{% endif %}">
                    {{ stock.slopeVol }}
                </span>
            </div>

            <!-- 📌 10. FIBONACCI 61.8% (ย้ายมาไว้ท้ายสุดตามต้องการ) -->
            <div class="col-field" style="width: 10%;">
                <span class="field-label">Fib 61.8% (30D)</span>
                <span class="field-value" style="color: #e3b341;">
                    {{ stock.fib618 if stock.fib618 else '-' }}
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
            return jsonify({"status": "error", "message": "No JSON payload provided"}), 400
        
        date_str = data.get("date", "")
        logo_base64 = data.get("logo", "")
        stocks = data.get("stocks", [])
        
        rendered_html = render_template_string(
            HTML_TEMPLATE, 
            date=date_str, 
            logo=logo_base64, 
            stocks=stocks
        )
        
        pdf_bytes = HTML(string=rendered_html).write_pdf()
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        return jsonify({"status": "success", "pdf_base64": pdf_base64})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
