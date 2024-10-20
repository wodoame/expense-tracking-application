"use strict";
const products = JSON.parse(document.getElementById('products').textContent);
const getProduct = (id) => {
    for (const product of products) {
        if (product.id == +id) {
            //  console.log(product);
            return product;
        }
    }
};
// instead of the function below if it becomes necessay (eg. if the UI needs to be dynamic ) I will use string literals to generate html and insert them 
// into the DOM using .insertAdjacentHTML() 
const setDetail = (id, value) => {
    document.getElementById(id).textContent = value;
};
const showDetails = (e) => {
    e.stopPropagation();
    const productId = e.currentTarget.id;
    const product = getProduct(productId);
    setDetail('product-name', product.name);
    setDetail('product-price', `GHS ${product.price.toFixed(2)}`);
    setDetail('product-category', product.category ? product.category.name : 'None');
    setDetail('product-description', product.description || 'No description');
    // TODO: make a reusable component for the details section so that you can use it in the delete modal
    toggle(e, 'show-details-modal');
};
const editProduct = (e) => {
    e.stopPropagation();
    const productId = e.currentTarget.parentNode.parentNode.parentNode.id;
    const product = getProduct(productId);
    const modal = document.getElementById('edit-product-modal');
    const nameInput = modal.querySelector('[name=name]');
    const cedisInput = modal.querySelector('[name=cedis]');
    const pesewasInput = modal.querySelector('[name=pesewas]');
    const descriptionInput = modal.querySelector('[name=description]');
    const idInput = modal.querySelector('[name=id]');
    const categoryInput = modal.querySelector('[name=category]');
    const priceParts = product.price.toString().split('.');
    if (priceParts.length > 1) {
        pesewasInput.value = priceParts[1];
    }
    if (product.category) {
        categoryInput.value = product.category.id.toString();
    }
    idInput.value = product.id.toString();
    setCategory(product.category);
    cedisInput.value = priceParts[0];
    nameInput.value = product.name;
    descriptionInput.value = product.description;
    toggle(e, 'edit-product-modal');
};
const deleteProduct = (e) => {
    e.stopPropagation();
    const productId = e.currentTarget.parentNode.parentNode.parentNode.id;
    console.log(productId);
    const product = getProduct(productId);
    setDetail('delete-product-name', product.name);
    setDetail('delete-product-price', `GHS ${product.price.toFixed(2)}`);
    setDetail('delete-product-category', product.category ? product.category.name : 'None');
    setDetail('delete-product-description', product.description || 'No description');
    document.getElementById('delete-product-id').value = productId;
    toggle(e, 'delete-product-modal');
};
