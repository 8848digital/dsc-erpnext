frappe.ui.form.on('Digital Signature', {
	setup: function(frm) {
		frm.set_query("document", function() {
			return {"filters": {
				'docstatus': 1
			}};
		});
	},
	before_workflow_action: function(frm){
		console.log('before')
		console.log(frm.doc.workflow_action)
	},
	after_workflow_action: function(frm){
		console.log(frm.doc.workflow_action)
		if(frm.doc.workflow_action != "Cancel"){
			frappe.call({
				'method': "dsc_erpnext.dsc_api.get_access_code",
				'args': {
					'doctype': frm.doc.doctype,
					'docname': frm.doc.name
				},
				freeze: true,
				freeze_message: __("Sending"),
				'callback': function(r){
					if(r.message){
						window.location.href = r.message
						//frappe.db.set_value(frm.doc.doctype, frm.doc.name, 'workflow_state',"DSC Completed")
					}
				},
				'error': function() {
					console.log('error')
				},
			})
		}
	}
});
