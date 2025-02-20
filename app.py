from flask import Flask, render_template, request, jsonify, redirect, url_for
from scrape.shafa import parse_shafa
from scrape.olx import parse_olx
import logging
import concurrent.futures
import re
import urllib.parse

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def calculate_statistics(prices):
    if not prices:
        return 0, 0, 0
    max_price = max(prices)
    min_price = min(prices)
    avg_price = round(sum(prices) / len(prices))
    return max_price, avg_price, min_price

def clean_price(price):
    numeric_price = re.sub(r'\D', '', price)
    return int(numeric_price) if numeric_price else 0

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        app.logger.debug(f"Received query: {query}")
        encoded_query = urllib.parse.quote(query)
        return redirect(url_for('results', query=encoded_query))
    return render_template('index.html')

@app.route('/results')
def results():
    query = request.args.get('query')
    if not query:
        return redirect(url_for('index'))
    query = urllib.parse.unquote(query)
    app.logger.debug(f"Received query: {query}")
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            olx_future = executor.submit(parse_olx, query)
            shafa_future = executor.submit(parse_shafa, query)
            olx_items = olx_future.result()
            shafa_items = shafa_future.result()
        
        app.logger.debug(f"OLX items: {olx_items}")
        app.logger.debug(f"Shafa items: {shafa_items}")

        olx_prices = [clean_price(item['price']) for item in olx_items if item['price']]
        shafa_prices = [clean_price(item['price']) for item in shafa_items if item['price']]
        all_prices = olx_prices + shafa_prices

        max_price, avg_price, min_price = calculate_statistics(all_prices)

        return render_template('results.html', query=query, olx_items=olx_items, shafa_items=shafa_items, 
                               olx_count=len(olx_items), shafa_count=len(shafa_items),
                               max_price=max_price, avg_price=avg_price, min_price=min_price)
    except Exception as e:
        app.logger.error(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/test')
def test():
    return render_template('test.html')

if __name__ == '__main__':
    app.run(debug=True)