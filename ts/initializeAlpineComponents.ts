function createModalInstance(id: string){
    return {
        isOpen: false,
        init(){
            modalManager.createModal(id, this);
        },
        // functionalities defined here can be used in the components directly
        open(){
            this.isOpen = true;
            this.toggleSideEffects(!this.isOpen); 
            history.pushState(null, '');
            localStorage.setItem('modalOpen', 'true');
            modalManager.currentlyOpenModal = this;
        }, 
        close(){
            this.isOpen = false;
            this.toggleSideEffects(!this.isOpen);
            // no matter what closes the modal remove these from localStorage
            localStorage.removeItem('modalOpen');
            localStorage.removeItem('forwarded');
        },
        toggleSideEffects(force:boolean){
            const animatedBackdrop = document.getElementById('animated-backdrop');
            const body = document.body;
            animatedBackdrop.classList.toggle('hidden', force); // note when force is true the class is added and if it's false it is removed
            body.classList.toggle('overflow-hidden', !force);
        }, 
        handleClickOutside(e: Event){
            if(e.target == e.currentTarget){
                this.close();
            }
        }
    }
}


function createSelectFieldInstance(id: string){
    return {
      isOpen:false, 
      filtered: [], // represent filtered results
      items: [],
      isFocused: false, 
      selected: {},
      submitProperty: '', 
      newSearch:'', 
      newCategory: {},
      async init(){
        // original = items
        // objects = filtered
        // open = isOpen
        selectFieldManager.setInstance(id, this);
        this.items = [{id: null, name: 'None'}, ... await fetchJSONData('/api/categories/')];
        this.selected = this.items[0];
      },
      open(){
        this.isOpen=true;
        this.isFocused=true;
      }, 
      close(){
        this.isOpen=false;
        this.selected = {...this.selected};
        this.filtered = [...this.items];
        this.isFocused = false;
      }, 
      filter(e:Event){
          this.filtered = this.items.filter((obj)=> (<string>obj.name).toLowerCase().includes((<HTMLInputElement>e.currentTarget).value.toLowerCase())); 
          if(this.filtered.length == 0){
             this.newSearch = (<HTMLInputElement>e.currentTarget).value; 
          }
      }, 
      select(selected:object){
        this.selected = selected; 
        this.isOpen = false; 
        this.filtered = [...this.items]
      },
    }
  }
  

function handleAlpineInitialization(){
    Alpine.data('baseModal', createModalInstance);
    Alpine.data('selectField', createSelectFieldInstance);
}

document.addEventListener('alpine:init', handleAlpineInitialization);
window.addEventListener('popstate', handleCloseModal);

window.addEventListener('beforeunload', ()=>{
    document.removeEventListener('alpine:init', handleAlpineInitialization);  
    window.removeEventListener('popstate', handleCloseModal);
})
