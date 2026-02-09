// static/js/customer_select.js
document.addEventListener("DOMContentLoaded", function () {
  const select = document.getElementById("customer-select");
  const hidden = document.getElementById("customer-id-hidden");

  if (!select || !hidden) return;

  const fields = {
    customer_number: document.getElementById("customer_number"),
    customer_name: document.getElementById("customer_name"),
    customer_address: document.getElementById("customer_address"),
    customer_vehicle: document.getElementById("customer_vehicle"),
    customer_license_plate: document.getElementById("customer_license_plate"),
    customer_kilometers: document.getElementById("customer_kilometers"),
    customer_created_at: document.getElementById("customer_created_at"),
    customer_updated_at: document.getElementById("customer_updated_at"),
  };

  function fillCustomer(data = {}) {
    if (fields.customer_number) fields.customer_number.textContent = data.customer_number || "—";
    if (fields.customer_name) fields.customer_name.textContent = data.customer_name || "—";
    if (fields.customer_address) fields.customer_address.textContent = data.customer_address || "—";
    if (fields.customer_vehicle) fields.customer_vehicle.textContent = data.customer_vehicle || "—";
    if (fields.customer_license_plate) fields.customer_license_plate.textContent = data.customer_license_plate || "—";
    if (fields.customer_kilometers) fields.customer_kilometers.textContent = data.customer_kilometers || "—";
    if (fields.customer_created_at) fields.customer_created_at.textContent = data.customer_created_at || "—";
    if (fields.customer_updated_at) fields.customer_updated_at.textContent = data.customer_updated_at || "—";
  }

  async function loadCustomer(id) {
    hidden.value = id || "";
    if (!id) {
      fillCustomer({});
      return;
    }

    try {
      const res = await fetch(`/invoices/get_customer_data/${id}/`);
      const data = await res.json();
      fillCustomer(data);
    } catch (e) {
      console.error("Failed loading customer", e);
      fillCustomer({});
    }
  }

  // Plain HTML change
  select.addEventListener("change", function () {
    loadCustomer(this.value);
  });

  // Select2 integration (if enabled)
  if (typeof $ !== "undefined" && typeof $.fn.select2 !== "undefined") {
    const $sel = $("#customer-select");

    if (!$sel.data("select2")) {
      $sel.select2({
        width: "100%",
        allowClear: true,
        placeholder: "Customer auswählen",
      });
    }

    // Make sure Select2 triggers real change too
    $sel.on("change", function () {
      loadCustomer(this.value);
    });
  }
});
