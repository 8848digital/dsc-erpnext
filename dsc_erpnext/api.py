import frappe
from frappe.desk.form.utils import get_pdf_link

def on_submit(self,method):
	documents = get_digital_signature_documents(self.doctype)
	if documents:
		for print_format,workflow in documents.items():
			doc = frappe.new_doc("Digital Signature")
			doc.document_type = self.doctype
			doc.document = self.name
			doc.print_format = print_format
			doc.workflow = workflow
			doc.pdf_document = get_pdf_link(self.doctype, self.name, print_format)
			doc.save()
			doc.submit()

def get_digital_signature_documents(doctype):
	documents = frappe.db.sql(f"select print_format,workflow from `tabDigital Signature Document` where document_type = '{doctype}'",as_dict=True)
	#document_list =  [d for document in documents for d in document]
	document_dict = {document.print_format:document.workflow for document in documents}
	return document_dict