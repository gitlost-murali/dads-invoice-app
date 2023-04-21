// Add event listener for the "Add Item" button
document.getElementById('add-item').addEventListener('click', () => {
  const itemsTable = document.getElementById('items');
  const itemRow = document.createElement('tr');

  itemRow.innerHTML = `
    <td><input type="text" class="color-name"></td>
    <td><input type="text" class="lot-id"></td>
    <td><input type="number" class="no-of-pcs"></td>
    <td><input type="number" class="total-sft"></td>
    <td><input type="number" class="rate"></td>
    <td><input type="number" class="amount" readonly></td>
  `;

  itemsTable.appendChild(itemRow);

  const rateInput = itemRow.querySelector('.rate');
  const totalSftInput = itemRow.querySelector('.total-sft');
  const amountInput = itemRow.querySelector('.amount');

  rateInput.addEventListener('input', updateAmount);
  totalSftInput.addEventListener('input', updateAmount);

  function updateAmount() {
    const rate = parseFloat(rateInput.value) || 0;
    const totalSft = parseFloat(totalSftInput.value) || 0;
    amountInput.value = rate * totalSft;
  }
});

// Add this function to handle form data before sending it to the backend
function getFormData() {
    const formData = new FormData();
  
    formData.append('invoice_address', document.getElementById('invoice-address').value);
    formData.append('delivery_address', document.getElementById('delivery-address').value);
    formData.append('gst_number', document.getElementById('gst-number').value);
    formData.append('date', document.getElementById('date').value);
    formData.append('vehicle_number', document.getElementById('vehicle-number').value);
  
    const itemsTableRows = document.querySelectorAll('#items tr');
    const items = [];
    
    itemsTableRows.forEach(row => {
      const colorName = row.querySelector('.color-name').value;
      const lotId = row.querySelector('.lot-id').value;
      const noOfPcs = row.querySelector('.no-of-pcs').value;
      const totalSft = row.querySelector('.total-sft').value;
      const rate = row.querySelector('.rate').value;
      const amount = row.querySelector('.amount').value;
  
      items.push({ colorName, lotId, noOfPcs, totalSft, rate, amount });
    });
  
    formData.append('items', JSON.stringify(items));
    formData.append('transport_charges', document.getElementById('transport-charges').value);
    formData.append('loading_unloading_charges', document.getElementById('loading-unloading-charges').value);
  
    return formData;
  }

// Add the remaining event listeners as mentioned in the previous responses

document.getElementById('invoice-form').addEventListener('submit', async (event) => {
    event.preventDefault();
  
    // Perform calculations
    const amounts = document.querySelectorAll('.amount');
    const transportCharges = parseFloat(document.getElementById('transport-charges').value) || 0;
    const loadingUnloadingCharges = parseFloat(document.getElementById('loading-unloading-charges').value) || 0;
  
    let total = 0;
  
    amounts.forEach(amount => {
      total += parseFloat(amount.value) || 0;
    });
  
    const subTotal = total + transportCharges + loadingUnloadingCharges;
    const gst = subTotal * 0.18;
    const grandTotal = subTotal + gst;
  
    // Send data to the backend and generate the PDF
    const formData = getFormData();
    formData.append('sub_total', subTotal);
    formData.append('gst', gst);
    formData.append('grand_total', grandTotal);
  
    const response = await fetch('/generate-pdf', {
      method: 'POST',
      body: formData
    });
  
    if (response.ok) {
      const pdfBlob = await response.blob();
      const pdfUrl = URL.createObjectURL(pdfBlob);
      const link = document.createElement('a');
      link.href = pdfUrl;
      link.download = 'invoice.pdf';
      link.click();
      URL.revokeObjectURL(pdfUrl);
    } else {
      alert('Error generating PDF');
    }
  });