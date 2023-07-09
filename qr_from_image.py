import win32ui
import win32print
import win32gui
import requests
import time
import datetime
import json
printer_name = 'POS-80C1'

def format_currency(amount):
    return "{:,.0f}".format(amount)

respDataReceipt = requests.get('http://tikkubzaza.trueddns.com:54242/web/restaurant/public_htmls/index.php?route=order/getReceipt')
respDataReceipt = json.loads(respDataReceipt.content.decode('utf-8-sig'))
for receipt in respDataReceipt:
    table_id = receipt['table_id']
    respDataReceiptDetail = requests.get('http://tikkubzaza.trueddns.com:54242/web/restaurant/public_htmls/index.php?route=order/getOrder&table_id='+table_id)
    if respDataReceiptDetail.ok is not None:
        respDataReceiptDetail = json.loads(respDataReceiptDetail.content.decode('utf-8-sig'))
        receipt = "***************************\n"
        receipt += "                      RECEIPT        \n"
        receipt += "************************************************\n\n"
        receipt += "Items:\n"
        max_item_length = max(len(item['name']) for item in respDataReceiptDetail)
        total = 0
        for item in respDataReceiptDetail:
            item_line = "- {:<{item_width}}".format(item['name'], item_width=max_item_length)
            price = float(item['price'])
            receipt += f"{item_line}  {format_currency(price):>8} $\n"
            receipt += "     - " + item['comment'] + "\n"
            total += price
        receipt += "\n"
        receipt += "------------------------------------------------\n"
        receipt += "Total:           {}\n".format(format_currency(total)) + ".-"
        receipt += "------------------------------------------------\n\n"

        qr_code_content = "Your QR code text"  # Replace with your desired text for the QR code

        receipt += "       ขอบคุณหลายเด้อ       \n"
        receipt += "***********************************************\n"

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