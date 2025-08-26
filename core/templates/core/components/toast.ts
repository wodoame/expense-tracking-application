import { BaseElement } from "./baseElement";
import { html } from "lit";
import { customElement, property, state } from "lit/decorators.js";

export type ToastType = 'success' | 'error' | 'warning' | 'info';

interface ToastData {
    id: string;
    message: string;
    type: ToastType;
    autoDismiss?: boolean;
    duration?: number;
}

@customElement('app-toast')
export class AppToast extends BaseElement {
    @property({ type: String }) accessor message = '';
    @property({ type: String }) accessor type: ToastType = 'info';
    @property({ type: String }) accessor toastId = '';
    @property({ type: Boolean }) accessor autoDismiss = true;
    @property({ type: Number }) accessor duration = 2000;
    @state() private accessor isVisible = true;

    
    connectedCallback() {
        super.connectedCallback();
        if (this.autoDismiss) {
            setTimeout(() => {
                this.dismiss();
            }, this.duration);
        }
    }

    firstUpdated() {
        window.initFlowbite();
    }

    private getIcon() {
        switch (this.type) {
            case 'success':
                return html`
                   <div class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 text-green-500 bg-green-100 rounded-lg dark:bg-green-800 dark:text-green-200">
                        <svg class="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5Zm3.707 8.207-4 4a1 1 0 0 1-1.414 0l-2-2a1 1 0 0 1 1.414-1.414L9 10.586l3.293-3.293a1 1 0 0 1 1.414 1.414Z"/>
                        </svg>
                        <span class="sr-only">Check icon</span>
                    </div>
                `;
            case 'error':
                return html`
                    <div class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 text-red-500 bg-red-100 rounded-lg dark:bg-red-800 dark:text-red-200">
                        <svg class="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5Zm3.707 11.793a1 1 0 1 1-1.414 1.414L10 11.414l-2.293 2.293a1 1 0 0 1-1.414-1.414L8.586 10 6.293 7.707a1 1 0 0 1 1.414-1.414L10 8.586l2.293-2.293a1 1 0 0 1 1.414 1.414L11.414 10l2.293 2.293Z"/>
                        </svg>
                        <span class="sr-only">Error icon</span>
                    </div>
                `;
            case 'warning':
                return html`
                   <div class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 text-orange-500 bg-orange-100 rounded-lg dark:bg-orange-700 dark:text-orange-200">
                        <svg class="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5ZM10 15a1 1 0 1 1 0-2 1 1 0 0 1 0 2Zm1-4a1 1 0 0 1-2 0V6a1 1 0 0 1 2 0v5Z"/>
                        </svg>
                        <span class="sr-only">Warning icon</span>
                    </div>
                `;
            default: // info
                return html`
                    <div class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 text-blue-500 bg-blue-100 rounded-lg dark:bg-blue-800 dark:text-blue-200">
                        <svg class="w-4 h-4" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 18 20">
                            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.147 15.085a7.159 7.159 0 0 1-6.189 3.307A6.713 6.713 0 0 1 3.1 15.444c-2.679-4.513.287-8.737.888-9.548A4.373 4.373 0 0 0 5 1.608c1.287.953 6.445 3.218 5.537 10.5 1.5-1.122 2.706-3.01 2.853-6.14 1.433 1.049 3.993 5.395 1.757 9.117Z"/>
                        </svg>
                        <span class="sr-only">Fire icon</span>
                    </div>
                `;
        }
    }

    private dismiss() {
        this.isVisible = false;
        // Wait for animation to complete before removing from DOM
        setTimeout(() => {
            this.dispatchEvent(new CustomEvent('toast-dismiss', {
                detail: { id: this.toastId },
                bubbles: true
            }));
        }, 300);
    }
   

    render() {
        return html`
                ${this.getIcon()}
        
                <div class="ms-3 text-sm font-normal">${this.message}</div>
                <button type="button" class="ms-auto -mx-1.5 -my-1.5 bg-white text-gray-400 hover:text-gray-900 rounded-lg focus:ring-2 focus:ring-gray-300 p-1.5 hover:bg-gray-100 inline-flex items-center justify-center h-8 w-8 dark:text-gray-500 dark:hover:text-white dark:bg-gray-800 dark:hover:bg-gray-700" data-dismiss-target="#${this.toastId}" aria-label="Close">
                    <span class="sr-only">Close</span>
                    <svg class="w-3 h-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14">
                        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"/>
                    </svg>
                </button>
        `;
    }
}

@customElement('toast-container')
export class ToastContainer extends BaseElement {
    
    @state() private accessor toasts: ToastData[] = [];
    connectedCallback() {
        super.connectedCallback();
        // Listen for toast events from anywhere in the document
        document.addEventListener('show-toast', this.handleShowToast as EventListener);
    }

    disconnectedCallback() {
        super.disconnectedCallback();
        document.removeEventListener('show-toast', this.handleShowToast as EventListener);
    }

    private handleShowToast = (event: CustomEvent<ToastData>) => {
        this.addToast(event.detail);
    };

    private handleToastDismiss = (event: CustomEvent<{ id: string }>) => {
        this.removeToast(event.detail.id);
    };

    addToast(toastData: Omit<ToastData, 'id'>) {
        const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const toast: ToastData = {
            id,
            autoDismiss: true,
            duration: 5000,
            ...toastData
        };
        
        this.toasts = [...this.toasts, toast];
    }

    removeToast(id: string) {
        this.toasts = this.toasts.filter(toast => toast.id !== id);
    }

    render() {
        return html`
                ${this.toasts.map(toast => html`
                    <app-toast
                        id=${toast.id}
                        role="alert"
                        class="flex items-center w-full max-w-[26rem] p-4 mb-4 text-gray-500 bg-white rounded-lg shadow dark:text-gray-400 dark:bg-dark2 dark:shadow-dark1 dark:shadow-md"
                        .message=${toast.message}
                        .type=${toast.type}
                        .toastId=${toast.id}
                        .duration=${toast.duration}
                        @toast-dismiss=${this.handleToastDismiss}
                    ></app-toast>
                `)}
        `;
    }
}

// Global toast utility functions
export class ToastManager {
    static show(message: string, type: ToastType = 'info', options?: Partial<ToastData>) {
        const event = new CustomEvent('show-toast', {
            detail: {
                message,
                type,
                ...options
            }
        });
        document.dispatchEvent(event);
    }

    static success(message: string, options?: Partial<ToastData>) {
        this.show(message, 'success', options);
    }

    static error(message: string, options?: Partial<ToastData>) {
        this.show(message, 'error', options);
    }

    static warning(message: string, options?: Partial<ToastData>) {
        this.show(message, 'warning', options);
    }

    static info(message: string, options?: Partial<ToastData>) {
        this.show(message, 'info', options);
    }
}

function showToast(message: string, type: ToastType = 'info', options?: Partial<ToastData>) {
    ToastManager.show(message, type, options);
}

window['showToast'] = showToast;