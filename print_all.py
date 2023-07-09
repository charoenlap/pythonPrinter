import win32ui
import win32print
import win32gui
import requests
import time
import datetime
import json
import qrcode
# from pythainlp.tokenize import dict_word_tokenize

while True:
    try:
        for printer_name in ['POS-80C1', 'POS-80C2']:
            # respData = [{"table_name":"Table 1","date_create":"2022-04-25 18:30:00","orders":[{"menu_name":"Grilled Salmon","option_name":"Buffalo Sauce","comment":"Medium rare"},{"menu_name":"Chicken Wings","option_name":"Buffalo Sauce","comment":"Extra crispy"}]}]
            # respData = requests.get('https://charoenlap.com/restaurant/public_html/index.php?route=order/feedPrinter')
            respData = requests.get('https://charoenlap.com/restaurant/public_html/index.php?route=order/feedPrinter&printer_name=' + printer_name)
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
                    text = "                โต๊ะ "+ row['table_name'] +"\n\n"
                    text += "เวลา " + row['date_create'] + "\n"
                    text += "===================================\n"
                    for order in row['orders']:
                        print(order)
                        text += order['menu_name']
                        if order['option_name']:
                            text += " - " + order['option_name']
                        text += '\n'
                        if order['comment']:
                            text += "     - " + order['comment'] + "\n"
                            # tokens = word_tokenize(order['comment'], engine="newmm")
                            # filtered_tokens = [token for token in tokens if len(token) <= 20]
                            # for token in tokens:
                            #     # print(token)
                            #     # text += "     - " + token + "\n"
                        orderArr.append(order['id'])
                    text += "==================================="

                    if printer_name == 'GP-5890XII':
                        print(printer_name)
                        font_name = "TH Sarabun New"
                        font_size = 1.8
                        font_weight = 800  # 800 is equivalent to bold
                        paper_width = 55 * 1440 / 25.4
                        paper_height = 2000

                        printer_name = win32print.GetDefaultPrinter()

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
                                for orderId in orderArr:
                                    # x = requests.get('https://charoenlap.com/restaurant/public_html/index.php?route=order/feedPrinterUpdate&order_id='+orderId)
                                    print('https://charoenlap.com/restaurant/public_html/index.php?route=order/feedPrinterUpdate&order_id=' + orderId)
                        finally:
                            hDC.DeleteDC()
                    eles:
                    # printer_name = "POS-80C1"
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
                for orderId in orderArr:
                    x = requests.get('https://charoenlap.com/restaurant/public_html/index.php?route=order/feedPrinterUpdate&order_id='+orderId)
                    print('https://charoenlap.com/restaurant/public_html/index.php?route=order/feedPrinterUpdate&order_id=' + orderId)
            if printer_name == 'POS-80C1':
                # data = json.loads(respData.content.decode('utf-8-sig'))
                respDataReceipt = requests.get('http://tikkubzaza.trueddns.com:54242/web/restaurant/public_htmls/index.php?route=order/getReceipt')
                for respDataReceipt in receipt:
                    table = receipt.table_id
                    respDataReceiptDetail = requests.get('http://tikkubzaza.trueddns.com:54242/web/restaurant/public_htmls/index.php?route=order/getOrder&table_id='+table_id)
                    if respDataReceiptDetail.ok is not None:
                        print(respDataReceiptDetail)
                        receipt = "***************************\n"
                        receipt += "        RECEIPT        \n"
                        receipt += "***************************\n\n"
                        receipt += "Items:\n"
                        max_item_length = max(len(item['name']) for item in respDataReceiptDetail)
                        total = 0
                        for item in respDataReceiptDetail:
                            item_line = "- {:<{item_width}}".format(item['name'], item_width=max_item_length)
                            price = int(float(item['price']) * 100)
                            receipt += f"{item_line}  ${price:>8}\n"
                            receipt += "  Option: " + item['option'] + "\n"
                            total += price
                        receipt += "\n"
                        receipt += "---------------------------\n"
                        receipt += "        เลขบัญชี 1730691250 กรุงไทย        \n"
                        receipt += "       ชื่อ นาย ชาตรี มณีวรวัฒน์       \n"
                        receipt += "---------------------------\n\n"

                        qr_code_content = "Your QR code text"  # Replace with your desired text for the QR code

                        # Generate the QR code
                        qr_code = qrcode.make(qr_code_content)

                        # Add the QR code to the receipt
                        receipt += qr_code.get_ascii() + "\n"

                        receipt += "       Thank you for your purchase!       \n"
                        receipt += "***************************\n"

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
    x = datetime.datetime.now()
    print(x)
    time.sleep(2)
except:
print('fail')
