frappe.ui.form.on('Sales', {
	refresh(frm) {
		frm.add_custom_button(__('Edit Items'), () => {
			let dialog = new frappe.ui.Dialog({
				title: __('Edit Sales Items'),
				fields: [
					{
						fieldname: 'items',
						label: __('Items'),
						fieldtype: 'Table',
						in_place_edit: true,
						data: [],
						fields: [
							{ fieldtype: 'Data', fieldname: 'name', hidden: 1 },
							{ fieldtype: 'Link', fieldname: 'item', label: __('Item'), options: 'Item', in_list_view: 1 },
							{ fieldtype: 'Int', fieldname: 'qty', label: __('Quantity'), default: 0, in_list_view: 1 },
							{ fieldtype: 'Currency', fieldname: 'rate', label: __('Rate'), default: 0, in_list_view: 1 },
							{ fieldtype: 'Currency', fieldname: 'amount', label: __('Amount'), read_only: 1, in_list_view: 1 }
						],
						reqd: 1
					}
				],
				primary_action_label: __('Update'),
				primary_action(values) {
					frappe.call({
						method: 'sim.shop_management_system.doctype.sales.sales.edit_and_resubmit',
						args: {
							docname: frm.doc.name,
							updated_items: values.items
						},
						callback: (r) => {
							if (!r.exc) {
								frappe.msgprint(__("Sales items updated successfully"));
								frm.reload_doc();
							}
						}
					});
					cur_dialog.hide();
				}
			});

			frm.doc.purchase.forEach(row => {
				dialog.fields_dict.items.df.data.push({
					name: row.name,
					item: row.item,
					qty: row.qty,
					rate: row.rate,
					amount: row.qty * row.rate
				});
			});

			dialog.fields_dict.items.df.data = dialog.fields_dict.items.df.data;
			dialog.fields_dict.items.grid.refresh();

			dialog.fields_dict.items.grid.wrapper.on('change', function () {
				cur_dialog.fields_dict.items.grid.grid_rows.forEach(grid_row => {
					let data = grid_row.doc;
					let qty = parseFloat(data.qty) || 0;
					let rate = parseFloat(data.rate) || 0;
					let amount = qty * rate;
					data.amount = amount;
					grid_row.refresh();  
				});
			});

			dialog.show();
		});
	}
});
