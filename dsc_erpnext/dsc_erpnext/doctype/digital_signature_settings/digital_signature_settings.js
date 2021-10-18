// Copyright (c) 2021, Nirali Satapara and contributors
// For license information, please see license.txt
cur_frm.set_query("print_format", "documents", function(doc, cdt, cdn) {
	var d = locals[cdt][cdn];
	return{
		filters: {
			'doc_type': d.entity_type
		}
	}
});
frappe.ui.form.on('Digital Signature Settings', {
	// refresh: function(frm) {

	// }
});
