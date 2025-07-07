import { BaseElement } from "./baseElement";
import { html} from "lit";
import { customElement, property } from "lit/decorators.js";

@customElement('weeks-records')
export class MyButton extends BaseElement {
    @property({ type: String }) accessor label = 'Click Me';

    render() {
        return html`
        <div class="p-4 bg-gray-50 dark:bg-dark2 dark:border-darkborder rounded-md border relative record" {% if edited %}hx-swap-oob="true"{% endif %} id="d-{{date|dateString}}" x-data="{id: $id('record')}">
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
                    <!-- checkbox -->
                    <!-- <th scope="col" class="p-4">
                      <div class="flex items-center">
                          <input id="checkbox-all-search" type="checkbox" class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded-sm focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 dark:focus:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
                          <label for="checkbox-all-search" class="sr-only">checkbox</label>
                      </div>
                    </th> -->
                    <th scope="col" class="px-6 py-3 text-start text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Week</th>
                    <th scope="col" class="px-6 py-3 text-start text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Total</th>
                    <!-- <th scope="col" class="px-6 py-3 text-start text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Category</th> -->
                    <!-- <th scope="col" class="px-6 py-3 text-start text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th> -->
                  </tr>
                </thead>
                <tbody class="divide-y dark:divide-gray-100/5">
                  <tr x-data="{data: $el.dataset.info}">
                    <!-- checkbox  -->
                    <!-- <td class="w-4 p-4">
                      <div class="flex items-center">
                          <input id="checkbox-table-search-1" type="checkbox" class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded-sm focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 dark:focus:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
                          <label for="checkbox-table-search-1" class="sr-only">checkbox</label>
                      </div>
                  </td> -->
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800 dark:text-neutral-200">
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-800 dark:text-neutral-200"></td>
                    <!-- <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-800 dark:text-neutral-200 link"></td>
                    <td>
                        <div class="price ps-6 flex gap-5">
                           <button>
                             <svg xmlns="http://www.w3.org/2000/svg" class="fill-teal-600" width="21" height="21" viewBox="0 0 24 24"><path d="M4 21a1 1 0 0 0 .24 0l4-1a1 1 0 0 0 .47-.26L21 7.41a2 2 0 0 0 0-2.82L19.42 3a2 2 0 0 0-2.83 0L4.3 15.29a1.06 1.06 0 0 0-.27.47l-1 4A1 1 0 0 0 3.76 21 1 1 0 0 0 4 21zM18 4.41 19.59 6 18 7.59 16.42 6zM5.91 16.51 15 7.41 16.59 9l-9.1 9.1-2.11.52z"></path></svg>
                           </button>
               
                           <button>
                             <svg xmlns="http://www.w3.org/2000/svg" class="fill-pink-600" width="21" height="21" viewBox="0 0 24 24"><path d="M15 2H9c-1.103 0-2 .897-2 2v2H3v2h2v12c0 1.103.897 2 2 2h10c1.103 0 2-.897 2-2V8h2V6h-4V4c0-1.103-.897-2-2-2zM9 4h6v2H9V4zm8 16H7V8h10v12z"></path></svg>
                           </button>
                        </div>
                    </td> -->
                  </tr>
          
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