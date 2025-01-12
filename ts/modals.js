var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var ModalManager = /** @class */ (function () {
    function ModalManager() {
        this.modals = {}; // a store of created modals
        this.currentlyOpenModal = null;
    }
    ModalManager.prototype.createModal = function (id, modalInstance) {
        this.modals[id] = modalInstance;
    };
    ModalManager.prototype.getModal = function (id) {
        return this.modals[id];
    };
    return ModalManager;
}());
var modalManager = new ModalManager();
// link a modal with this class to control basic modal functionality
var BaseModal = /** @class */ (function () {
    function BaseModal(id) {
        this.modal = modalManager.getModal(id);
    }
    BaseModal.prototype.open = function () {
        this.modal.open();
    };
    BaseModal.prototype.close = function () {
        this.modal.close();
    };
    return BaseModal;
}());
var AddProductModal = /** @class */ (function (_super) {
    __extends(AddProductModal, _super);
    function AddProductModal() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    AddProductModal.prototype.submitForm = function () {
        var form = document.getElementById('add-product-form');
        if (form.checkValidity()) {
            document.getElementById('main-content').innerHTML = router.routes[router.currentRoute]; // insert the placeholder without triggering htmx
            this.close();
            var target = '#main-content';
            if (router.currentRoute == '/all-expenditures/') {
                target = '#all-expenditures'; // put the content inside #all-expenditures div instead of #main-content
            }
            var formData = htmx.values(form);
            htmx.ajax('POST', '/implementations/dashboard/', {
                values: formData,
                target: target,
            }).then(function () {
                categoryPublisher.fetchLatest();
            });
            form.reset();
            var field = selectFieldManager.getInstance('categories-add-product');
            field.select(field.none);
        }
        else {
            form.reportValidity();
        }
    };
    return AddProductModal;
}(BaseModal));
var AddCategoryModal = /** @class */ (function (_super) {
    __extends(AddCategoryModal, _super);
    function AddCategoryModal() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return AddCategoryModal;
}(BaseModal));
var DataFields = /** @class */ (function () {
    function DataFields() {
        // data fields 
        this.dataFields = {};
    }
    DataFields.prototype.setDataField = function (key, value) {
        this.dataFields[key] = value;
    };
    return DataFields;
}());
;
var FormFields = /** @class */ (function () {
    function FormFields() {
        // form fields 
        this.formFields = {};
    }
    FormFields.prototype.setFormField = function (key, value) {
        this.formFields[key] = value;
    };
    return FormFields;
}());
var ShowDetailsModal = /** @class */ (function (_super) {
    __extends(ShowDetailsModal, _super);
    function ShowDetailsModal(id, df) {
        var _this = _super.call(this, id) || this;
        _this.df = df;
        return _this;
    }
    ShowDetailsModal.prototype.setDetails = function (data) {
        var product = JSON.parse(data);
        var dataFields = this.df.dataFields;
        // set data field text contents
        dataFields.name.textContent = product.name;
        dataFields.price.textContent = "GHS ".concat(product.price.toFixed(2));
        dataFields.category.textContent = product.category ? product.category.name : 'None';
        dataFields.description.textContent = product.description || 'No description';
        this.open();
    };
    return ShowDetailsModal;
}(BaseModal));
var DeleteProductModal = /** @class */ (function (_super) {
    __extends(DeleteProductModal, _super);
    function DeleteProductModal(id, df, ff) {
        var _this = _super.call(this, id) || this;
        _this.df = df;
        _this.ff = ff;
        return _this;
    }
    DeleteProductModal.prototype.setDetails = function (data) {
        var product = JSON.parse(data);
        var dataFields = this.df.dataFields;
        var formFields = this.ff.formFields;
        // set data field text contents
        dataFields.name.textContent = product.name;
        dataFields.price.textContent = "GHS ".concat(product.price.toFixed(2));
        dataFields.category.textContent = product.category ? product.category.name : 'None';
        dataFields.description.textContent = product.description || 'No description';
        // set form field values
        formFields.id.value = product.id.toString();
        formFields.date.value = product.date;
        this.open();
    };
    DeleteProductModal.prototype.submitForm = function () {
        var form = document.getElementById('delete-product-form');
        var formData = htmx.values(form);
        var tr = htmx.find("#product-".concat(formData.id));
        var elementToReplace = htmx.closest(tr, '.record');
        elementToReplace.querySelector('.skeleton').classList.remove('hidden');
        this.close();
        htmx.ajax('POST', '/implementations/dashboard/?delete=1', {
            values: formData,
            target: elementToReplace,
            swap: 'outerHTML'
        });
    };
    return DeleteProductModal;
}(BaseModal));
var EditProductModal = /** @class */ (function (_super) {
    __extends(EditProductModal, _super);
    function EditProductModal(id, ff) {
        var _this = _super.call(this, id) || this;
        _this.ff = ff;
        return _this;
    }
    EditProductModal.prototype.setDetails = function (data) {
        var product = JSON.parse(data);
        var formFields = this.ff.formFields;
        var priceParts = product.price.toString().split('.');
        formFields.name.value = product.name;
        formFields.cedis.value = priceParts[0];
        console.log(priceParts);
        if (product.category) {
            formFields.category.value = product.category.id.toString();
        }
        if (priceParts.length == 2) {
            formFields.pesewas.value = priceParts[1];
        }
        else {
            formFields.pesewas.value = '00';
        }
        formFields.id.value = product.id.toString();
        formFields.description.value = product.description;
        formFields.date.value = product.date;
        this.setCategory(product.category);
        this.open();
    };
    EditProductModal.prototype.setCategory = function (category) {
        var field = selectFieldManager.getInstance('categories-edit-product');
        if (category) {
            field.select(category);
        }
        else {
            field.select({ id: null, name: 'None' });
        }
    };
    EditProductModal.prototype.submitForm = function () {
        var form = document.getElementById('edit-product-form');
        if (form.checkValidity()) {
            var formData = htmx.values(form);
            var tr = htmx.find("#product-".concat(formData.id));
            var elementToReplace = htmx.closest(tr, '.record');
            elementToReplace.querySelector('.skeleton').classList.remove('hidden');
            this.close();
            htmx.ajax('POST', '/implementations/dashboard/?edit=1', {
                values: formData,
                target: elementToReplace,
                swap: 'outerHTML'
            }).then(function () {
                categoryPublisher.fetchLatest();
            });
        }
        else {
            form.reportValidity(); // display the validation messages
        }
    };
    return EditProductModal;
}(BaseModal));
var CategoryDetailsModal = /** @class */ (function (_super) {
    __extends(CategoryDetailsModal, _super);
    function CategoryDetailsModal(id, df) {
        var _this = _super.call(this, id) || this;
        _this.df = df;
        return _this;
    }
    CategoryDetailsModal.prototype.setDetails = function (data) {
        var category = JSON.parse(data);
        var dataFields = this.df.dataFields;
        // set data field text contents
        dataFields.name.textContent = category.name;
        dataFields.product_count.textContent = category.product_count.toString();
        dataFields.description.textContent = category.description || 'No description';
        this.open();
    };
    return CategoryDetailsModal;
}(BaseModal));
var getAddProductModal = (function () {
    var instance = undefined; // just a reference to the modal if it has been called already 
    return function () {
        if (instance) {
            return instance;
        }
        instance = new AddProductModal('add-product-modal');
        return instance;
    };
})();
var getAddCategoryModal = (function () {
    var instance = undefined; // just a reference to the modal if it has been called already 
    return function () {
        if (instance) {
            return instance;
        }
        instance = new AddCategoryModal('add-category-modal');
        return instance;
    };
})();
var getDeleteProductModal = (function () {
    var instance = undefined;
    return function () {
        if (instance) {
            return instance;
        }
        var df = new DataFields();
        var ff = new FormFields();
        instance = new DeleteProductModal('delete-product-modal', df, ff);
        return instance;
    };
})();
var getShowDetailsModal = (function () {
    var instance = undefined;
    return function () {
        if (instance) {
            return instance;
        }
        var df = new DataFields();
        instance = new ShowDetailsModal('show-details-modal', df);
        return instance;
    };
})();
var getEditProductModal = (function () {
    var instance = undefined;
    return function () {
        if (instance) {
            return instance;
        }
        var ff = new FormFields();
        instance = new EditProductModal('edit-product-modal', ff);
        return instance;
    };
})();
var getCategoryDetailsModal = (function () {
    var instance = undefined;
    return function () {
        if (instance) {
            return instance;
        }
        var df = new DataFields();
        instance = new CategoryDetailsModal('category-details-modal', df);
        return instance;
    };
})();
function handleCloseModal() {
    if (localStorage.getItem('modalOpen')) {
        localStorage.removeItem('modalOpen');
        localStorage.setItem('forwarded', 'true');
        history.forward();
    }
    else if (localStorage.getItem('forwarded')) {
        modalManager.currentlyOpenModal.close();
    }
}
