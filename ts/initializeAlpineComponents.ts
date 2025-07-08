import { categoryPublisher, fetchJSONData, globalEventEmitter, getSidebar} from "./utils";
import { modalManager, handleCloseModal } from "./modals";
import { datePickerManager, selectFieldManager } from "./selectField";
import Alpine from "alpinejs";

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

function createDatePicker(id:string){
  return{
    calendar:undefined,
    field:undefined, 
    options:{
       inputMode:true, 
       positionToInput: 'center',
       styles: {
        // Some styles are left blank to remove default styles
        calendar: 'calendar',
        dateBtn: 'vc-date__btn date-btn', 
        date: 'vc-date',
        month: '',
        year: '',
        yearsYear: 'vc-years__year',
        monthsMonth: 'vc-months__month',
        }, 
        onClickDate(self:any, event:Event){
          const selectedDate = self.context.selectedDates[0];
            if (selectedDate) {
              (<HTMLInputElement>document.getElementById(id + '-value')).value = selectedDate; 
              // Update the input field with the selected date
              const formattedDate = new Date(selectedDate); 
              (<HTMLInputElement>document.getElementById(id)).value = formattedDate.toDateString();
          }
        }
    }, 
    init(){
      datePickerManager.setInstance(id, this); 
      const { Calendar } = window['VanillaCalendarPro'];
      this.field = document.getElementById(id);
      this.calendar = new Calendar(this.field, this.options);
      this.calendar.init();
      this.setToday();
    }, 
    setDate(date:string){
      const selectedDate = new Date(date);
      this.field.value = selectedDate.toDateString();
      const isoDateString = selectedDate.toISOString().split('T')[0]; 
      (<HTMLInputElement>document.getElementById(id + '-value')).value = isoDateString;
      this.calendar.update();
    },
    setToday(){
       // Get today's date
       const today = new Date();
       // Convert to dateString format
       const dateString = today.toDateString();
       this.field.value = dateString;
       (<HTMLInputElement>document.getElementById(id + '-value')).value = today.toISOString().split('T')[0];
    }
  }
}

function handleAlpineInitialization(){
    Alpine.data('baseModal', createModalInstance);
    Alpine.data('selectField', createSelectFieldInstance);
    Alpine.data('datePicker', createDatePicker);
}

function initializeFlowbite(){
  getSidebar().hide(); // close the sidebar before flowbite reinitializes to prevent unexpected behaviours
  window.initFlowbite()
}

function restoreHistory(e:PopStateEvent){
  if(e.state){
    document.getElementById('main-content').innerHTML = e.state.html;
    if(window.location.pathname == '/dashboard/'){
      globalEventEmitter.emit('popstate');
    }
  }
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
