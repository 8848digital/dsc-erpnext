import frappe
from dsc_erpnext.dsc_erpnext.doctype.digital_signature_settings.digital_signature_settings import get_digital_signature_documents
from frappe.desk.form.utils import get_pdf_link

def validate(self,method):
	documents = get_digital_signature_documents(self.doctype)
	if documents:
		for document in documents:
			doc = frappe.new_doc("Digital signature")
			doc.entity_type = self.doctype
			doc.entity = self.name
			doc.pdf_document = get_pdf_link(self.doctype, self.name, document)
			doc.save()


