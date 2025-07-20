import { html } from "lit";
import { customElement, property } from "lit/decorators.js";
import { map } from 'lit/directives/map.js';
import { BaseElement } from "./baseElement";

@customElement('weeks-records-paginator')
export class WeeksRecordsPaginator extends BaseElement {
    @property({ type: Number }) accessor currentPage: number = 1;
    @property({ type: Number }) accessor numberOfPages: number = 1;
    @property({ attribute:false}) accessor nextFxn!: () => void;
    @property({ attribute:false}) accessor prevFxn!: () => void;
    @property({ attribute:false}) accessor getPageFxn!: (page: number) => void;

    renderPageNumbers() {
    return map(Array.from({ length: this.numberOfPages }, (_, i) => i + 1), (page) => html`
        <li>
            <button
                type="button"
                class="flex items-center justify-center px-3 h-8 leading-tight ${this.currentPage === page ? 'text-blue-600 bg-blue-100 dark:bg-gray-700 dark:text-white' : 'text-gray-500 bg-white dark:bg-gray-800 dark:text-gray-400'} border border-gray-300 hover:bg-gray-100 hover:text-gray-700 dark:border-darkborder dark:hover:bg-gray-700 dark:hover:text-white"
                @click=${() => this.getPageFxn(page)}
            >
                ${page}
            </button>
        </li>
    `);
}

render() {
    return html`
    <nav aria-label="Page navigation example" class="flex items-center justify-center p-4">
      <ul class="inline-flex -space-x-px text-sm">
        <li>
          <button
            type="button"
            class="flex items-center justify-center px-3 h-8 ms-0 leading-tight text-gray-500 bg-white border border-e-0 border-gray-300 rounded-s-md hover:bg-gray-100 hover:text-gray-700 dark:bg-dark2 dark:border-darkborder dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white"
            @click=${() => this.prevPage()}
            ?disabled=${this.currentPage === 1}
          >Previous</button>
        </li>
        ${this.renderPageNumbers()}
        <li>
          <button
            type="button"
            class="flex items-center justify-center px-3 h-8 leading-tight text-gray-500 bg-white border border-gray-300 rounded-e-md hover:bg-gray-100 hover:text-gray-700 dark:bg-dark2 dark:border-darkborder dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white"
            @click=${() => this.nextPage()}
            ?disabled=${this.currentPage === this.numberOfPages}
          >Next</button>
        </li>
      </ul>
    </nav>
    `;
    }
    prevPage() {
        this.prevFxn();
    }

    nextPage() {
      this.nextFxn();
    }

    getPage(page: number){
      this.getPageFxn(page);
    }
}