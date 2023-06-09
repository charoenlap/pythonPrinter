import win32ui
import win32print
import win32gui
import requests
import time
import datetime
import json
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

                    # Start printing the receipt
                    hDC.StartDoc("Receipt")
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

                    # Print each line of the receipt
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
        x = datetime.datetime.now()
        print(x)
        time.sleep(2)
    except:
        print('fail')