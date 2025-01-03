const getSidebar = (()=>{
    let instance = undefined; 
    return ():DrawerInstance =>{
        if(instance){
            return instance; 
        }
        
        instance = window['FlowbiteInstances']._instances.Drawer['separator-sidebar']; 
        return instance;
    };
 })(); 