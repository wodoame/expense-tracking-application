"use strict";
class DropdownManager {
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
const dropdownManager = new DropdownManager();
