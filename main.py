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
            size: A4;
            margin: 0;
        }
        body {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background-color: #0d1117;
            color: #ffffff;
            margin: 0;
            padding: 10px;
        }
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #161b22;
            padding: 15px 20px;
            border-radius: 6px;
            margin-bottom: 12px;
            border: 1px solid #30363d;
        }
        .logo-box img {
            height: 95px;
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
            border-radius: 6px;
            padding: 10px 12px;
            margin-bottom: 8px;
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
            width: 15%;
        }
        .col-symbol .symbol-text {
            font-size: 13px;
            font-weight: bold;
            color: #ffffff;
            display: block;
        }
        .col-field {
            text-align: right;
        }
        .field-label {
            font-size: 7px;
            color: #8b949e;
            text-transform: uppercase;
            display: block;
            margin-bottom: 2px;
            text-align: right;
        }
        .field-value {
            font-size: 11px;
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

            <!-- 1. SYMBOL -->
            <div class="col-symbol" style="padding-left: 8px;">
                <span class="symbol-text">{{ stock.symbol }}</span>
            </div>

            <!-- 2. OPEN -->
            <div class="col-field" style="width: 10%;">
                <span class="field-label">OPEN</span>
                <span class="field-value">{{ stock.open }}</span>
            </div>

            <!-- 3. CLOSE -->
            <div class="col-field" style="width: 14%;">
                <span class="field-label">CLOSE</span>
                <span class="field-value">
                    {{ stock.close }}
                    <span style="font-size: 9px; font-weight: normal;" class="{% if '-' in stock.closeOpenDiff %}text-red{% else %}text-green{% endif %}">
                        ({{ stock.closeOpenDiff }})
                    </span>
                </span>
            </div>

            <!-- 4. TARGET PRICE -->
            <div class="col-field" style="width: 16%;">
                <span class="field-label">TargetPrice/Close</span>
                <span class="field-value">
                    {{ stock.targetPrice }}
                    <span style="font-size: 9px; font-weight: normal;" class="{% if '-' in stock.diff %}text-red{% else %}text-green{% endif %}">
                        ({{ stock.diff }})
                    </span>
                </span>
            </div>

            <!-- 5. YESTERDAY VOL -->
            <div class="col-field" style="width: 13%;">
                <span class="field-label">YESTERDAY_VOL</span>
                <span class="field-value" style="font-size: 10px;">{{ stock.volume }}</span>
            </div>

            <!-- 6. TREND PRICE -->
            <div class="col-field" style="width: 12%;">
                <span class="field-label">TrendPrice/Avg</span>
                <span class="field-value {% if is_up %}text-green{% else %}text-red{% endif %}">
                    {% if is_up %}▲ Up{% else %}▼ Down{% endif %} {{ stock.trendPrice.replace('Up','').replace('Down','').strip() }}
                </span>
            </div>

            <!-- 7. SLOPE PRICE (เพิ่มใหม่) -->
            <div class="col-field" style="width: 10%;">
                <span class="field-label">SLOPE PRICE</span>
                <span class="field-value {% if '-' in stock.slopePrice %}text-red{% else %}text-green{% endif %}">
                    {{ stock.slopePrice }}
                </span>
            </div>

            <!-- 8. SLOPE VOL (เพิ่มใหม่) -->
            <div class="col-field" style="width: 10%;">
                <span class="field-label">SLOPE VOL</span>
                <span class="field-value {% if '-' in stock.slopeVol %}text-red{% else %}text-green{% endif %}">
                    {{ stock.slopeVol }}
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
