type SelectFieldInstance = {
  select: (selected:object)=>void; 
  filter: (e: Event)=>void;
  isOpen: boolean;
  none: object;
};

class SelectFieldManager{
  instances: {[key: string]: SelectFieldInstance} = {}; 

  getInstance(id:string){
    return this.instances[id]; 
  }

  setInstance(id:string, instance:SelectFieldInstance){
    this.instances[id] = instance; 
  }
}

const selectFieldManager = new SelectFieldManager();
type DatePickerInstance = {
  setDate: (date:string)=>void;
  setToday: ()=>void;
}
class DatePickerManager{
  instances: {[key: string]: DatePickerInstance} = {}; 

  getInstance(id:string){
    return this.instances[id]; 
  }

  setInstance(id:string, instance:DatePickerInstance){
    this.instances[id] = instance; 
  }
}

const datePickerManager = new DatePickerManager();
export {
  datePickerManager, 
  selectFieldManager
};


