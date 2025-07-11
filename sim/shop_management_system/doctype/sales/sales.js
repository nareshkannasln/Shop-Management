frappe.ui.form.on('Sales', {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button('Update Purchase', () => {
                let table_data = frm.doc.purchase.map(row => ({
                    item: row.item,
                    qty: row.qty,
                    rate: row.rate,
                    amount: row.amount
                }));

                let dialog = new frappe.ui.Dialog({
                    title: 'Edit Purchase Items',
                    fields: [
                        {
                            fieldname: 'purchase_items',
                            fieldtype: 'Table',
                            cannot_add_rows: false,
                            in_place_edit: true,
                            data: table_data,
                            fields: [
                                {
                                    label: 'Item',
                                    fieldname: 'item',
                                    fieldtype: 'Link',
                                    options: 'Item',
                                    in_list_view: true
                                },
                                {
                                    label: 'Qty',
                                    fieldname: 'qty',
                                    fieldtype: 'Int',
                                    in_list_view: true
                                },
                                {
                                    label: 'Rate',
                                    fieldname: 'rate',
                                    fieldtype: 'Currency',
                                    in_list_view: true
                                },
                                {
                                    label: 'Amount',
                                    fieldname: 'amount',
                                    fieldtype: 'Currency',
                                    in_list_view: true,
                                    read_only: 1
                                }
                            ]
                        }
                    ],
                    primary_action_label: 'Submit',
                    primary_action(values) {
                        frm.clear_table('purchase');
                        let total_amount = 0;

                        (values.purchase_items || []).forEach(row => {
                            let child = frm.add_child('purchase');
                            child.item = row.item;
                            child.qty = row.qty;
                            child.rate = row.rate;
                            child.amount = row.qty * row.rate || 0;
                            total_amount += child.amount;
                        });

                        frm.set_value('total_amount', total_amount);
                        frm.refresh_field('purchase');
                        frm.refresh_field('total_amount');

                        dialog.hide();

                        frm.save()
                            .then(() => {
                                frappe.call({
                                    method: 'sim.shop_management_system.doctype.sales.sales.submit_sales',
                                    args: {
                                        name: frm.doc.name
                                    },
                                    callback: function(r) {
                                        if (!r.exc) {
                                            frappe.msgprint(__('✅ Document submitted successfully'));
                                            frm.reload_doc();
                                        } else {
                                            frappe.msgprint(__('❌ Failed to submit document: ') + r.exc);
                                        }
                                    }
                                });
                            })
                            .catch(err => {
                                frappe.msgprint(__('❌ Save failed: ') + err.message);
                            });
                    }
                });

                dialog.show();
            });
        }
    }
});
