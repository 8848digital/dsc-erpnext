frappe.ui.form.on('Digital signature', {
	setup: function(frm) {
		frm.set_query("entity", function() {
			return {"filters": {
				'docstatus': 1
			}};
		});
	}
});
