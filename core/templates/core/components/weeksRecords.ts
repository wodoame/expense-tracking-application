import { BaseElement } from "./baseElement";
import { html} from "lit";
import { customElement, property } from "lit/decorators.js";
import { routes } from "../../../../ts/router";
import { fetchJSONData } from "../../../../ts/utils";
export interface WeekRecordsStore{
  data: Array<any> | undefined;
  currentPages: number;
  numberOfPages: number;
  useCachedData: boolean;
}

export const weeksRecordsStore = {
  data: undefined, 
  currentPages: 1,
  numberOfPages: 1, 
  useCachedData: false
} as WeekRecordsStore;

@customElement('weeks-records')
export class WeeksRecords extends BaseElement {
    @property({ type: Array }) accessor data: Array<any> = [];
    @property({ type: Boolean }) accessor ready: boolean = false;
    @property({ type: Number }) accessor currentPage: number = 1;
    @property({ type: Number }) accessor numberOfPages: number = 1;

    nextPage(){
      if (this.currentPage < this.numberOfPages) {
          this.ready = false;
          this.currentPage++;
          this.fetchData();
      }
    }

    prevPage(){
      if (this.currentPage > 1) {
          this.ready = false;
          this.currentPage--;
          this.fetchData();
      }
    }

    getPage(page: number){
      if(page >= 1 && page <= this.numberOfPages && page !== this.currentPage){
        this.ready = false;
        this.currentPage = page;
        this.fetchData();
      }
    }

     async fetchData() {
        if(weeksRecordsStore.useCachedData && weeksRecordsStore.data){
          this.data = weeksRecordsStore.data;
          this.numberOfPages = weeksRecordsStore.numberOfPages;
          this.currentPage = weeksRecordsStore.currentPages;
          weeksRecordsStore.useCachedData = false; // reset the flag after using cached data (it's set to true only when the user navigates back to the page)
        }
        else{
          const data = await fetchJSONData(`/api/weekly-spendings/?page=${this.currentPage}`);
          this.data = data.weekly_spendings;
          this.numberOfPages = data.number_of_pages;
          this.currentPage = data.current_page;
          weeksRecordsStore.data = this.data;
          weeksRecordsStore.numberOfPages = this.numberOfPages;
          weeksRecordsStore.currentPages = this.currentPage;
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
    ${html`
      <weeks-records-paginator
      .nextFxn=${this.nextPage.bind(this)}
      .prevFxn=${this.prevPage.bind(this)}
      .getPageFxn=${this.getPage.bind(this)}
      .currentPage=${this.currentPage}
      .numberOfPages=${this.numberOfPages}
      >
      </weeks-records-paginator>`}
    `;
    }
  }
  