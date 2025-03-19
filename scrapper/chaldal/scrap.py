import requests
import csv
import time
import json

# Replace with your actual API endpoint
url = "https://catalog.chaldal.com/searchPersonalized"

# Base payload with your API parameters
base_payload = {
    "apiKey": "e964fc2d51064efa97e94db7c64bf3d044279d4ed0ad4bdd9dce89fecc9156f0",
    "storeId": 1,
    "warehouseId": 27,
    "pageSize": 10000,
    "currentPageIndex": 18,
    "metropolitanAreaId": 1,
    "query": "",
    "productVariantId": -1,
    "bundleId": None,
    "canSeeOutOfStock": True,
    "filters": [],
    "maxOutOfStockCount": None,
    "shouldShowAlternateProductsForAllOutOfStock": None,
    "customerGuid": None,
    "deliveryAreaId": None,
    "shouldShowCategoryBasedRecommendations": None
}

all_products = []  # List to store all the products

# Loop over page indices from 0 to 62 (inclusive)
for page in range(63):
    payload = base_payload.copy()
    payload["currentPageIndex"] = page

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        response.encoding = 'utf-8'  # Ensure proper encoding for the response
        data = response.json()
        hits = data.get("hits", [])
        all_products.extend(hits)
        print(f"Page {page}: Retrieved {len(hits)} products")
    except requests.RequestException as e:
        print(f"Error on page {page}: {e}")

    # Add cooldown every 15 iterations
    if (page + 1) % 15 == 0 and page < 62:
        print(f"Cooling down for 5 seconds after page {page}...")
        # time.sleep(5)

# Function to flatten nested JSON
def flatten_json(nested_json, prefix=''):
    flattened = {}
    for key, value in nested_json.items():
        if isinstance(value, dict):
            flattened.update(flatten_json(value, prefix + key + '_'))
        elif isinstance(value, list):
            # For lists, convert to JSON string with ensure_ascii=False to preserve Unicode
            flattened[prefix + key] = json.dumps(value, ensure_ascii=False)
        else:
            flattened[prefix + key] = value
    return flattened

# Flatten all products
flattened_products = [flatten_json(product) for product in all_products]

# Get all unique keys to use as CSV headers
all_keys = set()
for product in flattened_products:
    all_keys.update(product.keys())

# Sort keys for consistent column order
fieldnames = sorted(list(all_keys))

# Save to CSV with proper encoding and handling for Bengali characters
csv_filename = "products.csv"
try:
    # Using utf-8-sig encoding with BOM to help Excel recognize the encoding
    with open(csv_filename, "w", newline='', encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for product in flattened_products:
            # Handle any missing keys
            row = {k: (product.get(k, '') or '') for k in fieldnames}
            writer.writerow(row)
    print(f"Successfully saved {len(flattened_products)} products to {csv_filename}")
except Exception as e:
    print(f"Error writing to CSV: {e}")