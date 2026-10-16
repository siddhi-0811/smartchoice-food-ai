
from pathlib import Path
import sqlite3
from flask import Flask, request, render_template_string

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "data" / "processed" / "smartchoice.db"

NUTRIENTS = {
    "energy_kcal": "Energy (kcal)",
    "protein_g": "Protein (g)",
    "total_fat_g": "Total fat (g)",
    "carbohydrates_g": "Carbohydrates (g)",
    "total_sugars_g": "Total sugars (g)",
    "added_sugars_g": "Added sugars (g)",
    "dietary_fiber_g": "Dietary fibre (g)",
    "sodium_mg": "Sodium (mg)",
    "saturated_fat_g": "Saturated fat (g)",
}

HTML = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SmartChoice | Food Label Explorer</title>
<style>
body { font-family: Arial, sans-serif; max-width: 1000px;
       margin: 35px auto; padding: 0 18px; color: #24332b;
       background: #f7f8f4; }
h1 { color: #176b4d; }
form, .product { background: white; padding: 20px;
                 border-radius: 12px; margin: 18px 0; }
input { padding: 12px; width: 65%; max-width: 500px; }
button { padding: 12px 18px; background: #176b4d; color: white;
         border: 0; border-radius: 6px; cursor: pointer; }
table { width: 100%; border-collapse: collapse; margin-top: 12px; }
td, th { padding: 9px; text-align: left; border-bottom: 1px solid #ddd; }
small, .muted { color: #65756b; }
</style>
</head>
<body>
<h1>SmartChoice</h1>
<p>Explore packaged-food ingredients and nutrition information.</p>

<form method="get">
  <input name="q" value="{{ query }}" placeholder="Search product or brand"
         required>
  <button type="submit">Search</button>
</form>

{% if query %}
  <p>{{ products|length }} result(s) shown. Maximum 20.</p>
{% endif %}

{% for p in products %}
<div class="product">
  <h2>{{ p["description"] or "Product description unavailable" }}</h2>
  <p><b>Brand/owner:</b> {{ p["brand_owner"] or "Not provided" }}</p>
  <p><b>Category:</b> {{ p["branded_food_category"] or "Not provided" }}</p>
  <p><b>Serving:</b>
    {{ p["serving_size"] if p["serving_size"] is not none else "Unknown" }}
    {{ p["serving_size_unit"] or "" }}
  </p>
  <p><b>Ingredients:</b>
    {{ p["ingredients"] or "Ingredients not provided" }}
  </p>

  <h3>Reported nutrition per 100 g or 100 ml</h3>
  <table>
    <tr><th>Nutrient</th><th>Value</th></tr>
    {% for key, label in nutrients.items() %}
    <tr>
      <td>{{ label }}</td>
      <td>
      {% if p[key] is none %}
        Not reported
      {% else %}
        {{ "%.2f"|format(p[key]) }}
      {% endif %}
      </td>
    </tr>
    {% endfor %}
  </table>
  <small>Values are reported database values, not laboratory measurements.
  Check the product's physical label for confirmation.</small>
</div>
{% endfor %}

{% if query and not products %}
<p>No matches found. Try a different product or brand name.</p>
{% endif %}
</body>
</html>
"""


@app.route("/")
def home():
    query = request.args.get("q", "").strip()
    products = []

    if query:
        connection = sqlite3.connect(DB_FILE)
        connection.row_factory = sqlite3.Row

        pattern = "%" + query + "%"
        products = connection.execute("""
            SELECT p.*, f.description
            FROM products p
            LEFT JOIN food_descriptions f ON p.fdc_id = f.fdc_id
            WHERE f.description LIKE ?
               OR p.brand_owner LIKE ?
               OR p.brand_name LIKE ?
            LIMIT 20
        """, (pattern, pattern, pattern)).fetchall()

        connection.close()

    return render_template_string(
        HTML,
        query=query,
        products=products,
        nutrients=NUTRIENTS,
    )


if __name__ == "__main__":
    if not DB_FILE.exists():
        raise FileNotFoundError(
            "Database missing. Run build_database.py first."
        )
    app.run(debug=True)
