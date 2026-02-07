// #######################################################
// static/js/invoice_dropdown.js
// invoice_dropdown.js
// Handles ONLY invoice selection + meta/customer loading
// #######################################################

$(document).ready(function () {

    console.log("invoice_dropdown.js loaded ✅");

    // Lock/unlock invoice meta fields
    function lockInvoiceFields(lock) {
        $('#id_invoice_order_date').prop('disabled', lock);
        $('#id_invoice_service_date').prop('disabled', lock);
    }

    // Activate Select2 for invoice dropdown
    $('#invoice-select').select2({
        placeholder: "Rechnung auswählen",
        allowClear: true,
        width: '100%'
    });

    // When invoice selection changes
    $('#invoice-select').on('change', function () {

        const invoiceId = $(this).val();

        // ===============================
        // NEW INVOICE / CLEARED SELECTION
        // ===============================
        if (!invoiceId) {
            lockInvoiceFields(false);

            clearInvoiceItems();
            lockInvoiceItems(false);

            // 🔓 UNLOCK VAT FOR NEW INVOICE
            $('#id_invoice_vat_percent').prop('disabled', false);

            $('#id_invoice_order_date').val('');
            $('#id_invoice_service_date').val('');

            $('#customer_number, #customer_name, #customer_address, #customer_vehicle, \
                #customer_license_plate, #customer_kilometers, #customer_created_at, \
                #customer_updated_at').text('—');

            $('#add-item').show();
            return;
        }


        // ===============================
        // EXISTING INVOICE SELECTED
        // ===============================
        fetch(`/invoices/get_invoice_data/${invoiceId}/`)
            .then(res => res.json())
            .then(data => {

                // Lock invoice meta fields
                lockInvoiceFields(true);

                // Fill invoice dates
                $('#id_invoice_order_date').val(data.invoice_order_date);
                $('#id_invoice_service_date').val(data.invoice_service_date);

                // Fill customer info
                $('#customer_number').text(data.customer_number);
                $('#customer_name').text(data.customer_name);
                $('#customer_address').text(data.customer_address);
                $('#customer_vehicle').text(data.customer_vehicle);
                $('#customer_license_plate').text(data.customer_license_plate);
                $('#customer_kilometers').text(data.customer_kilometers);
                $('#customer_created_at').text(data.customer_created_at);
                $('#customer_updated_at').text(data.customer_updated_at);

                // Load invoice items (AJAX)
                loadInvoiceItems(invoiceId);

                // Hide add-row button (read-only mode)
                $('#add-item').hide();
            });
    });
});
