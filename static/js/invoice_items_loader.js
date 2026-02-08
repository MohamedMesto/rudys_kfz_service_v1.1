// static/js/invoice_items_loader.js
// Loads invoice items and rebuilds formset (readonly)

function clearInvoiceItems() {
  const tbody = document.getElementById("invoice-items-body");
  if (tbody) tbody.innerHTML = "";

  const totalForms = document.querySelector('input[name$="TOTAL_FORMS"]');
  if (totalForms) totalForms.value = 0;
}

function lockInvoiceItems(lock = true) {
  document.querySelectorAll("#invoice-items-body select, #invoice-items-body input")
    .forEach((el) => (el.disabled = lock));
}

function loadInvoiceItems(invoiceId) {
  clearInvoiceItems();

  fetch(`/invoices/get_invoice_items/${invoiceId}/`)
    .then((res) => res.json())
    .then((data) => {
      if (!data || !Array.isArray(data.items)) {
        console.error("Invalid invoice items payload", data);
        return;
      }

      const tbody = document.getElementById("invoice-items-body");
      const totalFormsInput = document.querySelector('input[name$="TOTAL_FORMS"]');
      const emptyRowTpl = document.getElementById("empty-form-row");

      if (!tbody || !totalFormsInput || !emptyRowTpl) {
        console.error("Missing DOM elements for formset rebuild");
        return;
      }

      data.items.forEach((item, index) => {
        const row = emptyRowTpl.cloneNode(true);
        row.classList.remove("d-none");
        row.removeAttribute("id");

        row.innerHTML = row.innerHTML.replace(/__prefix__/g, index);
        tbody.appendChild(row);

        // Diagnosis select
        const select = row.querySelector("select.diagnosis-select");
        if (select) {
          select.value = item.diagnosis_id;

          // If select2 exists, update UI properly
          if (typeof $ !== "undefined" && $(select).data("select2")) {
            $(select).val(item.diagnosis_id).trigger("change");
          } else if (typeof $ !== "undefined" && typeof $.fn.select2 !== "undefined") {
            $(select).select2({ width: "100%" });
            $(select).val(item.diagnosis_id).trigger("change");
          }
        }

        // Quantity & unit price
        const qty = row.querySelector('input[name$="invoice_item_quantity"]');
        const price = row.querySelector('input[name$="invoice_item_unit_price"]');

        if (qty) qty.value = item.quantity;
        if (price) price.value = item.unit_price;

        // Line total display
        const totalCell = row.querySelector(".item-total");
        if (totalCell) totalCell.textContent = parseFloat(item.line_total).toFixed(2) + " €";
      });

      totalFormsInput.value = data.items.length;

      // Totals (readonly display)
      $("#subtotal").text(parseFloat(data.subtotal).toFixed(2) + " €");
      $("#id_invoice_vat_percent").val(data.vat_percent).prop("disabled", true);
      $("#vat-amount").text(parseFloat(data.vat_amount).toFixed(2) + " €");
      $("#grand-total").text(parseFloat(data.grand_total).toFixed(2) + " €");

      // Lock editing for existing invoices
      lockInvoiceItems(true);
    })
    .catch((err) => console.error("loadInvoiceItems fetch error", err));
}
