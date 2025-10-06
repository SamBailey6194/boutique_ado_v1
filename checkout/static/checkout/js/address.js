document.addEventListener('DOMContentLoaded', function() {
    const addressDropdown = document.getElementById('id-address-select'); 
    if (!addressDropdown) return;

    const fullNameField = document.getElementById('id_full_name');
    const emailField = document.getElementById('id_email');
    const phoneField = document.getElementById('id_phone_number');
    const countryField = document.getElementById('id_country');
    const postcodeField = document.getElementById('id_postcode');
    const townField = document.getElementById('id_town_or_city');
    const street1Field = document.getElementById('id_street_address1');
    const street2Field = document.getElementById('id_street_address2');
    const countyField = document.getElementById('id_county');

    addressDropdown.addEventListener('change', function() {
        const selectedOption = addressDropdown.selectedOptions[0];
        if (!selectedOption) return;

        // Populate fields safely
        if (fullNameField) fullNameField.value = selectedOption.dataset.fullName || '';
        if (phoneField) phoneField.value = selectedOption.dataset.phone || '';
        if (countryField) countryField.value = selectedOption.dataset.country || '';
        if (postcodeField) postcodeField.value = selectedOption.dataset.postcode || '';
        if (townField) townField.value = selectedOption.dataset.town || '';
        if (street1Field) street1Field.value = selectedOption.dataset.street1 || '';
        if (street2Field) street2Field.value = selectedOption.dataset.street2 || '';
        if (countyField) countyField.value = selectedOption.dataset.county || '';
        
        // Email stays constant
    });
});