import frappe
from frappe.desk.form.utils import get_pdf_link

def on_submit(self,method):
    documents = get_digital_signature_documents(self.doctype)
    if documents:
        for print_format,workflow in documents.items():
            doc = frappe.new_doc(f"DSC {self.doctype}")
            # doc = frappe.new_doc("Digital Signature")
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

def create_doctype(doctype):
    try:
        doc = frappe.new_doc("DocType")
        doc.editable_grid = 1
        doc.name = f"DSC {doctype}"
        a = doctype.split(" ")
        if len(a)>1:
            name = a[0][0]+a[1][0]
        else:
            name = a[0][0]
        doc.autoname = f"D-{name}-.####"
        doc.track_changes = 1
        doc.is_submittable = 1
        list = [{
                    "doctype": "DocField",
                    "fieldname": "document_type",
                    "fieldtype": "Link",
                    "label": "Document Type",
                    "options":"DocType"
                },
                {
                    "doctype": "DocField",
                    "fieldname": "document",
                    "fieldtype": "Dynamic Link",
                    "label": "Document",
                    "options":"document_type"
                },
                {
                    "doctype": "DocField",
                    "fieldname": "status",
                    "fieldtype": "Select",
                    "label": "Status",
                    "options": "\nPending\nPartially Signed\nCompleted\nCancelled",
                },
                {
                    "doctype": "DocField",
                    "fieldname": "print_format",
                    "fieldtype": "Link",
                    "label": "Print Format",
                    "options": "Print Format",
                },
                {
                    "doctype": "DocField",
                    "fieldname": "column_break",
                    "fieldtype": "Column Break"
                },
                {
                    "doctype": "DocField",
                    "fieldname": "pdf_document",
                    "fieldtype": "Attach",
                    "allow_on_submit": 1,
                    "label": "PDF Document"
                },
                {
                    "doctype": "DocField",
                    "fieldname": "amended_from",
                    "read_only":1,
                    "fieldtype": "Link",
                    "label": "Amended From",
                    "options": f"DSC {doctype}"
                },
                {
                    "doctype": "DocField",
                    "fieldname": "workflow_state",
                    "allow_on_submit": 1,
                    "hidden":1,
                    "no_copy": 1,
                    "fieldtype": "Data",
                    "label": "Workflow state"
                },
                {
                    "doctype": "DocField",
                    "fieldname": "workflow",
                    "fieldtype": "Data",
                    "label": "Workflow"
                },
                {
                    "doctype": "DocField",
                    "fieldname": "code",
                    "allow_on_submit": 1,
                    "hidden":1,
                    "fieldtype": "Small Text",
                    "label": "Code"
                },
                {
                    "doctype": "DocField",
                    "fieldname": "previous_state",
                    "fieldtype": "Data",
                    "read_only":1,
                    "hidden": 1,
                    "label": "Previous State",
                },
                {
                    "doctype": "DocField",
                    "fieldname": "section_break",
                    "fieldtype": "Section Break",
                    "label": "Other"
                },
                {
                    "doctype": "DocField",
                    "fieldname": "documents",
                    "fieldtype": "Table",
                    "allow_on_submit": 1,
                    "no_copy": 1,
                    "label": "Documents",
                    "options": "Digital Signature Signed Document",
                }]
        for item in list:
            doc.append("fields",item)
        doc.append("permissions",  {
                    "role": "System Manager",
                    "submit": 1,
                    "Cancel": 1
                    })
        doc.module="Dsc Erpnext"
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        return
    except Exception as e:
        frappe.logger("docusign").exception(e)