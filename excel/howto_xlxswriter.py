# pandas writing engine
import xlsxwriter

# Create a new workbook and worksheet
workbook = xlsxwriter.Workbook("example.xlsx")
worksheet = workbook.add_worksheet()

# Define a format with custom font and alignment
format_centered = workbook.add_format({
    "font_name": "Calibri",       # Set font
    "font_size": 14,              # Set font size
    "align": "center",            # Horizontal center alignment
    "valign": "vcenter"           # Vertical center alignment
})

# border
format_border = workbook.add_format({
    "top": 2, "left": 1, "bottom": 2, "right": 1
})

# Adjust row height and column width to better see alignment
worksheet.set_row(0, 30)          # Set row height for row 1
worksheet.set_column("A:A", 20)  # Set column width for column A

# merge
worksheet.merge_range("D1:F1", "Merged Columns", format_centered)

# Write data with the custom format
worksheet.write("A1", "Hello, Excel!", format_centered)

# Manually write data
for row, row_data in enumerate(data):
    for col, value in enumerate(row_data):
        worksheet.write(row, col, value)

# Save the workbook
workbook.close()


# ~~~~~~~~~~~~~~~~~~~~~~~  OR  ~~~~~~~~~~~~~~~~~~~~~~~

import pandas as pd

# get previous sheet data using openpyxl


# Sample DataFrame
data = {"Name": ["Alice", "Bob"], "Age": [25, 30]}
df = pd.DataFrame(data)

# Write to Excel starting from column "D" (index 3)
with pd.ExcelWriter("example.xlsx", engine="xlsxwriter") as writer:
    df.to_excel(writer, index=False, startcol=3, sheet_name="Sheet1")

    # Access the workbook and worksheet
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    
    # Define custom formatting
    custom_format = workbook.add_format({
        "italic": True,
        "align": "center",
        "valign": "vcenter"
    })
    
    # Apply formatting to the DataFrame cells
    for row in range(len(df) + 1):  # Include the header row
        for col in range(len(df.columns)):
            worksheet.write(row, col + 3, worksheet.table[row][col], custom_format)  # Offset by 3 for "D"
