document.addEventListener('DOMContentLoaded', function() {
    const editButtons = document.querySelectorAll('.btn-edit-address');
    editButtons.forEach(btn => {
        btn.addEventListener('click', e => {
            const addressId = btn.dataset.id;
            const modal = document.getElementById('editAddressModal');
            const form = modal.querySelector('form');
            form.action = `/profile/address/${addressId}/edit/`; // points to UpdateView
            // Populate form fields with existing address data
            form.querySelector('#id_label').value = btn.dataset.label;
            form.querySelector('#id_street_address1').value = btn.dataset.street1;
            form.querySelector('#id_street_address2').value = btn.dataset.street2;
            form.querySelector('#id_town_or_city').value = btn.dataset.city;
            form.querySelector('#id_county').value = btn.dataset.county;
            form.querySelector('#id_postcode').value = btn.dataset.postcode;
            form.querySelector('#id_country').value = btn.dataset.country;
            form.querySelector('#id_phone_number').value = btn.dataset.phone;
        });
    });

    const deleteButtons = document.querySelectorAll('.btn-delete-address');
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', e => {
            const addressId = btn.dataset.id;
            const modal = document.getElementById('deleteAddressModal');
            const form = modal.querySelector('form');
            form.action = `/profile/address/${addressId}/delete/`;
        });
    });
});