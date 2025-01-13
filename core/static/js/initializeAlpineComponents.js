"use strict";
function createModalInstance(id) {
    return {
        isOpen: false,
        init() {
            modalManager.createModal(id, this);
        },
        // functionalities defined here can be used in the components directly
        open() {
            this.isOpen = true;
            this.toggleSideEffects(!this.isOpen);
            history.pushState(null, '');
            localStorage.setItem('modalOpen', 'true');
            modalManager.currentlyOpenModal = this;
        },
        close() {
            this.isOpen = false;
            this.toggleSideEffects(!this.isOpen);
            // no matter what closes the modal remove these from localStorage
            localStorage.removeItem('modalOpen');
            localStorage.removeItem('forwarded');
        },
        toggleSideEffects(force) {
            const animatedBackdrop = document.getElementById('animated-backdrop');
            const body = document.body;
            animatedBackdrop.classList.toggle('hidden', force); // note when force is true the class is added and if it's false it is removed
            body.classList.toggle('overflow-hidden', !force);
        },
        handleClickOutside(e) {
            if (e.target == e.currentTarget) {
                this.close();
            }
        }
    };
}
function createSelectFieldInstance(id) {
    return {
        isOpen: false,
        filtered: [], // represent filtered results
        items: [],
        isFocused: false,
        selected: {},
        submitProperty: '',
        newSearch: '',
        newCategory: {},
        none: { id: null, name: 'None' },
        async init() {
            selectFieldManager.setInstance(id, this);
            categoryPublisher.subscribe(this);
            const data = await fetchJSONData('/api/categories/');
            this.update(data);
            this.selected = this.none;
        },
        update(data) {
            this.items = [this.none, ...data];
            this.filtered = [...this.items];
        },
        open() {
            this.isOpen = true;
            this.isFocused = true;
        },
        close() {
            this.isOpen = false;
            this.selected = { ...this.selected };
            this.filtered = [...this.items];
            this.isFocused = false;
        },
        filter(e) {
            this.filtered = this.items.filter((obj) => obj.name.toLowerCase().includes(e.currentTarget.value.toLowerCase()));
            if (this.filtered.length == 0) {
                this.newSearch = e.currentTarget.value;
            }
        },
        select(selected) {
            this.selected = selected;
            this.isOpen = false;
            this.filtered = [...this.items];
        },
    };
}
function handleAlpineInitialization() {
    Alpine.data('baseModal', createModalInstance);
    Alpine.data('selectField', createSelectFieldInstance);
}
function initializeFlowbite() {
    window.initFlowbite();
}
document.addEventListener('alpine:init', handleAlpineInitialization);
document.addEventListener('htmx:afterSwap', initializeFlowbite);
window.addEventListener('popstate', handleCloseModal);
window.addEventListener('beforeunload', () => {
    document.removeEventListener('alpine:init', handleAlpineInitialization);
    window.removeEventListener('popstate', handleCloseModal);
    document.removeEventListener('htmx:afterSwap', initializeFlowbite);
});
