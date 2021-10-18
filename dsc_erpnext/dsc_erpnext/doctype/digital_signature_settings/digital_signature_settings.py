# Copyright (c) 2021, Nirali Satapara and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DigitalSignatureSettings(Document):
	pass


def get_digital_signature_documents(doctype):
	documents = frappe.db.sql(f"select print_format from `tabDigital signature Document` where entity_type = '{doctype}'",as_list=True)
	document_list =  [d for document in documents for d in document]
	return document_list