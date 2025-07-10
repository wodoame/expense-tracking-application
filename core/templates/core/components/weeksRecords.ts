import { BaseElement } from "./baseElement";
import { html} from "lit";
import { customElement, property } from "lit/decorators.js";
import Alpine from "alpinejs";
import { fetchTextData } from "./utils/core";
import { routes } from "../../../../ts/router";

export interface WeekRecordsStore{
  data: Array<any> | undefined;
  useCachedData: boolean;
}

export const weeksRecordsStore = {
  data: undefined, 
  useCachedData: false
} as WeekRecordsStore;

@customElement('weeks-records')
export class WeeksRecords extends BaseElement {
    @property({ type: Array }) accessor data: Array<any> = [];
    @property({ type: Boolean }) accessor ready: boolean = false;

     async fetchData() {
        if(weeksRecordsStore.useCachedData && weeksRecordsStore.data){
          this.data = weeksRecordsStore.data;
          weeksRecordsStore.useCachedData = false; // reset the flag after using cached data (it's set to true only when the user navigates back to the page)
        }
        else{
          const response = await fetch('/api/weekly-spendings/');
          const data = await response.json();
          this.data = data;
          // Store the data in Alpine store for future use
          weeksRecordsStore.data = this.data;
        }

        this.ready = true;
    }

    populateData(data: Array<any>){
        const res = data.map((entry)=>html`
            <tr>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800 dark:text-neutral-200 link" 
                @click=${() => routes.viewWeek(entry.id, `${entry.week_start} - ${entry.week_end}`)}                
                >    
                ${entry.week_start} - ${entry.week_end}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-800 dark:text-neutral-200">
                    GHS ${entry.total_amount}
                </td>
            </tr>
        `)
        return res;
    }

    skeletonRows(nRows: number) {
        const res = [];
        for (let i = 0; i < nRows; i++) {
            res.push(html`
                <tr>
                   <td class="px-6 py-4">
                      <div class="h-4 w-32 record-skeleton"></div>
                    </td>
                   <td class="px-6 py-4">
                      <div class="h-4 w-12 record-skeleton"></div>
                    </td>
                </tr>
            `);
        }
        return res;
    }
    
    connectedCallback(): void {
        super.connectedCallback();
        this.fetchData();
    }

    render() {
        return html`
        <div class="p-4 bg-gray-50 dark:bg-dark2 dark:border-darkborder rounded-md border relative record">
            <h3 class="p-2  tracking-tight border-b dark:border-darkborder text-gray-900 dark:text-gray-300">
            <div class="flex items-center justify-between">
                <div class="text-xl font-bold">
                <!-- {{date|timesince}} -->
                </div>
            </div>   
            <div class="text-sm text-gray-500 dark:text-gray-400 font-medium my-2">
                <!-- {{ date | dateOnly}} -->
            </div>
            </h3>
        
    <div class="flex flex-col">
        <div class="-m-1.5 overflow-x-auto">
          <div class="p-1.5 min-w-full inline-block align-middle">
            <div class="overflow-hidden">
              <table class="min-w-full divide-y dark:divide-gray-100/5">
                <thead>
                  <tr>
                    <th scope="col" class="px-6 py-3 text-start text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Week</th>
                    <th scope="col" class="px-6 py-3 text-start text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Total</th>
                  </tr>
                </thead>
                <tbody class="divide-y dark:divide-gray-100/5">
                    ${this.ready?html`${this.populateData(this.data)}`:html`${this.skeletonRows(5)}`}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
 </div>
        `;
    }
}
