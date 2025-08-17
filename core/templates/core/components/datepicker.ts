import { BaseElement } from "./baseElement";
import { html } from "lit";
import { customElement, property } from "lit/decorators.js";
import { Calendar } from "vanilla-calendar-pro";
@customElement('date-picker')
export class DatePicker extends BaseElement {
    @property({attribute: false}) accessor onSelectDate: (date: string) => void;
    @property({attribute: false}) accessor init: () => void;
    @property({type: String}) accessor currentDate: string;
    calendar: Calendar;
    private calendarId: string;

    constructor() {
        super();
        // Generate a unique ID for this calendar instance
        this.calendarId = `calendar-${Math.random().toString(36).substr(2, 9)}`;
    }

    firstUpdated(): void {
        const onSelectDate = this.onSelectDate;
        console.log(this.currentDate);
        
        this.calendar = new Calendar(`#${this.calendarId}`, {
            // Your settings
            dateToday: this.currentDate ? new Date(this.currentDate) : new Date(),
            styles: {
                calendar: 'calendar__custom',
                dateBtn: 'date__btn',
                monthsMonth: '', 
                yearsYear: '',
            }, 
            onClickDate(self, event) {
                const selectedDate = self.context.selectedDates[0];
                if (selectedDate && onSelectDate) {
                    onSelectDate(selectedDate);
                }

                // Remove data-date-selected from any previously selected button
                const previouslySelected = document.querySelector('[data-date-selected]');
                if (previouslySelected) {
                    previouslySelected.removeAttribute('data-date-selected');
                }
                
                // Add data-date-selected to the clicked button
                if (event.target && (event.target as HTMLElement).classList.contains('date__btn')) {
                    (event.target as HTMLElement).setAttribute('data-date-selected', 'true');
                }
            },
        });
        this.calendar.init();
    }

    disconnectedCallback(): void {
        this.calendar.destroy();
    }

    updated(){
        this.calendar.set(
            {
                dateToday: this.currentDate ? new Date(this.currentDate) : new Date()
            }
        );
    }

    render() {
        return html`<div id="${this.calendarId}"></div>`;
    }
}