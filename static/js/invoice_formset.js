// ########################################################
// invoice_formset.js
// Handles:
// - Dynamic Django formset rows
// - Select2 initialization
// - Validation before adding new rows
// - Auto price fill from diagnosis
// ########################################################

document.addEventListener('DOMContentLoaded', function () {

    // -----------------------------------------------------
    // Core DOM references
    // -----------------------------------------------------
    const addButton = document.getElementById('add-item');
    const tableBody = document.getElementById('invoice-items-body');
    const totalFormsInput = document.querySelector('input[name$="TOTAL_FORMS"]');
    const row = document.getElementById('empty-form-row').cloneNode(true);
    row.classList.remove('d-none');
    row.removeAttribute('id');

    row.innerHTML = row.innerHTML.replace(/__prefix__/g, index);
    tbody.appendChild(row);


    // -----------------------------------------------------
    // Initialize Select2 for diagnosis dropdowns
    // context = document (page load) OR newRow (dynamic)
    // -----------------------------------------------------
    function initDiagnosisSelect(context = document) {
        $(context).find('.diagnosis-select').select2({
            placeholder: "Diagnose auswählen",
            allowClear: true,
            width: '100%'
        });
    }

    // -----------------------------------------------------
    // Validate last row before allowing a new row
    // Prevents empty invoice items
    // -----------------------------------------------------
    function lastRowIsValid() {
        const rows = tableBody.querySelectorAll('.invoice-item-row');
        if (rows.length === 0) return true;

        const lastRow = rows[rows.length - 1];

        const diagnosis = lastRow.querySelector('select[name$="invoice_item_diagnosis"]');
        const quantity = lastRow.querySelector('input[name$="invoice_item_quantity"]');
        const price = lastRow.querySelector('input[name$="invoice_item_unit_price"]');

        // If inputs are missing, do not block user
        if (!diagnosis || !quantity || !price) return true;

        return (
            diagnosis.value !== '' &&
            parseFloat(quantity.value) > 0 &&
            parseFloat(price.value) > 0
        );
    }

    // -----------------------------------------------------
    // Initialize Select2 on page load (existing rows)
    // -----------------------------------------------------
    initDiagnosisSelect();

    // -----------------------------------------------------
    // Add new invoice item row
    // -----------------------------------------------------
    addButton.addEventListener('click', function () {

        // Block adding new row if last row incomplete
        if (!lastRowIsValid()) {
            alert('Bitte füllen Sie zuerst Diagnose, Menge und Preis aus.');
            return;
        }

        // Current Django formset index
        let formIndex = parseInt(totalFormsInput.value, 10);

        // Clone hidden empty form template
        const newRow = emptyRow.cloneNode(true);
        newRow.removeAttribute('id');       // avoid duplicate IDs
        newRow.classList.remove('d-none');  // make row visible

        // Replace Django __prefix__ with real index
        newRow.innerHTML = newRow.innerHTML.replace(/__prefix__/g, formIndex);

        // Append to table
        tableBody.appendChild(newRow);

        // Update Django TOTAL_FORMS
        totalFormsInput.value = formIndex + 1;

        // Initialize Select2 ONLY for the new row
        initDiagnosisSelect(newRow);
    });
});


// ########################################################
// AUTO FILL PRICE FROM DIAGNOSIS (Admin-like behavior)
// When diagnosis changes → fetch default price
// ########################################################
document.addEventListener('change', function (e) {

    // Only react to diagnosis dropdown changes
    if (!e.target.classList.contains('diagnosis-select')) return;

    const select = e.target;
    const row = select.closest('.invoice-item-row');

    // ⚠️ FIX #1: correct input name suffix
    const priceInput = row.querySelector('input[name$="invoice_item_unit_price"]');

    if (!select.value || !priceInput) return;

    fetch(`/diagnosis/get/${select.value}/`)
        .then(res => res.json())
        .then(data => {
            priceInput.value = data.default_price;

            // ⚠️ FIX #2: guard against missing functions
            if (typeof recalcRow === 'function') {
                recalcRow(row);
            }

            if (typeof recalcInvoiceTotals === 'function') {
                recalcInvoiceTotals();
            }
        });
});
