// #######################################################
// static/js/invoice_dropdown.js
//
// Handles invoice selection:
// - loads invoice meta + customer info
// - loads invoice items
// - locks/unlocks fields
// - disables customer select for existing invoices
// - disables Save for existing invoices
// - updates PDF button URL
// #######################################################

$(document).ready(function () {
  console.log("invoice_dropdown.js loaded ✅");

  const pdfBtn = document.getElementById("pdf-btn");

  const $customerSelect = $("#customer-select");
  const $saveBtn = $("#save-btn");

  // -----------------------------------------------------
  // Disable/enable Save button
  // -----------------------------------------------------
  function lockSave(lock) {
    if (!$saveBtn.length) return;
    $saveBtn.prop("disabled", lock);
  }

  // -----------------------------------------------------
  // PDF button handler
  // -----------------------------------------------------
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

  // -----------------------------------------------------
  // Lock/unlock invoice meta fields
  // -----------------------------------------------------
  function lockInvoiceFields(lock) {
    $("#id_invoice_order_date").prop("disabled", lock);
    $("#id_invoice_service_date").prop("disabled", lock);
  }

  // -----------------------------------------------------
  // Enable / disable customer selection (Select2-safe)
  // -----------------------------------------------------
  function lockCustomerSelect(lock) {
    if (!$customerSelect.length) return;

    $customerSelect.prop("disabled", lock);

    // If Select2 is active, it will reflect disabled state
    if ($customerSelect.data("select2")) {
      $customerSelect.trigger("change"); // refresh UI
    }
  }

  // -----------------------------------------------------
  // Activate Select2 for invoice dropdown (if present)
  // -----------------------------------------------------
  if ($("#invoice-select").length && typeof $.fn.select2 !== "undefined") {
    $("#invoice-select").select2({
      placeholder: "Rechnung auswählen",
      allowClear: true,
      width: "100%",
    });
  }

  // -----------------------------------------------------
  // Invoice selection change
  // -----------------------------------------------------
  $("#invoice-select").on("change", function () {
    const invoiceId = $(this).val();

    // ===============================
    // CLEARED SELECTION → NEW INVOICE
    // ===============================
    if (!invoiceId) {
      lockInvoiceFields(false);
      lockCustomerSelect(false);
      lockSave(false);

      if (typeof clearInvoiceItems === "function") clearInvoiceItems();
      if (typeof lockInvoiceItems === "function") lockInvoiceItems(false);

      // unlock VAT for new invoice
      $("#id_invoice_vat_percent").prop("disabled", false);

      $("#id_invoice_order_date").val("");
      $("#id_invoice_service_date").val("");

      // clear customer display
      $("#customer_number, #customer_name, #customer_address, #customer_vehicle, \
        #customer_license_plate, #customer_kilometers, #customer_created_at, \
        #customer_updated_at").text("—");

      $("#add-item").show();
      setPdfButton(null);
      return;
    }

    // ===============================
    // EXISTING INVOICE SELECTED
    // ===============================
    setPdfButton(invoiceId);
    lockCustomerSelect(true);
    lockSave(true);

    fetch(`/invoices/get_invoice_data/${invoiceId}/`)
      .then((res) => res.json())
      .then((data) => {
        // lock invoice meta
        lockInvoiceFields(true);

        // fill invoice dates
        $("#id_invoice_order_date").val(data.invoice_order_date);
        $("#id_invoice_service_date").val(data.invoice_service_date);

        // fill customer display (READ ONLY)
        $("#customer_number").text(data.customer_number);
        $("#customer_name").text(data.customer_name);
        $("#customer_address").text(data.customer_address);
        $("#customer_vehicle").text(data.customer_vehicle);
        $("#customer_license_plate").text(data.customer_license_plate);
        $("#customer_kilometers").text(data.customer_kilometers);
        $("#customer_created_at").text(data.customer_created_at);
        $("#customer_updated_at").text(data.customer_updated_at);

        // load invoice items
        if (typeof loadInvoiceItems === "function") loadInvoiceItems(invoiceId);

        // hide add-row button (read-only)
        $("#add-item").hide();
      })
      .catch((err) => console.error("Failed to load invoice data", err));
  });

  // -----------------------------------------------------
  // Initial state on page load
  // -----------------------------------------------------
  lockSave(false);
  lockCustomerSelect(false);
  setPdfButton(null);
});
