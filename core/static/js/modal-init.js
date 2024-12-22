"use strict";
class ModalManager {
    constructor() {
        this.modals = {}; // a store of created modals
        this.currentlyOpenModal = null;
    }
    createModal(id, modalInstance) {
        this.modals[id] = modalInstance;
    }
    getModal(id) {
        return this.modals[id];
    }
}
const modalManager = new ModalManager();
function handleAlpineInitialization() {
    createModal();
}
function createModalInstance(id) {
    return {
        isOpen: false,
        init() {
            modalManager.createModal(id, this);
        },
        // functionalities defined here can be used in the components directly
        toggle() {
            this.isOpen = !this.isOpen;
            const animatedBackdrop = document.getElementById('animated-backdrop');
            const body = document.body;
            animatedBackdrop.classList.toggle('hidden');
            body.classList.toggle('overflow-hidden');
            if (this.isOpen) {
                history.pushState(null, '');
                localStorage.setItem('modalOpen', 'true');
                modalManager.currentlyOpenModal = this;
            }
        },
        handleClickOutside(e) {
            if (e.target == e.currentTarget) {
                this.toggle();
            }
        }
    };
}
function createModal() {
    Alpine.data('baseModal', createModalInstance);
}
function handleCloseModal() {
    if (localStorage.getItem('modalOpen')) {
        localStorage.removeItem('modalOpen');
        localStorage.setItem('forwarded', ' true');
        history.forward();
    }
    else if (localStorage.getItem('forwarded')) {
        localStorage.removeItem('forwarded');
        modalManager.currentlyOpenModal.toggle();
    }
}
window.addEventListener('popstate', handleCloseModal);
document.addEventListener('alpine:init', handleAlpineInitialization);
window.addEventListener('beforeunload', () => {
    document.removeEventListener('alpine:init', handleAlpineInitialization);
    window.removeEventListener('popstate', handleCloseModal);
});
