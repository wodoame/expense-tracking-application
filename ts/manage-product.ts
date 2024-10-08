const products: Product[] = JSON.parse(document.getElementById('products').textContent); 

const getProduct = (id: string)=>{
    for(const product of products){
        if(product.id == +id){
         console.log(product);
            return product;
        }
    }
};
    
// instead of the function below if it becomes necessay (eg. if the UI needs to be dynamic ) I will use string literals to generate html and insert them 
// into the DOM using .insertAdjacentHTML() 
const setDetail = (id: string, value: string)=>{
    document.getElementById(id).textContent = value;
};

const showDetails = (e: Event)=>{
    e.stopPropagation();
    const productId = (<HTMLElement>e.currentTarget).id;
    const product = getProduct(productId);
    setDetail('product-name', product.name); 
    setDetail('product-price', `GHS ${product.price.toFixed(2)}`); 
    setDetail('product-description', product.description || 'No description');
    // document.getElementById('product-name')
    toggle(e, 'show-details-modal');
}

const editProduct = (e: Event)=>{
   e.stopPropagation();
}; 

const deleteProduct = (e: Event)=>{
    e.stopPropagation();
    const productId = (<HTMLElement>(<HTMLElement>e.currentTarget).parentNode.parentNode.parentNode).id;
    console.log(productId);
    const product = getProduct(productId);
    setDetail('delete-product-name', product.name);
    setDetail('delete-product-price', `GHS ${product.price.toFixed(2)}`); 
    setDetail('delete-product-description', product.description || 'No description');
    (<HTMLInputElement>document.getElementById('delete-product-id')).value = productId;
    toggle(e, 'delete-product-modal') 
}; 