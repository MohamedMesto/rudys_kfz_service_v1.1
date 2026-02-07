// ########################################################
// static/js/invoice_formset.js
//
// PURPOSE
// --------
// Handles dynamic Django formset rows for invoice items.
// - Adds new invoice item rows
// - Safely updates Django TOTAL_FORMS
// - Prevents adding empty / invalid rows
// - Initializes Select2 for diagnosis dropdowns
//
// This file ONLY handles formset row logic.
// (No invoice loading, no calculations)
// ########################################################

document.addEventListener("DOMContentLoaded", function () {

  // -----------------------------------------------------
  // Core DOM references
  // -----------------------------------------------------
  const addButton = document.getElementById("add-item"); // ➕ Add Item button
  const tableBody = document.getElementById("invoice-items-body"); // tbody for rows
  const totalFormsInput = document.querySelector('input[name$="TOTAL_FORMS"]'); // Django mgmt field
  const emptyTemplate = document.getElementById("empty-form-row"); // hidden empty form row

  // -----------------------------------------------------
  // Safety guard
  // If this page doesn't contain invoice formset elements,
  // stop execution to avoid JS errors on other pages.
  // -----------------------------------------------------
  if (!addButton || !tableBody || !totalFormsInput || !emptyTemplate) {
    return;
  }

  // -----------------------------------------------------
  // Validate last row before adding a new one
  // Prevents creating empty invoice items
  // -----------------------------------------------------
  function lastRowIsValid() {
    const rows = tableBody.querySelectorAll(".invoice-item-row");
    if (rows.length === 0) return true;

    const lastRow = rows[rows.length - 1];

    const diagnosis = lastRow.querySelector(
      'select[name$="invoice_item_diagnosis"]'
    );
    const quantity = lastRow.querySelector(
      'input[name$="invoice_item_quantity"]'
    );
    const price = lastRow.querySelector(
      'input[name$="invoice_item_unit_price"]'
    );

    // If inputs are missing (edge case), do not block user
    if (!diagnosis || !quantity || !price) return true;

    return (
      diagnosis.value !== "" &&
      parseFloat(quantity.value) > 0 &&
      parseFloat(price.value) > 0
    );
  }

  // -----------------------------------------------------
  // Initialize Select2 for diagnosis dropdowns
  // Can be applied to:
  // - document (page load)
  // - a newly added row
  // -----------------------------------------------------
  function initDiagnosisSelect(context = document) {
    if (typeof $ === "undefined" || typeof $.fn.select2 === "undefined") return;

    $(context).find(".diagnosis-select").select2({
      placeholder: "Diagnose auswählen",
      allowClear: true,
      width: "100%",
    });
  }

  // -----------------------------------------------------
  // Initialize Select2 for already existing rows on load
  // -----------------------------------------------------
  initDiagnosisSelect();

  // -----------------------------------------------------
  // Add new invoice item row
  // -----------------------------------------------------
  addButton.addEventListener("click", function () {

    // Block adding a new row if last row is incomplete
    if (!lastRowIsValid()) {
      alert("Bitte füllen Sie zuerst Diagnose, Menge und Preis aus.");
      return;
    }

    // Current Django formset index
    const formIndex = parseInt(totalFormsInput.value, 10);

    // Clone hidden empty form template
    const newRow = emptyTemplate.cloneNode(true);

    // Clean up cloned row
    newRow.removeAttribute("id");        // avoid duplicate IDs
    newRow.classList.remove("d-none");   // make row visible

    // Replace Django __prefix__ with actual index
    newRow.innerHTML = newRow.innerHTML.replace(
      /__prefix__/g,
      formIndex
    );

    // Append row to table
    tableBody.appendChild(newRow);

    // Update Django TOTAL_FORMS counter
    totalFormsInput.value = formIndex + 1;

    // Initialize Select2 ONLY for the new row
    initDiagnosisSelect(newRow);
  });
});
