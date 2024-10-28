import pandas as pd
import numpy as np
data = [
    {"name": "Alice", "age": 25, "city": "New York"},
    {"name": "Bob", "age": 30, "city": "San Francisco"},
    {"name": "Charlie", "age": 35, "city": "Los Angeles"}
]

df = pd.DataFrame(data)
print(df)
print()
print(df.get('age'))
