# Copyright (c) 2021, Nirali Satapara and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DigitalSignatureSettings(Document):
	pass


def get_digital_signature_documents(doctype):
	documents = frappe.db.sql(f"select print_format,workflow from `tabDigital Signature Document` where entity_type = '{doctype}'",as_dict=True)
	#document_list =  [d for document in documents for d in document]
	document_dict = {document.print_format:document.workflow for document in documents}
	return document_dict