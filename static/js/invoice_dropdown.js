$(document).ready(function () {

    console.log("invoice_dropdown.js loaded ✅");

    // 🔒 NEXT STEP (2): Lock fields when existing invoice selected

    function lockInvoiceFields(lock) {
        $('#id_invoice_order_date').prop('readonly', lock);
        $('#id_invoice_service_date').prop('readonly', lock);
    }

    // Activate Select2
    $('#invoice-select').select2({
        placeholder: "Rechnung auswählen",
        allowClear: true,
        width: '100%'
    });

    // On change → fetch invoice data
    $('#invoice-select').on('change', function () {

        const invoiceId = $(this).val();
        console.log("Selected invoice:", invoiceId);

        if (!invoiceId) {
            lockInvoiceFields(false);
            $('#id_invoice_order_date').val('');
            $('#id_invoice_service_date').val('');

            // clear customer info
            $('#customer_number').text('—');
            $('#customer_name').text('—');
            $('#customer_address').text('—');
            $('#customer_vehicle').text('—');
            $('#customer_license_plate').text('—');
            $('#customer_kilometers').text('—');
            $('#customer_created_at').text('—');
            $('#customer_updated_at').text('—');

            return;
        }


        fetch(`/invoices/get-invoice-data/${invoiceId}/`)
            .then(response => response.json())
            .then(data => {
                  // invoice dates
                lockInvoiceFields(true);
                console.log("Invoice data:", data);
                $('#id_invoice_order_date').val(data.invoice_order_date);
                $('#id_invoice_service_date').val(data.invoice_service_date);
 
   
                // customer info
                $('#customer_number').text(data.customer_number);
                $('#customer_name').text(data.customer_name);
                $('#customer_address').text(data.customer_address);
                $('#customer_vehicle').text(data.customer_vehicle);
                $('#customer_license_plate').text(data.customer_license_plate);
                $('#customer_kilometers').text(data.customer_kilometers);
                $('#customer_created_at').text(data.customer_created_at);
                $('#customer_updated_at').text(data.customer_updated_at);

            })
            .catch(error => console.error("Fetch error:", error));
    });
});



if (invoiceId) {
    lockInvoiceFields(true);
} else {
    lockInvoiceFields(false);
}


