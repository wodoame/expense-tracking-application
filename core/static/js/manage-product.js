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
const setDetail = (modal, query, value) => {
    modal.querySelector(query).textContent = value;
};
const showDetails = (e) => {
    e.stopPropagation();
    const productId = e.currentTarget.id;
    const product = getProduct(productId);
    const id = 'show-details-modal';
    const modal = document.getElementById(id);
    setDetail(modal, `#${id}-product-name`, product.name);
    setDetail(modal, `#${id}-product-price`, `GHS ${product.price.toFixed(2)}`);
    setDetail(modal, `#${id}-product-category`, product.category ? product.category.name : 'None');
    setDetail(modal, `#${id}-product-description`, product.description || 'No description');
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
    const product = getProduct(productId);
    const id = 'delete-product-modal';
    const modal = document.getElementById(id);
    setDetail(modal, `#${id}-product-name`, product.name);
    setDetail(modal, `#${id}-product-price`, `GHS ${product.price.toFixed(2)}`);
    setDetail(modal, `#${id}-product-category`, product.category ? product.category.name : 'None');
    setDetail(modal, `#${id}-product-description`, product.description || 'No description');
    modal.querySelector('#delete-product-id').value = productId;
    toggle(e, 'delete-product-modal');
};
