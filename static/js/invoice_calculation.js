// rudys_kfz_service_v1.1/static/js/invoice_calculation.js
// ########################################################
// Handles:
// - Line total calculation per invoice row
// - Invoice subtotal
// - VAT calculation
// - Grand total
// Works for:
// - Existing rows
// - Dynamically added rows
// ########################################################


// --------------------------------------------------------
// Recalculate ALL invoice totals (admin-like behavior)
// --------------------------------------------------------
function recalcInvoiceTotals() {
    let subtotal = 0;

    // Loop through each invoice item row
    document.querySelectorAll('.invoice-item-row').forEach(row => {

        // Quantity input (Django formset field name)
        const qtyInput = row.querySelector(
            'input[name$="invoice_item_quantity"]'
        );

        // Unit price input (Django formset field name)
        const priceInput = row.querySelector(
            'input[name$="invoice_item_unit_price"]'
        );

        // Line total cell
        const totalCell = row.querySelector('.item-total');

        // If inputs are missing, skip this row
        if (!qtyInput || !priceInput || !totalCell) return;

        // Parse numeric values safely
        const qty = parseFloat(qtyInput.value) || 0;
        const price = parseFloat(priceInput.value) || 0;

        // Calculate line total
        const lineTotal = qty * price;

        // Add to subtotal
        subtotal += lineTotal;

        // Update UI (line total)
        totalCell.innerText = lineTotal.toFixed(2) + ' €';
    });

    // ----------------------------------------------------
    // Update subtotal
    // ----------------------------------------------------
    const subtotalEl = document.getElementById('subtotal');
    if (subtotalEl) {
        subtotalEl.innerText = subtotal.toFixed(2) + ' €';
    }

    // ----------------------------------------------------
    // VAT calculation
    // ----------------------------------------------------
    const vatPercentInput = document.getElementById('id_invoice_vat_percent');
    const vatPercent = parseFloat(vatPercentInput?.value) || 0;

    const vatAmount = subtotal * vatPercent / 100;
    const grandTotal = subtotal + vatAmount;

    // ----------------------------------------------------
    // Update grand total
    // ----------------------------------------------------
    const grandTotalEl = document.getElementById('grand-total');
    if (grandTotalEl) {
        grandTotalEl.innerText = grandTotal.toFixed(2) + ' €';
    }
}


// --------------------------------------------------------
// Listen for ANY relevant input change
// - Quantity
// - Unit price
// - VAT percent
// --------------------------------------------------------
document.addEventListener('input', function (e) {
    if (
        e.target.name?.includes('invoice_item_quantity') ||
        e.target.name?.includes('invoice_item_unit_price') ||
        e.target.id === 'id_invoice_vat_percent'
    ) {
        recalcInvoiceTotals();
    }
});


// --------------------------------------------------------
// Initial calculation on page load
// (important when editing existing invoices)
// --------------------------------------------------------
document.addEventListener('DOMContentLoaded', recalcInvoiceTotals);
