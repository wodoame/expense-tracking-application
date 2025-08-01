import { BaseElement } from "./baseElement";
import { html, css, PropertyValues } from "lit";
import { customElement, property } from "lit/decorators.js";
import { routes } from "../../../../ts/router";
import axios from "axios";
import { getEditCategoryModal, getDeleteCategoryModal } from "../../../../ts/modals";
import { getDropdown } from "../../../../ts/utils";
import { initFlowbite } from "flowbite";
import { queryClient } from "./utils/setup";
import { filters } from "./catMetricFilter";
import { EventEmitter } from "../../../../ts/utils";

export let getCategories = undefined;
export let showSkeleton = undefined;
export const emitter = new EventEmitter();
emitter.addEventListener('expense_added_or_edited_or_deleted', () => {
    // Invalidate all queries whose key starts with 'categories'
    queryClient.invalidateQueries({
        predicate: (query) => {
            const queryKey = query.queryKey;
            return Array.isArray(queryKey) && queryKey[0] === 'categories';
        }
    });
});

export const toggleLoader = () => {
    const loader = document.getElementById('cat-page-loader');
    if(loader) loader.classList.toggle('hidden');
};

@customElement('categories-cards')
export class CategoriesCards extends BaseElement {
    @property({ type: Array }) accessor data: Category[] = [];
    @property({ type: Boolean}) accessor ready: boolean = false;

    getDataFxn() {
        return async (filter:number=filters.ALL_TIME) => {
            this.ready = false;
            const data = await queryClient.fetchQuery({
                queryKey: ['categories', filter],
                queryFn: () => this.fetchData(filter),
            });
            this.data = data;
            this.ready = true;
        };
    }

    getSkeletonFxn(){
        return()=>{
            this.ready = false;
        }
    }


    async fetchData (filter: number = filters.ALL_TIME): Promise<Category[]> {
    console.log('--- Axios: Fetching all categories ---');
    const response = await axios.get<Category[]>(`/api/categories/?metrics=1&filter=${filter}`);
    console.log(response.data);
    return response.data; // essential to return for caching
    }

    generateCards(data: Category[]){
        return data.map((category, _)=>{
            const dropdownId = `category-${category.id}`;
            return html`
             <div @click=${()=>{routes.category(category.name)}} class="cursor-pointer bg-gray-50 p-4 rounded-md border space-y-2 dark:bg-dark2 dark:border-darkborder">

    <!-- header   -->
         <div class="flex justify-between relative">
              <div class="text-gray-800 font-bold dark:text-gray-300">
              ${category.name}
             </div>
             ${category.name != 'None' ? html`
             <button @click=${(e:Event)=>e.stopPropagation()} data-dropdown-toggle=${dropdownId} data-dropdown-placement="bottom-end">
                 <svg xmlns="http://www.w3.org/2000/svg" class="stroke-gray-500 dark:stroke-gray-400 w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/></svg>
              </button>
              <categories-dropdown-menu id=${dropdownId} class="z-10 hidden" .data=${JSON.stringify(category)}></categories-dropdown-menu>
              `: html``}
         </div>
        <!--  / header -->
         <div class="flex items-center justify-between">
         <div class="text-gray-500">
             ${category.metrics.product_count} items
         </div>

             <div class="text-gray-800 font-medium dark:text-neutral-200">
              GHS ${category.metrics.total_amount_spent.toFixed(2)}
             </div>
         </div>
        </div>

        `});
    }

    protected firstUpdated(){
        getCategories = this.getDataFxn();
        showSkeleton = this.getSkeletonFxn();
        getCategories(); // Fetch initial data
    }

    updated(){
        initFlowbite();
    }

    render() {
        return html`
        ${this.ready ? html`
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            ${this.generateCards(this.data)}
        </div>
        ` : html`
        <categories-skeleton></categories-skeleton>
        `}
        `;
    }
}


// Dropdown
@customElement('categories-dropdown-menu')
export class CategoriesDropdownMenu extends BaseElement {
    @property({ type: String }) accessor data: string = '';

    handleEditClick(){
        getDropdown(this.id).hide();
        getEditCategoryModal().setDetails(this.data);
    }

    handleDeleteClick(){
        getDropdown(this.id).hide();
        getDeleteCategoryModal().setDetails(this.data);
    }

    render() {
        return html`
        <!-- Dropdown menu -->
        <div class="bg-white divide-y divide-gray-100 rounded shadow-md dark:border dark:bg-dark2 dark:border-darkborder dark:shadow-md dark:divide-darkborder w-44">
        <div class="px-4 py-3 text-sm text-gray-900 dark:text-white">
         <div class="font-bold dark:text-gray-300">Options</div>
        </div>
        <ul @click=${(e:Event)=>{e.stopPropagation()}} class="py-2 text-sm text-gray-700 dark:text-gray-200" aria-labelledby="dropdownDefaultButton">
                <li>
                <button @click=${this.handleEditClick} class="block text-start w-full px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white">Edit</button>
                </li>
                <li>
                <button @click=${this.handleDeleteClick} class="block text-start w-full px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white">Delete</button>
                </li>
             </ul>
        </div>
        `;
    }
}