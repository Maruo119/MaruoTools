#pip install PyMuPDF requests
import requests
import fitz  # PyMuPDF

def download_and_extract_pdf(url, output_pdf_name):
    # PDFファイルをダウンロード
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_pdf_name, "wb") as file:
            file.write(response.content)
        print(f"Downloaded PDF to {output_pdf_name}")
    else:
        print(f"Failed to download PDF. Status code: {response.status_code}")
        return

    # PDFからテキストを抽出
    doc = fitz.open(output_pdf_name)
    extracted_text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        extracted_text += page.get_text() + "\n"
    doc.close()

    return extracted_text

# PDFのURL
pdf_url = "https://www2.axa.co.jp/digitalprovision/pdf/0T0715_170.pdf"
output_pdf_name = "downloaded_pdf.pdf"

# 実行
text = download_and_extract_pdf(pdf_url, output_pdf_name)
if text:
    print("Extracted Text:")
    print(text[:1000])  # 1000文字だけ表示

    # 翻訳した内容を新しいファイルに保存
    with open("text_data_from_PDF.txt", "w", encoding="utf-8") as file:
        file.write(text)
