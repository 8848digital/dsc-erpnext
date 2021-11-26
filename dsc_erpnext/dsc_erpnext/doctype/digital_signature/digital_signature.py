# Copyright (c) 2021, Nirali Satapara and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DigitalSignature(Document):
	def validate(self):
		if self.entity_type and not frappe.db.exists("Custom Field",{'dt':self.entity_type,'fieldname':'dsc_status'}):
			status = frappe.new_doc("Custom Field")
			status.dt = self.entity_type
			status.label = 'DSC Status'
			status.fieldname = 'dsc_status'
			status.fieldtype = "Data"
			status.allow_on_submit = 1
			status.read_only = 1
			status.no_copy = 1 
			status.save()

