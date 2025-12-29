$(document).ready(function () {

    console.log("invoice_dropdown.js loaded ✅");

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
            $('#id_invoice_order_date').val('');
            $('#id_invoice_service_date').val('');
            return;
        }

        fetch(`/invoices/get-invoice-data/${invoiceId}/`)
            .then(response => response.json())
            .then(data => {
                console.log("Invoice data:", data);
                $('#id_invoice_order_date').val(data.invoice_order_date);
                $('#id_invoice_service_date').val(data.invoice_service_date);
            })
            .catch(error => console.error("Fetch error:", error));
    });
});
