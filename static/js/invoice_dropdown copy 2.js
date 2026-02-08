// #######################################################
// static/js/invoice_dropdown.js
// Handles invoice selection:
// - loads invoice meta + customer info
// - loads invoice items
// - updates PDF button url
// #######################################################

$(document).ready(function () {
  console.log("invoice_dropdown.js loaded ✅");

  const pdfBtn = document.getElementById("pdf-btn");

  function setPdfButton(invoiceId) {
    if (!pdfBtn) return;

    if (!invoiceId) {
      pdfBtn.classList.add("disabled");
      pdfBtn.href = "#";
      return;
    }

    pdfBtn.classList.remove("disabled");
    pdfBtn.href = `/invoices/${invoiceId}/pdf/`;
  }

  // Lock/unlock invoice meta fields
  function lockInvoiceFields(lock) {
    $("#id_invoice_order_date").prop("disabled", lock);
    $("#id_invoice_service_date").prop("disabled", lock);
  }

  // Activate Select2 for invoice dropdown
  $("#invoice-select").select2({
    placeholder: "Rechnung auswählen",
    allowClear: true,
    width: "100%",
  });

  // When invoice selection changes
  $("#invoice-select").on("change", function () {
    const invoiceId = $(this).val();

    // ===============================
    // CLEARED SELECTION
    // ===============================
    if (!invoiceId) {
      lockInvoiceFields(false);

      if (typeof clearInvoiceItems === "function") clearInvoiceItems();
      if (typeof lockInvoiceItems === "function") lockInvoiceItems(false);

      // unlock VAT for new invoice
      $("#id_invoice_vat_percent").prop("disabled", false);

      $("#id_invoice_order_date").val("");
      $("#id_invoice_service_date").val("");

      // clear customer labels
      $("#customer_number, #customer_name, #customer_address, #customer_vehicle, #customer_license_plate, #customer_kilometers, #customer_created_at, #customer_updated_at").text("—");

      $("#add-item").show();

      // disable pdf button
      setPdfButton(null);
      return;
    }

    // enable pdf button
    setPdfButton(invoiceId);

    // ===============================
    // EXISTING INVOICE SELECTED
    // ===============================
    fetch(`/invoices/get_invoice_data/${invoiceId}/`)
      .then((res) => res.json())
      .then((data) => {
        // Lock invoice meta fields
        lockInvoiceFields(true);

        // Fill invoice dates
        $("#id_invoice_order_date").val(data.invoice_order_date);
        $("#id_invoice_service_date").val(data.invoice_service_date);

        // Fill customer display
        $("#customer_number").text(data.customer_number);
        $("#customer_name").text(data.customer_name);
        $("#customer_address").text(data.customer_address);
        $("#customer_vehicle").text(data.customer_vehicle);
        $("#customer_license_plate").text(data.customer_license_plate);
        $("#customer_kilometers").text(data.customer_kilometers);
        $("#customer_created_at").text(data.customer_created_at);
        $("#customer_updated_at").text(data.customer_updated_at);

        // Load invoice items (AJAX)
        if (typeof loadInvoiceItems === "function") loadInvoiceItems(invoiceId);

        // Hide add-row button (read-only mode)
        $("#add-item").hide();
      });
  });

  // initial state
  setPdfButton(null);
});
