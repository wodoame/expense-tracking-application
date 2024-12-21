"use strict";
class ModalManager {
    constructor() {
        this.modals = {}; // a store of created modals
    }
    createModal(id, modalInstance) {
        this.modals[id] = modalInstance;
    }
    getModal(id) {
        return this.modals[id];
    }
}
const modalManager = new ModalManager();
document.addEventListener('alpine:init', () => {
    // this is where the actual creation of a modal takes place
    Alpine.data('baseModal', (id) => ({
        isOpen: false,
        init() {
            modalManager.createModal(id, this);
        },
        // functionalities defined here can be used in the components directly
        toggle(e) {
            e.stopPropagation(); // stop propagation to prevent other elements retoggling the modal
            this.isOpen = !this.isOpen;
            const animatedBackdrop = document.getElementById('animated-backdrop');
            const body = document.body;
            animatedBackdrop.classList.toggle('hidden');
            body.classList.toggle('overflow-hidden');
        },
        handleClickOutside(e) {
            if (e.target == e.currentTarget) {
                this.toggle(e);
            }
        }
    }));
});
