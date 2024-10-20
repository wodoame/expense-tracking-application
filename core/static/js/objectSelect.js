"use strict";
let setCategory;
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
            objects: objects, // represent filtered results
            original: objects,
            isFocused: false,
            selected: selected,
            submitProperty: submitProperty,
            self: self,
            filter(e) {
                this.objects = this.original.filter((obj) => obj.name.toLowerCase().includes(e.currentTarget.value.toLowerCase()));
            },
            setup() {
                const items = [{ id: null, name: 'None' }, ...JSON.parse(document.getElementById(this.listId).textContent)]; // added a default selected to be None
                const editProductForm = document.getElementById('edit-product-form');
                this.selected = items[0];
                this.original = items;
                this.objects = items;
                if (editProductForm.contains(this.self))
                    setCategory = (category) => {
                        // TODO: some products don't have categories so I can't actually select one for them. Will find a workaround later.
                        if (category) {
                            this.selected = category;
                        }
                        else {
                            this.selected = { id: null, name: 'None' };
                        }
                        this.open = false;
                    };
                // I tried returning 'this.setCategory' to a global variable but I was not able to access 'this' object when I called the variable
                // I decided to return 'this' itself and this fixed that issue
            }
        }));
    });
})();
