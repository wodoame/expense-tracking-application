import { categoryPublisher, fetchJSONData, getSidebar} from "./utils";
import { modalManager, handleCloseModal } from "./modals";
import { selectFieldManager } from "./selectField";
import Alpine from "alpinejs";
import { router } from "./router";
import { hh } from "./history";
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
      none: {id: null, name: 'None'}, 
      async init(){
        selectFieldManager.setInstance(id, this);
        categoryPublisher.subscribe(this); 
        const data = await fetchJSONData('/api/categories/');
        this.update(data);
        this.selected = this.none;
      }, 
      update(data: any){
        this.items = [this.none, ...data];
        this.filtered = [...this.items];
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
          const query = (<HTMLInputElement>e.currentTarget).value.toLowerCase();
          this.filtered = this.items.filter((obj)=> (<string>obj.name).toLowerCase().includes(query)); 
          if(this.filtered.length == 0){
             this.newSearch = (<HTMLInputElement>e.currentTarget).value; 
             this.newCategory={id:0, name:this.newSearch};
             this.select(this.newCategory);
          }
          else{
            this.open(); // open dropdown if there's a match
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

function initializeFlowbite(){
  getSidebar().hide(); // close the sidebar before flowbite reinitializes to prevent unexpected behaviours
  window.initFlowbite()
}

function restoreHistory(e:PopStateEvent){
  const currentPath = window.location.pathname;
  if(currentPath in router.routes)hh.handle(currentPath, e);
  initializeFlowbite();
};
document.addEventListener('htmx:afterSettle', initializeFlowbite);
document.addEventListener('alpine:init', handleAlpineInitialization);
window.addEventListener('popstate', handleCloseModal);
window.addEventListener('popstate', restoreHistory);

window.addEventListener('beforeunload', ()=>{
    document.removeEventListener('alpine:init', handleAlpineInitialization);  
    window.removeEventListener('popstate', handleCloseModal);
    window.removeEventListener('popstate', restoreHistory);
    document.addEventListener('htmx:afterSettle', initializeFlowbite);
})
