import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

# =====================================================
# 🛒 AMAZON PRODUCT SEARCH
# =====================================================
def search_amazon_products(keyword):
    """
    Search Amazon products using RapidAPI.
    """
    url = "https://real-time-amazon-data.p.rapidapi.com/search"
    querystring = {"query": keyword, "page": "1", "country": "US"}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()

        products = data.get("data", {}).get("products", [])
        clean_products = []
        for p in products:
            clean_products.append({
                "product_title": p.get("product_title"),
                "product_price": p.get("product_price"),
                "product_url": p.get("product_url"),
                "product_photo": p.get("product_photo")
            })
        return clean_products

    except Exception as e:
        print("⚠️ Error fetching Amazon data:", e)
        return []

# =====================================================
# 🏬 WALMART PRODUCT SEARCH
# =====================================================
def search_walmart_products(keyword):
    """
    Search Walmart products using RapidAPI.
    """
    url = "https://walmart-data.p.rapidapi.com/search"
    querystring = {"query": keyword, "page": "1"}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "walmart-data.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()

        items = data.get("items", [])
        clean_items = []
        for i in items:
            clean_items.append({
                "name": i.get("name"),
                "salePrice": i.get("salePrice"),
                "product_url": i.get("product_url"),
                "image": i.get("image")
            })
        return clean_items

    except Exception as e:
        print("⚠️ Error fetching Walmart data:", e)
        return []
