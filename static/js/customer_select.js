// static/js/customer_select.js
document.addEventListener("DOMContentLoaded", function () {
  const select = document.getElementById("customer-select");
  const hidden = document.getElementById("customer-id-hidden");

  if (!select || !hidden) return;

  function fillCustomer(data) {
    document.getElementById("customer_number").textContent = data.customer_number || "—";
    document.getElementById("customer_name").textContent = data.customer_name || "—";
    document.getElementById("customer_address").textContent = data.customer_address || "—";
    document.getElementById("customer_vehicle").textContent = data.customer_vehicle || "—";
    document.getElementById("customer_license_plate").textContent = data.customer_license_plate || "—";
    document.getElementById("customer_kilometers").textContent = data.customer_kilometers || "—";
    document.getElementById("customer_created_at").textContent = data.customer_created_at || "—";
    document.getElementById("customer_updated_at").textContent = data.customer_updated_at || "—";
  }

  function loadCustomer(id) {
    hidden.value = id || "";
    if (!id) return;

    fetch(`/invoices/get_customer_data/${id}/`)
      .then((res) => res.json())
      .then((data) => fillCustomer(data))
      .catch(() => fillCustomer({}));
  }

  // ---------- plain HTML select change ----------
  select.addEventListener("change", function () {
    loadCustomer(this.value);
  });

  // ---------- Select2 support ----------
  if (typeof $ !== "undefined" && typeof $.fn.select2 !== "undefined") {
    const $sel = $("#customer-select").select2({
      width: "100%",
      allowClear: true,
      placeholder: "Customer auswählen",
    });

    // when user selects from Select2 UI
    $sel.on("select2:select", function (e) {
      loadCustomer(e.params.data.id);
    });

    // when cleared
    $sel.on("select2:clear", function () {
      hidden.value = "";
      fillCustomer({});
    });
  }
});
