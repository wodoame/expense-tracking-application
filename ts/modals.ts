// link a modal with this class to control basic modal functionality
class BaseModal{
   modal: ModalInstance;
   constructor(id: string){
        this.modal = modalManager.getModal(id);
   }
   toggle(){
      this.modal.toggle();
   }
}

class AddProductModal extends BaseModal{
   submitForm(){
       const form = <HTMLFormElement>document.getElementById('add-product-form');
       if(form.checkValidity()){
           form.submit();
       }
       else{
           form.reportValidity();
       }
   }
}

class AddCategoryModal extends BaseModal{
}


const getAddProductModal = (()=>{
   let instance = undefined; // just a reference to the modal if it has been called already 
   return ()=>{
       if(instance){
           return instance; 
       }
       
       instance = new AddProductModal('add-product-modal');
       return instance;
   };
})();

const getAddCategoryModal = (()=>{
   let instance = undefined; // just a reference to the modal if it has been called already 
   return ()=>{
       if(instance){
           return instance; 
       }
       
       instance = new AddCategoryModal('add-category-modal');
       return instance;
   };
})(); 