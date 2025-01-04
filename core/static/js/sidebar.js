"use strict";
const getSidebar = (() => {
    let instance = undefined;
    return () => {
        if (instance) {
            return instance;
        }
        instance = window['FlowbiteInstances']._instances.Drawer['separator-sidebar'];
        return instance;
    };
})();
