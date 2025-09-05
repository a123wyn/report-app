import openpyxl
import random
from datetime import datetime, timedelta

# Create sample data
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Sales Data"

# Headers
headers = ["Date", "Product", "Category", "Sales", "Quantity", "Region", "Customer_Type"]
ws.append(headers)

# Sample data
products = ["Product A", "Product B", "Product C", "Product D", "Product E"]
categories = ["Electronics", "Clothing", "Home", "Sports", "Books"]
regions = ["North", "South", "East", "West", "Central"]
customer_types = ["New", "Returning", "Premium"]

start_date = datetime(2024, 1, 1)

for i in range(100):
    date = start_date + timedelta(days=random.randint(0, 90))
    product = random.choice(products)
    category = random.choice(categories)
    sales = round(random.uniform(100, 5000), 2)
    quantity = random.randint(1, 50)
    region = random.choice(regions)
    customer_type = random.choice(customer_types)
    
    ws.append([date.strftime("%Y-%m-%d"), product, category, sales, quantity, region, customer_type])

wb.save("sample_data.xlsx")
print("Sample data file created: sample_data.xlsx")
