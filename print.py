import win32ui
import win32print
import win32gui
import requests
import time
import datetime
import json

while True:
    # respData = [{"table_name":"Table 1","date_create":"2022-04-25 18:30:00","orders":[{"menu_name":"Grilled Salmon","option_name":"Buffalo Sauce","comment":"Medium rare"},{"menu_name":"Chicken Wings","option_name":"Buffalo Sauce","comment":"Extra crispy"}]}]
    respData = requests.get('https://charoenlap.com/restaurant/public_html/index.php?route=order/feedPrinter')
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
            text = "               โต๊ะ "+ row['table_name'] +"\n"
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
                orderArr.append(order['id'])
            text += "==================================="


            font_name = "TH Sarabun New"
            font_size = 1.8
            font_weight = 800  # 800 is equivalent to bold
            paper_width = 55 * 1440 / 25.4
            paper_height = 2000

            printer_name = win32print.GetDefaultPrinter()

            hDC = win32ui.CreateDC()
            # hDC.CreatePrinterDC(printer_name)
            hDC.CreatePrinterDC('POS-80C')

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
    
    x = datetime.datetime.now()
    print(x)
    time.sleep(2)
