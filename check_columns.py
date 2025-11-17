import pandas as pd
import sys

try:
    # Use the path to the uploaded file
    df = pd.read_excel("/home/ubuntu/upload/bank1.xlsx")
    print("Columns found in the Excel file:")
    for col in df.columns:
        print(col)
except Exception as e:
    print(f"Error loading file: {e}", file=sys.stderr)
