import requests
import json
import time  # Add this import for the sleep function

# Replace with your actual API endpoint
url = "https://catalog.chaldal.com/searchPersonalized"

# Base payload with your API parameters
base_payload = data = {
    "apiKey": "e964fc2d51064efa97e94db7c64bf3d044279d4ed0ad4bdd9dce89fecc9156f0",
    "storeId": 1,
    "warehouseId": 27,
    "pageSize": 10000,  # Increased to cover all products (if supported)
    "currentPageIndex": 18,
    "metropolitanAreaId": 1,
    "query": "",
    "productVariantId": -1,
    "bundleId": None,
    "canSeeOutOfStock": True,
    "filters": [],
    "maxOutOfStockCount": None,  # Removed out-of-stock limit
    "shouldShowAlternateProductsForAllOutOfStock": None,  # Turned off alternate recommendations
    "customerGuid": None,
    "deliveryAreaId": None,
    "shouldShowCategoryBasedRecommendations": None
}


all_products = []  # List to store all the products

# Loop over page indices from 0 to 60 (inclusive)
for page in range(63):
    payload = base_payload.copy()
    payload["currentPageIndex"] = page

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an error if the HTTP request returned an unsuccessful status code
        data = response.json()
        hits = data.get("hits", [])
        all_products.extend(hits)
        print(f"Page {page}: Retrieved {len(hits)} products")
    except requests.RequestException as e:
        print(f"Error on page {page}: {e}")

    # Add cooldown every 15 iterations
    if (page + 1) % 15 == 0 and page < 60:
        print(f"Cooling down for 5 seconds after page {page}...")
        # time.sleep(5)

# Save the collected products to a JSON file
json_filename = "products.json"
try:
    with open(json_filename, "w", encoding="utf-8") as jsonfile:
        json.dump(all_products, jsonfile, ensure_ascii=False, indent=4)
    print(f"Successfully saved {len(all_products)} products to {json_filename}")
except Exception as e:
    print(f"Error writing to JSON: {e}")