type SelectFieldInstance = {
  select: (selected:object)=>void; 
  filter: (e: Event)=>void;
  isOpen: boolean;
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
