import io
from json import JSONDecodeError
import logging
from multiprocessing.sharedctypes import Value
import traceback

import azure.functions as func
import PyPDF2

# MIT License - https://opensource.org/licenses/MIT

# I want to limit cost in our environment and have set this to 10
# If you wish to disable just set this to a very high number
MAXIMUM_PAGES_TO_HANDLE = 10


def main(req: func.HttpRequest) -> func.HttpResponse:
    """

    This function reads the PDF file from the request body.
    It uses the password from the query string to encrypt and return the PDF.

    Args:
        req (func.HttpRequest): A request object from Azure HTTP Trigger.

    Returns:
        func.HttpResponse: An encrypted version of the PDF file, or an error.
    """
    try:
        pdf_to_protect = req.files.get("file")
        password = req.params.get("password")
        if not password:
            return func.HttpResponse(
                "Please provide a password in the query string",
                status_code=400,
            )

        if not pdf_to_protect:
            return func.HttpResponse(
                "Please pass a PDF file in the request body", status_code=400
            )

        input_pdf_bytes = io.BytesIO()
        pdf_to_protect.save(input_pdf_bytes)
        input_pdf_bytes.seek(0)

        try:
            input_pdf = PyPDF2.PdfFileReader(input_pdf_bytes)
            number_of_pages = input_pdf.numPages
        except PyPDF2.utils.PdfReadError:
            return func.HttpResponse(
                f"Unable to open: {pdf_to_protect.filename}. Is it a valid, non-encrypted PDF?",
                status_code=415,
            )

        if number_of_pages > MAXIMUM_PAGES_TO_HANDLE:
            return func.HttpResponse(
                f"PDF of size {number_of_pages} exceeds {MAXIMUM_PAGES_TO_HANDLE} pages allowed.",
                status_code=415,
            )
        output_pdf = PyPDF2.PdfFileWriter()
        for page in range(number_of_pages):
            output_pdf.addPage(input_pdf.getPage(page))
        output_pdf.encrypt(password)
        output_pdf_bytes = io.BytesIO()
        output_pdf.write(output_pdf_bytes)
        output_pdf_bytes.seek(0)
        return func.HttpResponse(
            body=output_pdf_bytes.read(),
            mimetype="application/pdf",
            headers={
                "Content-Disposition": "attachment",
                "filename": pdf_to_protect.filename,
            },
        )
    except Exception as e:
        logging.critical(f"Exception: {e}.\nTraceback: {traceback.format_exc()}")
        return func.HttpResponse(f"Unhandled Exception", status_code=500)
