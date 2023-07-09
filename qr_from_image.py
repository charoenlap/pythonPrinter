import win32ui
import win32print
import win32gui
import requests
import time
import datetime
import json
from datetime import datetime
printer_name = 'POS-80C1'

def format_currency(amount):
    return "{:,.0f}".format(amount)

def generate_receipt(items):
    receipt = ""  # Initialize receipt string

    # Get current date and time
    current_datetime = datetime.now()

    # Header line
    receipt += "=" * 40 + "\n"
    receipt += "{:^40}\n".format("ใบเสร็จ")
    receipt += "=" * 40 + "\n"
    receipt += "{:^40}\n".format(current_datetime.strftime("%d/%m/%Y %H:%M:%S"))
    receipt += "-" * 40 + "\n"

    total = 0  # Initialize total

    # Print each item
    for item in items:
        name = item.get('name', '')
        option = item.get('option', '')
        price_str = item.get('price', '0.00')
        price = float(price_str)
        total += price

        # Format and append item name and price without decimal places
        formatted_price = "{:,.0f}".format(price)
        receipt += "{:<35}{:>5}\n".format(name, formatted_price)

        # Append item option on multiple lines with appropriate indentation
        if option:
            option_lines = option.split("\n")
            for line in option_lines:
                receipt += "  - {:<32}\n".format(line.strip())

        receipt += "-" * 40 + "\n"

    formatted_total = "{:,.0f}".format(total)
    receipt += "{:<35}{:>5}\n".format("Total", formatted_total)
    receipt += "=" * 40 + "\n"  # Footer line

    return receipt


# Example usage with multiple items
items = [
    {"name": "Item 1", "option": "Option A", "price": "9.99"},
    {"name": "Item 2", "option": "This is a long option\nthat exceeds 26 characters", "price": "14.99"},
    {"name": "Item 3", "option": "Option\nB", "price": "5.99"}
]



respDataReceipt = requests.get('http://tikkubzaza.trueddns.com:54242/web/restaurant/public_htmls/index.php?route=order/getReceipt')
respDataReceipt = json.loads(respDataReceipt.content.decode('utf-8-sig'))
for receipt in respDataReceipt:
    table_id = receipt['table_id']
    respDataReceiptDetail = requests.get('http://tikkubzaza.trueddns.com:54242/web/restaurant/public_htmls/index.php?route=order/getOrder&table_id='+table_id)
    if respDataReceiptDetail.ok is not None:
        respDataReceiptDetail = json.loads(respDataReceiptDetail.content.decode('utf-8-sig'))
        receipt = generate_receipt(respDataReceiptDetail)


        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(printer_name)

        # Define the font properties
        font_name = "TH Sarabun New"
        font_size = 1.8  # Smaller font size
        font_weight = 800

        # Set up paper size
        paper_width = 80 * 1440 / 25.4  # Convert 80mm to pixels
        paper_height = 2000  # Adjust as needed

        # Start printing the order
        hDC.StartDoc("order")
        hDC.StartPage()

        font = win32ui.CreateFont({
            "name": font_name,
            "height": int(font_size * -20),  # Convert font size to logical units
            "weight": font_weight,
        })

        hDC.SelectObject(font)

        # Calculate the size of a character in the selected font
        char_width, char_height = hDC.GetTextExtent("X")

        # Define the initial x and y coordinates for printing
        x = 10  # Move the text closer to the left margin
        y = 100

        # Print each line of the order
        i = 0
        for line in receipt.splitlines():
            if i == 0:
                font = win32ui.CreateFont({
                    "name": font_name,
                    "height": int(3 * -20),  # Convert font size to logical units
                    "weight": font_weight,
                })
                hDC.SelectObject(font)
            else:
                font = win32ui.CreateFont({
                    "name": font_name,
                    "height": int(font_size * -20),  # Convert font size to logical units
                    "weight": font_weight,
                })
            hDC.SelectObject(font)
            i+=1
            hDC.TextOut(x, y, line)
            y += char_height

            # Check if we reached the end of the page
            if y + char_height > paper_height:
                hDC.EndPage()
                hDC.StartPage()
                y = 100  # Reset y coordinate to top of new page

        # End printing and clean up the DC
        hDC.EndPage()
        hDC.EndDoc()
        hDC.DeleteDC()