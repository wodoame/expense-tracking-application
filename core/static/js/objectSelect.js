"use strict";
let objectSelect;
(function () {
    let listId;
    let objects = [];
    let selected = {};
    let submitProperty;
    let self;
    document.addEventListener('alpine:init', () => {
        Alpine.data('objectSelect', () => ({
            open: false,
            listId: listId,
            objects: objects,
            original: objects,
            isFocused: false,
            selected: selected,
            submitProperty: submitProperty,
            self: self,
            filter(e) {
                this.objects = this.original.filter((obj) => obj.name.toLowerCase().includes(e.currentTarget.value.toLowerCase()));
            },
            setCategory(category) {
                // TODO: some products don't have categories so I can't actually select one for them. Will find a workaround later.
                if (category) {
                    this.selected = category;
                }
                this.open = false;
            },
            setup() {
                const items = JSON.parse(document.getElementById(this.listId).textContent);
                const editProductForm = document.getElementById('edit-product-form');
                this.selected = items[0];
                this.original = items;
                this.objects = items;
                console.log(this);
                if (editProductForm.contains(this.self))
                    objectSelect = this;
                // I tried returning 'this.setCategory' to a global variable but I was not able to access 'this' object when I called the variable
                // I decided to return 'this' itself and this fixed that issue
            }
        }));
    });
})();
