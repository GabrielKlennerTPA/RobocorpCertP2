from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    orders = get_orders()
    
    open_robot_order_website()
    for row in orders:
        close_annoying_modal()
        fill_the_form(row)
        submit_order()
        store_receipt_as_pdf(row["Order number"])
        start_next_order()
    archive_receipts()

    


def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def close_annoying_modal():
    page = browser.page()
    page.click("button:text('OK')")

def get_orders():
    http = HTTP()
    tables = Tables()

    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    return tables.read_table_from_csv("orders.csv", header=True)

def fill_the_form(row):
    head = int(row["Head"])
    body = int(row["Body"])
    legs = int(row["Legs"])
    address = row["Address"]
    
    page = browser.page()
    page.locator("#head").select_option(index=head)

    page.locator("#id-body-"+str(body)).click()
    page.locator("input[placeholder=\"Enter the part number for the legs\"]").fill(str(legs))
    page.locator("input[placeholder=\"Shipping address\"]").fill(str(address))

def submit_order():
    page = browser.page()
    for _ in range(20): # 20 retries maximum
        page.locator("#order").click()
        if(page.locator(".alert-danger").count() == 0):
            break
        


def store_receipt_as_pdf(order_nr):
    page = browser.page()
    pdf_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    output_path = f"output/receipt_{order_nr}.pdf"
    preview_path = f"output/preview_{order_nr}.png"
    pdf.html_to_pdf(pdf_html, output_path)
    page.locator("#robot-preview-image").screenshot(path=preview_path)
    pdf.add_files_to_pdf([preview_path], target_document=output_path, append=True)

def start_next_order():
    page = browser.page()
    page.locator("#order-another").click()

def archive_receipts():
    archive = Archive()
    archive.archive_folder_with_zip("output/", "output/receipts.zip", include="*.pdf")