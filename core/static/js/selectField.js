"use strict";
class SelectFieldManager {
    constructor() {
        this.instances = {};
    }
    getInstance(id) {
        return this.instances[id];
    }
    setInstance(id, instance) {
        this.instances[id] = instance;
    }
}
const selectFieldManager = new SelectFieldManager();
