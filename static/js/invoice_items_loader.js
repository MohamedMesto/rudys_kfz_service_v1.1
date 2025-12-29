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

            const tbody = document.getElementById('invoice-items-body');
            const totalFormsInput = document.querySelector('input[name$="TOTAL_FORMS"]');

            data.items.forEach((item, index) => {

                const row = document.getElementById('empty-form-row').cloneNode(true);
                row.classList.remove('d-none');
                row.removeAttribute('id');

                row.innerHTML = row.innerHTML.replace(/__prefix__/g, index);
                tbody.appendChild(row);

                // Set values
                row.querySelector('select').value = item.diagnosis_id;
                row.querySelector('input[name$="quantity"]').value = item.quantity;
                row.querySelector('input[name$="unit_price"]').value = item.unit_price;
                row.querySelector('.item-total').textContent = item.line_total + ' €';

                // Activate Select2
                $(row).find('.diagnosis-select').select2({
                    width: '100%'
                });
            });

            totalFormsInput.value = data.items.length;

            // 🔒 lock editing
            lockInvoiceItems(true);
        });
}
