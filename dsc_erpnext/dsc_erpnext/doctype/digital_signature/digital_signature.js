frappe.ui.form.on('Digital Signature', {
	setup: function(frm) {
		frm.set_query("entity", function() {
			return {"filters": {
				'docstatus': 1
			}};
		});
	},
	
	after_workflow_action: function(frm){
		let workflow_state = frm.doc.workflow_state
		console.log(workflow_state)
		if(frm.doc.workflow_action != "Cancel"){
			frappe.call({
				'method': "dsc_erpnext.dsc_api.get_access_code",
				'args': {
					'doctype': frm.doc.doctype,
					'docname': frm.doc.name
				},
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
