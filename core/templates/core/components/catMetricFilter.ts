import { BaseElement } from "./baseElement";
import { html } from "lit";
import { customElement, property } from "lit/decorators.js";
import { getCategories } from "./categories";
import { getDropdown } from "../../../../ts/utils";

export const filters = {
 ALL_TIME: 0,
 THIS_WEEK: 1,
 LAST_WEEK: 2,
 THIS_MONTH: 3,
 LAST_MONTH: 4,
 THIS_YEAR: 5,
 LAST_YEAR: 6,
 CUSTOM: 7
};

@customElement('cat-metric-filter')
export class CatMetricFilter extends BaseElement {
    @property({ type: String })
    accessor selectedFilter: string = 'This week';

    async selectFilter(key:string, filter:number){
        this.selectedFilter = key;
        getDropdown('dropdown').hide();
        await getCategories(filter);
    }
    renderList() {
        const items: [string, number][] = [
            ['All-time', filters.ALL_TIME],
            ['This week', filters.THIS_WEEK],
            ['Last week', filters.LAST_WEEK],
            ['This month', filters.THIS_MONTH],
            ['Last month', filters.LAST_MONTH],
            // ['This year', filters.THIS_YEAR],
            // ['Last year', filters.LAST_YEAR],
            // ['Custom', filters.CUSTOM]
        ]; 
        return items.map(([key, value]) => html`
            <li @click=${()=>{this.selectFilter(key, value)}}>
                <button class="flex w-full text-start justify-between px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white">
                ${key}
                ${
                    this.selectedFilter == key? html`<svg xmlns="http://www.w3.org/2000/svg" width="21" height="21" viewBox="0 0 24 24" class="stroke-teal-500" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>`:''
                }
            </button>
            </li>
        `);
    }

    firstUpdated(){
    }
    render() {
        return html`
         <button id="dropdownDefaultButton" data-dropdown-toggle="dropdown" class="option flex text-sm items-center text-gray-800 dark:text-neutral-200" type="button">${this.selectedFilter}<svg class="w-2.5 h-2.5 ms-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 10 6">
        <path class="text-gray-500 dark:text-gray-400" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 4 4 4-4"/>
        </svg>
        </button>

        <!-- Dropdown menu -->
        <div id="dropdown" class="z-10 hidden bg-white divide-y divide-gray-100 rounded shadow-md dark:border dark:bg-dark2 dark:border-darkborder dark:shadow-md dark:divide-darkborder w-44">
            <ul class="py-2 text-sm text-gray-700 dark:text-gray-200" aria-labelledby="dropdownDefaultButton">
                ${this.renderList()}
            </ul>
        </div>
        `
    }
}