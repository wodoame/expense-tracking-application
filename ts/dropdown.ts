class DropdownManager{
    instances: {[key:string]: DropdownInstance} = {};
    getInstance(id:string){
        return this.instances[id]; 
    }
    
      setInstance(id:string, instance:DropdownInstance){
        this.instances[id] = instance; 
      }
}

const dropdownManager = new DropdownManager();