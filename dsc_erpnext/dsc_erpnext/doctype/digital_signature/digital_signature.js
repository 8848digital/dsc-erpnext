frappe.ui.form.on('Digital Signature', {
	setup: function(frm) {
		frm.set_query("entity", function() {
			return {"filters": {
				'docstatus': 1
			}};
		});
	},
	
	before_workflow_action: function(frm){
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
					}
				}
			})
		}
	}
});
