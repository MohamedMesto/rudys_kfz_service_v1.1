//  rudys_kfz_service_v1.1/static/js/invoice_dropdown.js 
// invoice_dropdown.js (ONLY invoice selection)
// #######################################################
$(document).ready(function () {

    console.log("invoice_dropdown.js loaded ✅");

    function lockInvoiceFields(lock) {
        $('#id_invoice_order_date').prop('disabled', lock);
        $('#id_invoice_service_date').prop('disabled', lock);
    }

    $('#invoice-select').select2({
        placeholder: "Rechnung auswählen",
        allowClear: true,
        width: '100%'
    });

    $('#invoice-select').on('change', function () {

        const invoiceId = $(this).val();

        if (!invoiceId) {
            lockInvoiceFields(false);
            $('#id_invoice_order_date').val('');
            $('#id_invoice_service_date').val('');

            $('#customer_number, #customer_name, #customer_address, #customer_vehicle, \
               #customer_license_plate, #customer_kilometers, #customer_created_at, \
               #customer_updated_at').text('—');
            return;
        }

        fetch(`/invoices/get-invoice-data/${invoiceId}/`)
            .then(res => res.json())
            .then(data => {
                lockInvoiceFields(true);

                $('#id_invoice_order_date').val(data.invoice_order_date);
                $('#id_invoice_service_date').val(data.invoice_service_date);

                $('#customer_number').text(data.customer_number);
                $('#customer_name').text(data.customer_name);
                $('#customer_address').text(data.customer_address);
                $('#customer_vehicle').text(data.customer_vehicle);
                $('#customer_license_plate').text(data.customer_license_plate);
                $('#customer_kilometers').text(data.customer_kilometers);
                $('#customer_created_at').text(data.customer_created_at);
                $('#customer_updated_at').text(data.customer_updated_at);
            });
    });
});

