// sales.js (Client Script for Sales doctype)
frappe.ui.form.on('Sales', {
    refresh(frm) {
        // Add a custom button in the form
        frm.add_custom_button(__('Edit Items'), () => {
            // Build a dialog with a Table field for child items
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
                            // Hidden field to store the child row name (primary key)
                            { fieldtype: 'Data', fieldname: 'name', hidden: 1 },
                            { fieldtype: 'Link', fieldname: 'item', label: __('Item'), options: 'Item', in_list_view: 1 },
                            { fieldtype: 'Float', fieldname: 'qty', label: __('Quantity'), default: 0, in_list_view: 1 },
                            { fieldtype: 'Currency', fieldname: 'rate', label: __('Rate'), default: 0, in_list_view: 1 }
                        ],
                        reqd: 1
                    }
                ],
                primary_action_label: __('Update'),
                primary_action(values) {
                    // Send the updated items to the server-side method
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
                    dialog.hide();
                }
            });

            // Pre-populate dialog with existing child table rows
            frm.doc.purchase.forEach(row => {
                dialog.fields_dict.items.df.data.push({
                    name: row.name,   // preserve the row name
                    item: row.item,
                    qty: row.qty,
                    rate: row.rate
                });
            });
            dialog.fields_dict.items.df.data = dialog.fields_dict.items.df.data;
            dialog.fields_dict.items.grid.refresh();
            dialog.show();
        });
    }
});
