// static/js/invoice_create_mode.js
document.addEventListener("DOMContentLoaded", function () {
  const newBtn = document.getElementById("new-invoice-btn");
  const cancelBtn = document.getElementById("cancel-new-invoice-btn");

  const select = document.getElementById("invoice-select");
  const input = document.getElementById("invoice-no-input");
  const err = document.getElementById("invoice-no-error");

  if (!newBtn || !cancelBtn || !select || !input || !err) return;

  function freezeInvoiceSelect(freeze) {
    // disable the underlying select
    select.disabled = freeze;

    // if select2 is active, also disable its UI
    if (typeof $ !== "undefined" && $("#invoice-select").data("select2")) {
      $("#invoice-select").prop("disabled", freeze);
    }
  }

  function setCreateMode(on) {
    if (on) {
      // freeze dropdown + clear selection
      freezeInvoiceSelect(true);
      if (typeof $ !== "undefined" && $("#invoice-select").data("select2")) {
        $("#invoice-select").val(null).trigger("change");
      } else {
        select.value = "";
      }

      // show input for new invoice number
      select.classList.add("d-none");
      input.classList.remove("d-none");
      input.value = "";
      input.focus();

      // show cancel button
      cancelBtn.classList.remove("d-none");

      // clear error
      err.classList.add("d-none");
      err.textContent = "";

      // unlock fields
      $("#id_invoice_order_date").prop("disabled", false).val("");
      $("#id_invoice_service_date").prop("disabled", false).val("");
      $("#id_invoice_vat_percent").prop("disabled", false);

      // clear customer UI
      // $("#customer-select").val(null).trigger("change");
      if (typeof $ !== "undefined" && $("#customer-select").data("select2")) {
      $("#customer-select").val(null).trigger("change.select2");
              } else {
                      document.getElementById("customer-select").value = "";
                      document.getElementById("customer-select").dispatchEvent(new Event("change"));
              }

      $("#customer-id-hidden").val("");
      $("#customer_number, #customer_name, #customer_address, #customer_vehicle, #customer_license_plate, #customer_kilometers, #customer_created_at, #customer_updated_at").text("—");

      // clear items
      if (typeof clearInvoiceItems === "function") clearInvoiceItems();
      if (typeof lockInvoiceItems === "function") lockInvoiceItems(false);

      $("#add-item").show();
      return;
    }

    // cancel create mode
    input.classList.add("d-none");
    select.classList.remove("d-none");
    cancelBtn.classList.add("d-none");

    freezeInvoiceSelect(false);

    // clear input/error
    input.value = "";
    err.classList.add("d-none");
    err.textContent = "";
  }

  newBtn.addEventListener("click", () => setCreateMode(true));
  cancelBtn.addEventListener("click", () => setCreateMode(false));

  // invoice number uniqueness check
  input.addEventListener("blur", function () {
    const value = input.value.trim();
    if (!value) return;

    fetch(`/invoices/check-invoice-no/?invoice_no=${encodeURIComponent(value)}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.exists) {
          err.textContent = "Invoice number already used!";
          err.classList.remove("d-none");
        } else {
          err.classList.add("d-none");
          err.textContent = "";
        }
      });
  });
});
