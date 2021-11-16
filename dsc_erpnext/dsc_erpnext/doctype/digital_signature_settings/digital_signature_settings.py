# Copyright (c) 2021, Nirali Satapara and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DigitalSignatureSettings(Document):
	@frappe.whitelist()
	def create_workflows(self):
		workflow_state_list = ["DSC 1 Completed","DSC 2 Completed","DSC 3 Completed","DSC 4 Completed"]
		workflow_action_list = ["DSC 1","DSC 2","DSC 3","DSC 4"]
		default_workflow_state = ["Submitted","Cancelled"]
		
		for state in default_workflow_state:
			if not frappe.db.exists("Workflow State",state):
				state_doc = frappe.new_doc("Workflow State")
				state_doc.workflow_state_name = state
				state_doc.save()
		if not frappe.db.exists("Workflow Action Master","Cancel"):
			action_doc = frappe.new_doc("Workflow Action Master")
			action_doc.workflow_action_name = "Cancel"
			action_doc.save()

		for document in self.documents:
			if document.workflow:
				frappe.msgprint(f"Row {document.idx} : workflow exist.")
			if not document.workflow and frappe.db.exists("Workflow",f"DSC {document.entity_type}"):
				document.db_set('workflow', f"DSC {document.entity_type}")
			if not document.role_1 and not document.role_2 and not document.role_3 and not document.role_4:
				frappe.throw(f"Row {document.idx} : Please select role to create workflow")
			if document.entity_type and not frappe.db.exists("Workflow",f"DSC {document.entity_type}"):
				workflow = frappe.new_doc("Workflow")
				workflow.workflow_name = f"DSC {document.entity_type}"
				workflow.document_type = "Digital Signature"
				workflow.sent_email_alert = 0
			
				if document.role_1:
					if not frappe.db.exists("Workflow State",workflow_state_list[0]):
						state_doc = frappe.new_doc("Workflow State")
						state_doc.workflow_state_name = workflow_state_list[0]
						state_doc.save()
					if not frappe.db.exists("Workflow Action Master",workflow_action_list[0]):
						action_doc = frappe.new_doc("Workflow Action Master")
						action_doc.workflow_action_name = workflow_action_list[0]
						action_doc.save()
					workflow.append("states",{
						"state": "Submitted",
						"doc_status": 1,
						"allow_edit": document.role_1
					})
					workflow.append("states",{
						"state": workflow_state_list[0],
						"doc_status": 1,
						"allow_edit": document.role_1
					})
					workflow.append("states",{
						"state": "Cancelled",
						"doc_status": 2,
						"allow_edit": document.role_1
					})
					workflow.append("transitions",{
						"state": "Submitted",
						"action": workflow_action_list[0],
						"next_state": workflow_state_list[0],
						"allowed": document.role_1
					})
					workflow.append("transitions",{
						"state": "Submitted",
						"action": "Cancel",
						"next_state": "Cancelled",
						"allowed": document.role_1
					})

				if document.role_2:
					if not frappe.db.exists("Workflow State",workflow_state_list[1]):
						state_doc = frappe.new_doc("Workflow State")
						state_doc.workflow_state_name = workflow_state_list[1]
						state_doc.save()
					if not frappe.db.exists("Workflow Action Master",workflow_action_list[1]):
						action_doc = frappe.new_doc("Workflow Action Master")
						action_doc.workflow_action_name = workflow_action_list[1]
						action_doc.save()
					workflow.append("states",{
						"state": workflow_state_list[1],
						"doc_status": 1,
						"allow_edit": document.role_2
					})
					workflow.append("transitions",{
						"state": workflow_state_list[0],
						"action": workflow_action_list[1],
						"next_state": workflow_state_list[1],
						"allowed": document.role_2
					})
					workflow.append("transitions",{
						"state": workflow_state_list[0],
						"action": "Cancel",
						"next_state": "Cancelled",
						"allowed": document.role_2
					})

				if document.role_3:
					if not frappe.db.exists("Workflow State",workflow_state_list[2]):
						state_doc = frappe.new_doc("Workflow State")
						state_doc.workflow_state_name = workflow_state_list[2]
						state_doc.save()
					if not frappe.db.exists("Workflow Action Master",workflow_action_list[2]):
						action_doc = frappe.new_doc("Workflow Action Master")
						action_doc.workflow_action_name = workflow_action_list[2]
						action_doc.save()
					workflow.append("states",{
						"state": workflow_state_list[2],
						"doc_status": 1,
						"allow_edit": document.role_3
					})
					workflow.append("transitions",{
						"state": workflow_state_list[1],
						"action": workflow_action_list[2],
						"next_state": workflow_state_list[2],
						"allowed": document.role_3
					})
					workflow.append("transitions",{
						"state": workflow_state_list[1],
						"action": "Cancel",
						"next_state": "Cancelled",
						"allowed": document.role_3
					})

				if document.role_4:
					if not frappe.db.exists("Workflow State",workflow_state_list[3]):
						state_doc = frappe.new_doc("Workflow State")
						state_doc.workflow_state_name = workflow_state_list[3]
						state_doc.save()
					if not frappe.db.exists("Workflow Action Master",workflow_action_list[3]):
						action_doc = frappe.new_doc("Workflow Action Master")
						action_doc.workflow_action_name = workflow_action_list[3]
						action_doc.save()
					workflow.append("states",{
						"state": workflow_state_list[3],
						"doc_status": 1,
						"allow_edit": document.role_4
					})
					workflow.append("transitions",{
						"state": workflow_state_list[2],
						"action": workflow_action_list[3],
						"next_state": workflow_state_list[3],
						"allowed": document.role_4
					})
					workflow.append("transitions",{
						"state": workflow_state_list[2],
						"action": "Cancel",
						"next_state": "Cancelled",
						"allowed": document.role_4
					})
				
				workflow.save(ignore_permissions=True)
				print(workflow.name)
				document.db_set('workflow',workflow.name)
				
		frappe.db.commit()
		return "Workflow Created"


def get_digital_signature_documents(doctype):
	documents = frappe.db.sql(f"select print_format,workflow from `tabDigital Signature Document` where entity_type = '{doctype}'",as_dict=True)
	#document_list =  [d for document in documents for d in document]
	document_dict = {document.print_format:document.workflow for document in documents}
	return document_dict