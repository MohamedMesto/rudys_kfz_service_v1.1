// ########################################################
// invoice_items_loader.js
// Loads invoice items and rebuilds formset (readonly)
// ########################################################

function clearInvoiceItems() {
    const tbody = document.getElementById('invoice-items-body');
    tbody.innerHTML = '';
    document.querySelector('input[name$="TOTAL_FORMS"]').value = 0;
}

function lockInvoiceItems(lock = true) {
    document.querySelectorAll(
        '#invoice-items-body select, #invoice-items-body input'
    ).forEach(el => {
        el.disabled = lock;
    });
}


function loadInvoiceItems(invoiceId) {

    clearInvoiceItems();

    fetch(`/invoices/get-invoice-items/${invoiceId}/`)
        .then(res => res.json())
        .then(data => {

            if (!data || !Array.isArray(data.items)) {
                console.error('Invalid invoice items payload', data);
                return;
            }

            const tbody = document.getElementById('invoice-items-body');
            const totalFormsInput = document.querySelector('input[name$="TOTAL_FORMS"]');

            data.items.forEach((item, index) => {

                const row = document.getElementById('empty-form-row').cloneNode(true);
                row.classList.remove('d-none');
                row.removeAttribute('id');

                row.innerHTML = row.innerHTML.replace(/__prefix__/g, index);
                tbody.appendChild(row);

                const select = row.querySelector('select.diagnosis-select');

                // Set value FIRST
                select.value = item.diagnosis_id;

                // Initialize Select2 ONCE
                $(select).select2({ width: '100%' });

                // Set other values
                row.querySelector('input[name$="quantity"]').value = item.quantity;
                row.querySelector('input[name$="unit_price"]').value = item.unit_price;
                row.querySelector('.item-total').textContent =
                    parseFloat(item.line_total).toFixed(2) + ' €';
            });

            totalFormsInput.value = data.items.length;

            // ===============================
            // UPDATE TOTALS (READONLY DISPLAY)
            // ===============================
            $('#subtotal').text(parseFloat(data.subtotal).toFixed(2) + ' €');
            $('#id_invoice_vat_percent').val(data.vat_percent).prop('disabled', true);
            $('#vat-amount').text(parseFloat(data.vat_amount).toFixed(2) + ' €');
            $('#grand-total').text(parseFloat(data.grand_total).toFixed(2) + ' €');

            // 🔒 lock editing
            lockInvoiceItems(true);
        });
}

// function loadInvoiceItems(invoiceId) {

//     clearInvoiceItems();

//     fetch(`/invoices/get-invoice-items/${invoiceId}/`)
//         .then(res => res.json())
//         .then(data => {

//             if (!data || !Array.isArray(data.items)) {
//                 console.error('Invalid invoice items payload', data);
//                 return;
//             }

//             const tbody = document.getElementById('invoice-items-body');
//             const totalFormsInput = document.querySelector('input[name$="TOTAL_FORMS"]');

//             data.items.forEach((item, index) => {

//                 const row = document.getElementById('empty-form-row').cloneNode(true);
//                 row.classList.remove('d-none');
//                 row.removeAttribute('id');

//                 row.innerHTML = row.innerHTML.replace(/__prefix__/g, index);
//                 tbody.appendChild(row);

//                 const select = row.querySelector('select.diagnosis-select');

//                 // Set value FIRST
//                 select.value = item.diagnosis_id;

//                 // Initialize Select2 ONCE
//                 $(select).select2({ width: '100%' });

//                 // Set other values
//                 row.querySelector('input[name$="quantity"]').value = item.quantity;
//                 row.querySelector('input[name$="unit_price"]').value = item.unit_price;

//                 row.querySelector('.item-total').textContent =
//                     parseFloat(item.line_total).toFixed(2) + ' €';

//             });

//             totalFormsInput.value = data.items.length;

//             // ===============================
//             // UPDATE TOTALS (READONLY DISPLAY)
//             // ===============================
//             $('#subtotal').text(parseFloat(data.subtotal).toFixed(2) + ' €');
//             $('#id_invoice_vat_percent').val(data.vat_percent).prop('disabled', true);
//             $('#vat-amount').text(parseFloat(data.vat_amount).toFixed(2) + ' €');
//             $('#grand-total').text(parseFloat(data.grand_total).toFixed(2) + ' €');

//             // 🔒 lock editing
//             lockInvoiceItems(true);
//         });
// }
