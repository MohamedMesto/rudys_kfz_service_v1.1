// #######################################################
// static/js/invoice_dropdown.js
//
// Handles invoice selection:
// - loads invoice meta + customer info
// - loads invoice items
// - locks/unlocks fields
// - disables customer select for existing invoices
// - disables save for existing invoices
// - updates PDF buttons URLs
// #######################################################

$(document).ready(function () {
  console.log("invoice_dropdown.js loaded ✅");

  const pdfBtnHtml = document.getElementById("pdf-btn-html"); // WeasyPrint
  const pdfBtnRl = document.getElementById("pdf-btn-rl");     // ReportLab
  const customerSelect = $("#customer-select");
  const saveBtn = $("#save-btn");

  function lockSave(lock) {
    if (!saveBtn.length) return;
    saveBtn.prop("disabled", lock);
  }

  function setPdfButtons(invoiceId) {
    // HTML/WeasyPrint
    if (pdfBtnHtml) {
      if (!invoiceId) {
        pdfBtnHtml.classList.add("disabled");
        pdfBtnHtml.href = "#";
      } else {
        pdfBtnHtml.classList.remove("disabled");
        pdfBtnHtml.href = `/invoices/${invoiceId}/pdf/`;
      }
    }

    // ReportLab
    if (pdfBtnRl) {
      if (!invoiceId) {
        pdfBtnRl.classList.add("disabled");
        pdfBtnRl.href = "#";
      } else {
        pdfBtnRl.classList.remove("disabled");
        pdfBtnRl.href = `/invoices/${invoiceId}/pdf-rl/`;
      }
    }
  }

  function lockInvoiceFields(lock) {
    $("#id_invoice_order_date").prop("disabled", lock);
    $("#id_invoice_service_date").prop("disabled", lock);
  }

  function lockCustomerSelect(lock) {
    customerSelect.prop("disabled", lock);
    if (customerSelect.data("select2")) {
      customerSelect.trigger("change.select2");
    }
  }

  // Invoice select2
  $("#invoice-select").select2({
    placeholder: "Rechnung auswählen",
    allowClear: true,
    width: "100%",
  });

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

      $("#id_invoice_vat_percent").prop("disabled", false);

      $("#id_invoice_order_date").val("");
      $("#id_invoice_service_date").val("");

      $("#customer_number, #customer_name, #customer_address, #customer_vehicle, \
        #customer_license_plate, #customer_kilometers, #customer_created_at, \
        #customer_updated_at").text("—");

      $("#add-item").show();

      setPdfButtons(null);
      return;
    }

    // ===============================
    // EXISTING INVOICE SELECTED
    // ===============================
    setPdfButtons(invoiceId);
    lockCustomerSelect(true);
    lockSave(true);

    fetch(`/invoices/get_invoice_data/${invoiceId}/`)
      .then((res) => res.json())
      .then((data) => {
        lockInvoiceFields(true);

        $("#id_invoice_order_date").val(data.invoice_order_date);
        $("#id_invoice_service_date").val(data.invoice_service_date);

        $("#customer_number").text(data.customer_number);
        $("#customer_name").text(data.customer_name);
        $("#customer_address").text(data.customer_address);
        $("#customer_vehicle").text(data.customer_vehicle);
        $("#customer_license_plate").text(data.customer_license_plate);
        $("#customer_kilometers").text(data.customer_kilometers);
        $("#customer_created_at").text(data.customer_created_at);
        $("#customer_updated_at").text(data.customer_updated_at);

        if (typeof loadInvoiceItems === "function") {
          loadInvoiceItems(invoiceId);
        }

        $("#add-item").hide();
      })
      .catch((err) => console.error("Failed to load invoice data", err));
  });

  // initial state
  setPdfButtons(null);
});
