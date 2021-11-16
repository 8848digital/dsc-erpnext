import frappe
from dsc_erpnext.dsc_erpnext.doctype.digital_signature_settings.digital_signature_settings import get_digital_signature_documents
from frappe.desk.form.utils import get_pdf_link

def validate(self,method):
	documents = get_digital_signature_documents(self.doctype)
	if documents:
		for print_format,workflow in documents.items():
			doc = frappe.new_doc("Digital Signature")
			doc.entity_type = self.doctype
			doc.entity = self.name
			doc.workflow = workflow
			doc.pdf_document = get_pdf_link(self.doctype, self.name, print_format)
			doc.save()


