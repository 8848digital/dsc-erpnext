import frappe

def execute():
	doctype = "Sales Invoice"
	role = "Sales Manager"
	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = f"DSC : {doctype}"
	workflow.document_type = "Digital Signature"
	workflow.sent_email_alert = 0

	workflow_state_list = ["Submitted","Signatory1","Signatory2"]
	for state in workflow_state_list:
		if not frappe.db.exists("Workflow State",state):
			state_doc = frappe.new_doc("Workflow State")
			state_doc.workflow_state_name = state
			state_doc.save()
		
	workflow_action_list = ["DSC 1","DSC 2"]
	for action in workflow_action_list:
		if not frappe.db.exists("Workflow Action Master",action):
			action_doc = frappe.new_doc("Workflow Action Master")
			action_doc.workflow_action_name = action
			action_doc.save()

	for state in workflow_state_list:
		workflow.append("states",{
			"state": state,
			"doc_status": 1,
			"allow_edit": role
		})
	workflow.append("transitions",{
		"state": "Submitted",
		"action": "DSC 1",
		"next_state": "Signatory1",
		"allowed": role
	})
	workflow.append("transitions",{
		"state": "Signatory1",
		"action": "DSC 2",
		"next_state": "Signatory2",
		"allowed": role
	})
	workflow.save(ignore_permissions=True)


