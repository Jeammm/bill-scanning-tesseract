#https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.1.20230401.exe

import pyautogui
import pytesseract
import keyboard
import os
import ctypes  # An included library with Python install.   


# import random
import cv2
import numpy

os.environ["TESSDATA_PREFIX"] = "Tesseract-OCR/tessdata"

def extract_text_from_screen(region):
    screenshot = pyautogui.screenshot()
    screenshot = screenshot.crop(region)
    # img_scaled = cv2.resize(numpy.array(screenshot), None, fx=4, fy=4, interpolation=cv2.INTER_LINEAR)
    # cv2.imwrite(f"./{region}.png", img_scaled)
    custom_config = r'--psm 6'
    text = pytesseract.image_to_string(screenshot, config=custom_config)
    return text.strip()

#pre-processing for id scanning
def extract_id_from_screen(region):
    screenshot = pyautogui.screenshot()
    screenshot = screenshot.crop(region)
    img_scaled = cv2.resize(numpy.array(screenshot), None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    kernel = numpy.ones((2, 2), numpy.uint8)
    img_scaled = cv2.dilate(img_scaled, kernel, iterations=1)
    custom_config = r'--psm 11'
    text = pytesseract.image_to_string(img_scaled, config=custom_config)
    return text.strip()

def extract_text_from_screen_thai(region):
    screenshot = pyautogui.screenshot()
    screenshot = screenshot.crop(region)
    custom_config = r'-l tha --psm 6'
    text = pytesseract.image_to_string(screenshot, config=custom_config)
    return text.strip()

pytesseract.pytesseract.tesseract_cmd = "Tesseract-OCR/tesseract.exe"

# Set the coordinates of the specific section you want to scan

customer_id_region = (87, 107, 181, 123) # (left, top, width, height)
customer_name_region = (30, 128, 932, 148)

invoice_id_region = (1082, 133, 1165, 145)

bill_id_start_region = (31, 276, 148, 299)
bill_date_start_region = (151, 276, 226, 299)
bill_type_start_region = (316, 276, 341, 299)
bill_price_start_region = (1518, 276, 1638, 299)
bill_total_price_region = (1770, 981, 1872, 999)
bill_row_amount = 28

# Set the coordinates of the button to access the next page
next_page_button = (312, 50)  # (x, y)
# next_page_button = (1901, 538)  # (x, y)

output_file = "extracted_text.txt"


running = True

def stop_program():
    global running
    running = False

keyboard.add_hotkey("Ctrl+Shift+S", stop_program)

# return price and commas in correct order base on bill type
def price_type(bill_type, bill_price):
    bill_type = bill_type.lower()
    if "mk" in bill_type:
        return f'{bill_price},,'
    elif "o" in bill_type:
        return f',,{bill_price}'
    else:
        return f',{bill_price},'

# give the info coordinate base on the line no. and line size
def next_line(i, region):
    bill_row_size = 25
    return (region[0], region[1] + bill_row_size*i, region[2], region[3] + bill_row_size*i)

# Loop until the program is stopped manually or stop condition is reached
previous_invoice = 0;

end_inv = input("ใบสุดท้ายคือ: ") or "0"
time_interval = int(input("หน่วงเวลา(default=.5s) :") or 0.5)

print("เริ่มทำงานใน 5 วินาที สลับไปโปรแกรม Express แล้วเปิดจอใหญ่ไว้")
pyautogui.sleep(5)
print("Runnning.", end="")
while running:
    print(".", end="")
    # Extract text from the specified region
    name = extract_text_from_screen_thai(customer_name_region).replace('๑', ' ')
    invoice = extract_id_from_screen(invoice_id_region)

    # stop when the invoice number is the same as last one
    if invoice == previous_invoice:
        break
    previous_invoice = invoice

    if invoice.lower() == end_inv.lower():
        stop_program()

    # array of data in this invoice
    invoices = []

    # scan and insert first line to data array
    bill_id = extract_id_from_screen(bill_id_start_region)
    if bill_id and bill_id[0] == "1":
      bill_id = f"I{bill_id[1:]}"
      
    bill_date = extract_text_from_screen(bill_date_start_region).replace('/', '.')
    bill_type = extract_text_from_screen(bill_type_start_region)
    bill_price = extract_text_from_screen(bill_price_start_region).replace(',', '')

    bill_item = f"{bill_id},{bill_date},{price_type(bill_type, bill_price)}"

    first_row = f"{name},{invoice},{bill_item}"
    invoices.append(first_row)

    # loop each item in invoice exclude the first one
    for i in range(1, bill_row_amount):
        bill_id = extract_id_from_screen(next_line(i, bill_id_start_region))
        if bill_id == "":
            break;
        
        if bill_id and bill_id[0] == "1":
             bill_id = f"I{bill_id[1:]}"
        
        bill_date = extract_text_from_screen(next_line(i, bill_date_start_region)).replace('/', '.')
        bill_type = extract_text_from_screen(next_line(i, bill_type_start_region))
        bill_price = extract_text_from_screen(next_line(i, bill_price_start_region)).replace(',', '')
        bill_item = f"{bill_id},{bill_date},{price_type(bill_type, bill_price)}"
        invoices.append(f",,{bill_item}")

    # add total price to last item before new line
    total_price = extract_text_from_screen(bill_total_price_region).replace(',', '')

    # Write the extracted text to a file
    with open(output_file, "a", encoding="utf-8") as file:
        file.write("\n".join(invoices) + f",{total_price}\n")

    # Click the button to access the next page
    pyautogui.click(next_page_button[0], next_page_button[1])

    # Wait for a short duration to allow the next page to load
    pyautogui.sleep(time_interval)

print("\nDone!")
ctypes.windll.user32.MessageBoxW(0, "เช็คให้ดีด้วย", "เสร็จแล้ว", 1)