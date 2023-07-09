import win32ui
import win32print
import win32gui
import requests
import time
import datetime
import json
from pythainlp.tokenize import word_tokenize

def format_currency(amount):
    return "{:,.0f}".format(amount)

def generate_receipt(items):
    receipt = ""  # Initialize receipt string

    # Get current date and time
    current_datetime = datetime.datetime.now()

    # Header line
    
    receipt += "{:^30}\n".format("ใบเสร็จ " + items[0]['table_name']) + " \n"
    receipt += "=" * 55 + "\n"
    receipt += current_datetime.strftime("%d/%m/%Y %H:%M:%S") + " \n"
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

while True:
    try:
        for printer_name in ['POS-80C1', 'POS-80C2', 'GP-5890XII']:
            # respData = [{"table_name":"Table 1","date_create":"2022-04-25 18:30:00","orders":[{"menu_name":"Grilled Salmon","option_name":"Buffalo Sauce","comment":"Medium rare"},{"menu_name":"Chicken Wings","option_name":"Buffalo Sauce","comment":"Extra crispy"}]}]
            # respData = requests.get('https://charoenlap.com/restaurant/public_htmls/index.php?route=order/feedPrinter')
            respData = requests.get('http://tikkubzaza.trueddns.com:54242/web/restaurant/public_htmls/index.php?route=order/feedPrinter&printer_name=' + printer_name)
            # print(respData)
            if respData.ok is not None:
                # data = respData.json()
                data = json.loads(respData.content.decode('utf-8-sig'))
                for row in data:
                    #     text = """
                    #                 โต๊ะ 01
                    # เวลา 09:27
                    # ===================================
                    # ต้มเลือดหมู
                    # ต้มเลือกหมู - พิเศษ + ไข่ดาว
                    #    - ไม่ผัก
                    # ผัดกระเพราทะเล - พิเศษ + ไข่ดาว
                    # ==================================="""
                    orderArr = []
                    text = "         "+ row['table_name'] +"\n\n"
                    text += "เวลา " + row['date_create'] + "\n"
                    text += "===================================\n"
                    for order in row['orders']:
                        print(order)
                        text += order['menu_name']
                        if order['option_name']:
                            text += " - " + order['option_name']
                        text += '\n'
                        if order['comment']:
                            # text += "     - " + order['comment'] + "\n"

                            tokens = word_tokenize(order['comment'])
                            result = ''
                            count = 0

                            for token in tokens:
                                if count + len(token) + 1 > 40:
                                    result += '\n     - '
                                    count = 0

                                result += token
                                count += len(token) + 1
                            text += "     - " + result + "\n"
                        orderArr.append(order['id'])
                    text += "==================================="
                    # text += "===================================\n"
                    # text += "===================================\n"
                    # text += "==================================="

                    if printer_name == 'GP-5890XII':
                        print(printer_name)
                        font_name = "TH Sarabun New"
                        font_size = 1.8
                        font_weight = 800  # 800 is equivalent to bold
                        paper_width = 55 * 1440 / 25.4
                        paper_height = 2000

                        # printer_name = win32print.GetDefaultPrinter()

                        hDC = win32ui.CreateDC()
                        # hDC.CreatePrinterDC(printer_name)
                        hDC.CreatePrinterDC(printer_name)

                        try:
                            hDC.StartDoc("Order Receipt")
                            try:
                                for line in text.splitlines():
                                    hDC.StartPage()
                                    font = win32ui.CreateFont({
                                        "name": font_name,
                                        "height": int(font_size * -20),
                                        "weight": font_weight,
                                    })
                                    hDC.SelectObject(font)
                                    max_line_height = int(paper_height / font_size * 0.9)
                                    x = 0
                                    y = 0
                                    while line:

                                        max_line_width = int(paper_width / font_size * 0.9)
                                        while win32gui.GetTextExtentPoint32(hDC.GetSafeHdc(), line[:max_line_width])[0] > paper_width:
                                            max_line_width -= 1
                                        hDC.TextOut(x, y, line[:max_line_width])
                                        y += font_size
                                        if y + font_size > max_line_height:
                                            hDC.EndPage()
                                            hDC.StartPage()
                                            y = 0
                                        line = line[max_line_width:].lstrip()
                                    # Print any remaining text that was not printed in the loop

                                    if line:
                                        hDC.TextOut(x, y, line)

                                    hDC.EndPage()
                            finally:
                                hDC.EndDoc()
                                # for orderId in orderArr:
                                    # x = requests.get('https://charoenlap.com/restaurant/public_html/index.php?route=order/feedPrinterUpdate&order_id='+orderId)
                                    # print('https://charoenlap.com/restaurant/public_html/index.php?route=order/feedPrinterUpdate&order_id=' + orderId)
                        finally:
                            hDC.DeleteDC()
                    else:
                        # printer_name = "POS-80C1"
                        hDC = win32ui.CreateDC()
                        hDC.CreatePrinterDC(printer_name)

                        # Define the font properties
                        font_name = "TH Sarabun New"
                        font_size = 2  # Smaller font size
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
                        for line in text.splitlines():
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
                            i += 1
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
                    for orderId in orderArr:
                        x = requests.get('http://tikkubzaza.trueddns.com:54242/web/restaurant/public_htmls/index.php?route=order/feedPrinterUpdate&order_id='+orderId)
                        # print('https://charoenlap.com/restaurant/public_htmls/index.php?route=order/feedPrinterUpdate&order_id=' + orderId)
            if printer_name == 'POS-80C1':
                respDataReceipt = requests.get('http://tikkubzaza.trueddns.com:54242/web/restaurant/public_htmls/index.php?route=order/getReceipt')
                respDataReceipt = json.loads(respDataReceipt.content.decode('utf-8-sig'))
                for receipt in respDataReceipt:
                    table_id = receipt['table_id']
                    respDataReceiptDetail = requests.get('http://tikkubzaza.trueddns.com:54242/web/restaurant/public_htmls/index.php?route=order/getOrder&table_id='+table_id)
                    if respDataReceiptDetail.ok is not None:
                        respDataReceiptDetail = json.loads(respDataReceiptDetail.content.decode('utf-8-sig'))
                        if len(respDataReceiptDetail) > 0:
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

                            requests.get('http://tikkubzaza.trueddns.com:54242/web/restaurant/public_htmls/index.php?route=order/delReceipt&table_id='+table_id)
        x = datetime.datetime.now()
        print(x)
        time.sleep(2)
    except Exception as e:
        print(e)
