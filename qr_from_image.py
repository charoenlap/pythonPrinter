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
    
    receipt += "{:^40}\n".format("ใบเสร็จ") + "\n"
    receipt += "=" * 55 + "\n"
    receipt += "{:^55}\n".format(current_datetime.strftime("%d/%m/%Y %H:%M:%S"))
    receipt += "-" * 55 + "\n"

    total = 0  # Initialize total

    # Print each item
    for item in items:
        name = item.get('name', '')
        comment = item.get('comment', '')
        option_name = item.get('option_name', '')
        price_str = item.get('price', '0.00')
        price = float(price_str)
        total += price

        # Format and append item name and price without decimal places
        formatted_price = "{:,.0f}".format(price)

        # Combine item name and option name
        combined_name = f"{name} - {option_name}" if option_name else name

        # Append item name and price
        receipt += "{:<50}{:>5}\n".format(combined_name, formatted_price)

        # Append item comment on multiple lines with appropriate indentation
        if comment:
            comment_lines = comment.split("\n")
            for line in comment_lines:
                receipt += "  {:<47}\n".format(line.strip())

    receipt += "-" * 55 + "\n"
    formatted_total = "{:,.0f}".format(total)
    receipt += "{:<50}{:>5}\n".format("Total", formatted_total)
    receipt += "=" * 55 + "\n"  # Footer line

    return receipt

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
        font_size = 1.7  # Smaller font size
        font_weight = 800

        # Set up paper size
        paper_width = 55 * 1440 / 25.4  # Convert 55mm to pixels
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
