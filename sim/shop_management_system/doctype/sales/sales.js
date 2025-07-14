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
                    primary_action_label: 'Update',
                    primary_action(values) {
                        frm.clear_table('purchase');
                        let total_amount = 0;

                        (values.purchase_items || []).forEach(row => {
                            let child = frm.add_child('purchase');
                            child.item = row.item;
                            child.qty = row.qty;
                            child.rate = row.rate;
                            child.amount = (row.qty || 0) * (row.rate || 0);
                            total_amount += child.amount;
                        });

                        frm.set_value('total_amount', total_amount);
                        frm.refresh_field('purchase');
                        frm.refresh_field('total_amount');

                        frappe.call({
                            method: 'sim.shop_management_system.doctype.sales.sales.edit_and_resubmit',
                            args: {
                                docname: frm.doc.name,
                                sales_items: JSON.stringify(values.purchase_items)
                            },
                            callback(r) {
                                if (!r.exc) {
                                    frappe.msgprint(__('Purchase items updated successfully'));
                                    frm.reload_doc();
                                    dialog.hide();
                                }
                            }
                        });
                    }
                });

                dialog.show();
            });
        }
    }
});
