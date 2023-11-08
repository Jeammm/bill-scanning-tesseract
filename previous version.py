#https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.1.20230401.exe

import pyautogui
import pytesseract
import keyboard
import os

os.environ["TESSDATA_PREFIX"] = "Tesseract-OCR/tessdata"

def extract_text_from_screen(region):
    screenshot = pyautogui.screenshot()
    screenshot = screenshot.crop(region)
    custom_config = r'--psm 6'
    text = pytesseract.image_to_string(screenshot, config=custom_config)
    return text.strip()

def extract_text_from_screen_thai(region):
    screenshot = pyautogui.screenshot()
    screenshot = screenshot.crop(region)
    custom_config = r'-l tha --psm 6'
    text = pytesseract.image_to_string(screenshot, config=custom_config)
    return "".join(text.strip().split(" "))

pytesseract.pytesseract.tesseract_cmd = "Tesseract-OCR/tesseract.exe"

# Set the coordinates of the specific section you want to scan

customer_id_region = (87, 107, 181, 123) # (left, top, width, height)
customer_name_region = (30, 128, 932, 148)

invoice_id_region = (1081, 133, 1179, 146)

bill_id_start_region = (31, 276, 148, 299)
bill_date_start_region = (151, 276, 226, 299)
bill_type_start_region = (316, 276, 341, 299)
bill_price_start_region = (1518, 276, 1638, 299)
bill_total_price_region = (1770, 981, 1872, 999)
bill_row_amount = 28

first_row = [invoice_id_region, bill_id_start_region, bill_date_start_region, bill_type_start_region, bill_price_start_region]

# Set the coordinates of the button to access the next page
# next_page_button = (312, 50)  # (x, y)
next_page_button = (1901, 538)  # (x, y)

output_file = "extracted_text.txt"


running = True

def stop_program():
    global running
    running = False

keyboard.add_hotkey("Ctrl+Shift+S", stop_program)

def price_type(bill_type, bill_price):
    if bill_type == 'mk':
        return f'{bill_price},,'
    elif bill_type == 'o':
        return f',,{bill_price}'
    else:
        return f',{bill_price},'
    
def next_line(i, region):
    bill_row_size = 25
    return (region[0], region[1] + bill_row_size*i, region[2], region[3] + bill_row_size*i)

# Loop until the program is stopped manually
while running:
    print("Runnning...")
    # Extract text from the specified region
    name = extract_text_from_screen_thai(customer_name_region)
    invoice = extract_text_from_screen(invoice_id_region)

    bill_id = extract_text_from_screen(bill_id_start_region)
    bill_date = extract_text_from_screen(bill_date_start_region)
    bill_type = extract_text_from_screen(bill_type_start_region)
    bill_price = extract_text_from_screen(bill_price_start_region).replace(',', '')

    bill_item = f"{bill_id},{bill_date},{price_type(bill_type, bill_price)}"

    invoices = []
    first_row = f"{name},{invoice},{bill_item}"
    invoices.append(first_row)

    for i in range(1, bill_row_amount):
        bill_id = extract_text_from_screen(next_line(i, bill_id_start_region))
        if bill_id == "":
            break;
        
        bill_date = extract_text_from_screen(next_line(i, bill_date_start_region))
        bill_type = extract_text_from_screen(next_line(i, bill_type_start_region))
        bill_price = extract_text_from_screen(next_line(i, bill_price_start_region)).replace(',', '')
        bill_item = f"{bill_id},{bill_date},{price_type(bill_type, bill_price)}"
        invoices.append(f",,{bill_item}")

    total_price = extract_text_from_screen(bill_total_price_region).replace(',', '')

    # Write the extracted text to a file
    print(invoices)
    with open(output_file, "a", encoding="utf-8") as file:
        file.write("\n".join(invoices) + f",{total_price}\n")

    # Click the button to access the next page
    pyautogui.click(next_page_button[0], next_page_button[1])

    # Wait for a short duration to allow the next page to load
    pyautogui.sleep(1)