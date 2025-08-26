import { router } from "./router";
import { categoryPublisher } from "./utils";
import { datePickerManager, selectFieldManager } from "./selectField";
import { emitter, showSkeleton, toggleLoader } from "../core/templates/core/components/categories";
import { getCategories } from "../core/templates/core/components/categories";
import { ToastManager } from "../core/templates/core/components/toast";
class ModalManager{
    modals:any; 
    currentlyOpenModal: ModalInstance | null;  // track the currently opened modal
    constructor(){
        this.modals = {}; // a store of created modals
        this.currentlyOpenModal = null;
    }

    createModal(id: string, modalInstance: ModalInstance){
        this.modals[id] = modalInstance; 
    }

    getModal(id: string){
        return this.modals[id];
    }


}

const modalManager = new ModalManager();

// link a modal with this class to control basic modal functionality
// The modal classes here are basically proxy classes for controlling the actual modal instance created using Alpine.js
class BaseModal{
   modal: ModalInstance;
   constructor(id: string){
        this.modal = modalManager.getModal(id);
   }
   open(){
      this.modal.open();
   }
   
   close(){
      this.modal.close();
   }
}

class AddProductModal extends BaseModal{
   
   private _showPageSkeleton(path: string) {
        const pattern = /^\/categories\/[^\/]+\/$/;
        if(pattern.test(path))return document.getElementById('see-products')!.outerHTML = router.routes['seeProductsSkeleton']; // insert the placeholder without triggering htmx
        if(!(path in router.routes) || path == '/search/')return this._navigateToDashboard();
        return document.getElementById('main-content')!.innerHTML = router.routes[path];
    }

    private _getHTMXTarget(path: string): string{
        const pattern = /^\/categories\/[^\/]+\/$/;
        if(pattern.test(path)) return '#see-products';
        if(path == '/all-expenditures/')return '#all-expenditures';
        if(path == '/categories/')return '#toast-wrapper';
        return '#main-content';
    }

     private _navigateToDashboard() {
        document.getElementById('main-content')!.innerHTML = router.routes['/dashboard/'];
        history.pushState(null, '', '/dashboard/');
        router.currentRoute = '/dashboard/';
    }

    private _resetFormUI(form: HTMLFormElement) {
        form.reset();
        selectFieldManager.getInstance('categories-add-product').select(selectFieldManager.getInstance('categories-add-product').none);
        datePickerManager.getInstance('add-product-date-picker').setToday();
    }

    private _submitProductForm(form: HTMLFormElement, target: string) {
        const formData = htmx.values(form);
        htmx.ajax('POST', '/implementations/dashboard/', {
            values: formData,
            target: target,
        }).then(() => {
            categoryPublisher.fetchLatest();
            emitter.emit('expense_added_or_edited_or_deleted'); // notify that an expense has been added or edited or deleted
            toggleLoader();
        });
    }

   submitForm(){
       const form = <HTMLFormElement>document.getElementById('add-product-form');
       if(form.checkValidity()){
        toggleLoader();
        const currentPagePath = window.location.pathname;
        const target = this._getHTMXTarget(currentPagePath);
        this._showPageSkeleton(currentPagePath); 
        this.close();
        this._submitProductForm(form, target) 
        this._resetFormUI(form);
       }
       else{
           form.reportValidity();
       }
   }
}

class AddCategoryModal extends BaseModal{
    categoryExists(formData: any){
        const categoryName = formData.name;
        const currentCategories = selectFieldManager.getInstance('categories-add-product').items; // grab the categories from any of the available select fields
        return currentCategories.some(item => item.name === categoryName);
    }
    submitForm(){
        const form = <HTMLFormElement>document.getElementById('add-category-form');
        if(form.checkValidity()){
            this.close();
            const formData = htmx.values(form);
            if(!this.categoryExists(formData)){
                toggleLoader();
                showSkeleton();
                htmx.ajax('POST', '/implementations/categories/', {
                    values: formData,
                    target: '#toast-wrapper',
                }).then(()=>{
                    categoryPublisher.fetchLatest();
                    emitter.emit('expense_added_or_edited_or_deleted');
                    getCategories(); // fetch the latest categories
                    toggleLoader(); // hide the loader
                });
            }
            else{
                ToastManager.error("Category already exists");
            }
            form.reset();
        }
        else{
            form.reportValidity();
        }
    }
}

class EditCategoryModal extends BaseModal{
    ff: FormFields;
    constructor(id: string, ff: FormFields){
        super(id);
        this.ff = ff;
    }
    setDetails(data: string){
        const category: Category = JSON.parse(data);
        const formFields = this.ff.formFields;
        formFields.name.value = category.name; 
        formFields.description.value = category.description?category.description:''; 
        formFields.id.value = category.id.toString(); 
        this.open();   
    }
    submitForm(){
        const form = <HTMLFormElement>document.getElementById('edit-category-form');
        if(form.checkValidity()){
         toggleLoader();
         showSkeleton();
         this.close();
         const formData = htmx.values(form);
         htmx.ajax('POST', '/implementations/categories/?edit=1', {
          values: formData,
          target: '#toast-wrapper',
         }).then(()=>{
            categoryPublisher.fetchLatest();
            emitter.emit('expense_added_or_edited_or_deleted');
            getCategories(); // fetch the latest categories
            toggleLoader(); // hide the loader
         });
         form.reset();
        }
        else{
            form.reportValidity();
        }
    }
}


class DeleteCategoryModal extends BaseModal{
    df: DataFields;
    ff: FormFields;
    constructor(id: string, df: DataFields, ff: FormFields){
        super(id);
        this.df = df;
        this.ff = ff;
    }
    setDetails(data: string){
        const category: Category = JSON.parse(data);
        const dataFields = this.df.dataFields; 
        const formFields = this.ff.formFields;
        // set data field text contents
        dataFields.name.textContent = category.name;
        // set form field values
        formFields.id.value = category.id.toString(); 
        this.open();   
    }
    submitForm(){
        const form = <HTMLFormElement>document.getElementById('delete-category-form');
        const formData = htmx.values(form);
        toggleLoader(); 
        showSkeleton();
        this.close();
        htmx.ajax('POST', '/implementations/categories/?delete=1', {
         values: formData,
         target: '#toast-wrapper',
        }).then(()=>{
            categoryPublisher.fetchLatest();
            emitter.emit('expense_added_or_edited_or_deleted');
            getCategories(); // fetch the latest categories
            toggleLoader(); // hide the loader
        });
    }
}
class DataFields{
     // data fields 
     dataFields: {[key: string]: HTMLElement} = {};
     setDataField(key:string, value:HTMLElement){
         this.dataFields[key] = value;
     }
 };

class FormFields{
    // form fields 
    formFields: {[key: string]: HTMLInputElement} = {};

    setFormField(key: string, value:HTMLInputElement){
         this.formFields[key] = value; 
    }
}

class ShowDetailsModal extends BaseModal{
    df: DataFields;
    constructor(id: string, df: DataFields){
        super(id);
        this.df = df; 
    }

    setDetails(data: string){
        const product: Product = JSON.parse(data);
        const dataFields = this.df.dataFields;
        // set data field text contents
        dataFields.name.textContent = product.name;
        dataFields.price.textContent = `GHS ${product.price.toFixed(2)}`;
        dataFields.category.textContent = product.category? product.category.name: 'None';
        dataFields.description.textContent = product.description || 'No description'; 
        this.open();
    }
}

class DeleteProductModal extends BaseModal{
    df: DataFields;
    ff: FormFields;
    constructor(id: string, df: DataFields, ff: FormFields){
        super(id);
        this.df = df;
        this.ff = ff;
    }
    setDetails(data: string){
        const product: Product = JSON.parse(data);
        const dataFields = this.df.dataFields; 
        const formFields = this.ff.formFields;
        // set data field text contents
        dataFields.name.textContent = product.name;
        dataFields.price.textContent = `GHS ${product.price.toFixed(2)}`;
        dataFields.category.textContent = product.category? product.category.name: 'None';
        dataFields.description.textContent = product.description || 'No description'; 
        // set form field values
        formFields.id.value = product.id.toString(); 
        formFields.date.value = product.date;
        this.open();   
    }
    submitForm(){
        const form = <HTMLFormElement>document.getElementById('delete-product-form');
        toggleLoader();
        const formData = htmx.values(form);
        const tr = htmx.find(`#product-${formData.id}`);
        const elementToReplace = <HTMLElement>htmx.closest(tr, '.record');
        elementToReplace.querySelector('.skeleton').classList.remove('hidden');
        this.close();
        htmx.ajax('POST', '/implementations/dashboard/?delete=1', {
         values: formData,
         target: elementToReplace,
         swap: 'outerHTML'
        }).then(()=>{
            emitter.emit('expense_added_or_edited_or_deleted');
            toggleLoader();
        });
    }
}


class EditProductModal extends BaseModal{
 ff:FormFields;
 constructor(id:string, ff: FormFields){
    super(id)
    this.ff = ff; 
 }
  setDetails(data: string){
    const product: Product = JSON.parse(data);
    const formFields = this.ff.formFields;
    const priceParts = product.price.toString().split('.');
    formFields.name.value = product.name;
    formFields.cedis.value = priceParts[0];
    console.log(priceParts);
    if(product.category){
        formFields.category.value = product.category.id.toString();
    }
    if(priceParts.length == 2){
        formFields.pesewas.value = priceParts[1].length == 2? priceParts[1]: priceParts[1] + '0';
    }
    else{
        formFields.pesewas.value = '00';
    }

    formFields.id.value = product.id.toString();
    formFields.description.value = product.description;
    formFields.date.value = product.date;
    this.setCategory(product.category)
    datePickerManager.getInstance('edit-product-date-picker').setDate(product.date); 
    this.open();
  }

  setCategory(category: object){
    const field = selectFieldManager.getInstance('categories-edit-product');
    if(category){
        field.select(category);
    }
    else{
        field.select({id:null, name:'None'});
    }
  }
  submitForm(){
    const form = <HTMLFormElement>document.getElementById('edit-product-form');
    if(form.checkValidity()){
      toggleLoader();
      const formData = htmx.values(form);
      const tr = htmx.find(`#product-${formData.id}`);
      const elementToReplace = <HTMLElement>htmx.closest(tr, '.record');
      elementToReplace.querySelector('.skeleton').classList.remove('hidden');
      this.close();
      htmx.ajax('POST', '/implementations/dashboard/?edit=1', {
       values: formData,
       target: elementToReplace,
       swap: 'outerHTML'
      }).then(()=>{
        categoryPublisher.fetchLatest();
        emitter.emit('expense_added_or_edited_or_deleted');
        toggleLoader();
      });
    }
    else{
     form.reportValidity(); // display the validation messages
    }
  }
}

class CategoryDetailsModal extends BaseModal{
    df: DataFields;
    constructor(id: string, df: DataFields){
        super(id);
        this.df = df;
    }
    
    setDetails(data: string){
        const category: Category = JSON.parse(data);
        const dataFields = this.df.dataFields;
        // set data field text contents
        dataFields.name.textContent = category.name;
        dataFields.product_count.textContent = category.metrics.product_count.toString();
        dataFields.description.textContent = category.description || 'No description';
        this.open();
    }
}

class SearchModal extends BaseModal{
    ff: FormFields;
    constructor(id:string, ff: FormFields){
        super(id);
        this.ff = ff;
    }

    async submitForm(){
        const form = <HTMLFormElement>document.getElementById('search-form');
        if(form.checkValidity()){
            this.close(); 
            router.navigate('/search/')
            const formData = htmx.values(form)
            const target = '#main-content';
            htmx.ajax('GET', '/components/search/', {
             values: formData,
             target: target,
            });
            form.reset();
        }
        else{
            form.reportValidity();
        }
    }
}

// search modal 
const getSearchModal = (()=>{
    let instance = undefined; 
    return ()=>{
        if(instance){
            return instance; 
        }
        const ff = new FormFields();
        instance = new SearchModal('search-modal', ff);
        return instance;
    };
})();

// product modals 
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

const getDeleteProductModal = (()=>{
   let instance = undefined; 
   return ()=>{
       if(instance){
           return instance; 
       }
       const df = new DataFields();
       const ff = new FormFields(); 
       instance = new DeleteProductModal('delete-product-modal', df, ff);
       return instance;
   };
})(); 

const getShowDetailsModal = (()=>{
   let instance = undefined; 
   return ()=>{
       if(instance){
           return instance; 
       }
       const df = new DataFields();
       instance = new ShowDetailsModal('show-details-modal', df);
       return instance;
   };
})();

const getEditProductModal = (()=>{
   let instance = undefined; 
   return ()=>{
       if(instance){
           return instance; 
       }
       const ff = new FormFields();
       instance = new EditProductModal('edit-product-modal', ff);
       return instance;
   };
})();

// category modals
const getCategoryDetailsModal = (()=>{
   let instance = undefined; 
   return ()=>{
       if(instance){
           return instance; 
       }
       const df = new DataFields(); 
       instance = new CategoryDetailsModal('category-details-modal', df);
       return instance;
   };
})();
 
const getDeleteCategoryModal = (()=>{
   let instance = undefined; 
   return ()=>{
       if(instance){
           return instance; 
       }
       const df = new DataFields();
       const ff = new FormFields(); 
       instance = new DeleteCategoryModal('delete-category-modal', df, ff);
       return instance;
   };
})();

const getEditCategoryModal = (()=>{
   let instance = undefined; 
   return ()=>{
       if(instance){
           return instance; 
       }
       const ff = new FormFields(); 
       instance = new EditCategoryModal('edit-category-modal', ff);
       return instance;
   };
})(); 



// Other stuff
function handleCloseModal(){
    if(localStorage.getItem('modalOpen')){
        localStorage.removeItem('modalOpen');
        localStorage.setItem('forwarded','true')
        history.forward();
    }
    else if(localStorage.getItem('forwarded')){
        modalManager.currentlyOpenModal.close();
    }
}

// make some things available globally
// product modals
window['getAddProductModal'] = getAddProductModal;
window['getDeleteProductModal'] = getDeleteProductModal;
window['getShowDetailsModal'] = getShowDetailsModal;
window['getEditProductModal'] = getEditProductModal;

// category modals
window['getCategoryDetailsModal'] = getCategoryDetailsModal;
window['getAddCategoryModal'] = getAddCategoryModal;
window['getDeleteCategoryModal'] = getDeleteCategoryModal;
window['getEditCategoryModal'] = getEditCategoryModal;

// other modals
window['getSearchModal'] = getSearchModal;

// others
window['handleCloseModal'] = handleCloseModal;
window['modalManager'] = modalManager;

export {
    modalManager, 
    handleCloseModal,
    getEditCategoryModal,
    getDeleteCategoryModal
}; 
