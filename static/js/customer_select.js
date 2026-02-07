// static/js/customer_select.js
document.addEventListener("DOMContentLoaded", function () {
  const select = document.getElementById("customer-select");
  const hidden = document.getElementById("customer-id-hidden");

  if (!select || !hidden) return;

  // select2 optional
  if (typeof $ !== "undefined" && typeof $.fn.select2 !== "undefined") {
    $("#customer-select").select2({ width: "100%", allowClear: true });
  }

  select.addEventListener("change", function () {
    const id = this.value;
    hidden.value = id || "";

    if (!id) return;

    fetch(`/invoices/get_customer_data/${id}/`)
      .then((res) => res.json())
      .then((data) => {
        document.getElementById("customer_number").textContent = data.customer_number || "—";
        document.getElementById("customer_name").textContent = data.customer_name || "—";
        document.getElementById("customer_address").textContent = data.customer_address || "—";
        document.getElementById("customer_vehicle").textContent = data.customer_vehicle || "—";
        document.getElementById("customer_license_plate").textContent = data.customer_license_plate || "—";
        document.getElementById("customer_kilometers").textContent = data.customer_kilometers || "—";
        document.getElementById("customer_created_at").textContent = data.customer_created_at || "—";
        document.getElementById("customer_updated_at").textContent = data.customer_updated_at || "—";
      });
  });
});
