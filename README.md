1) Install Tesseract OCR
ไปที่ [Tesseract OCR](https://link-url-here.org) แล้วติดตั้งไฟล์บนโฟล์เดอร์นี้

3) Activate Python Environment
เปิด terminal โดยการกด Win+R แล้วพิมพ์ cmd จากนั้นกด Enter แล้วพิมพ์คำสั่ง
```.\myenv\Scripts\activate```
=> ถ้าพิมพ์แล้วขึ้นตัวแดงให้พิมพ์อันนี้ก่อน
```Set-ExecutionPolicy Unrestricted -Force```
=> แล้วตามด้วยอันนี้
```.\myenv\Scripts\activate```

5) Install dependencies
```pip install -r requirements.txt```

6) Start the program
เปิดหน้าบิลเริ่มต้นของ ExpressAudit
```python main.py```
ทำตามคำสั่งใน CLI
เมื่อเสร็จสิ้นจะได้ไฟล์ extracted_text.txt

