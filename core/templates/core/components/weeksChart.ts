import { BaseElement } from "./baseElement";
import { customElement, property } from "lit/decorators.js";
import { html, svg } from "lit";
import ApexCharts from "apexcharts";
import { fetchJSONData } from "../../../../ts/utils";
import { createElement } from "lucide";
import { Loader } from "lucide";

export const weeklyChartData = {
    data: undefined, 
    useCachedData: false
}

@customElement('weeks-chart')
export class WeeksChart extends BaseElement{
   @property({ type: Array }) accessor data: Array<any> = [];
   @property({ type: Boolean }) accessor ready: boolean = false;

   chart: ApexCharts | null = null;
   observer: MutationObserver | null = null;

   // Define the formatter as a class method
    private tooltipFormatter(value: any, { dataPointIndex }: { dataPointIndex: number }): string {
    const categories = this.data.map((entry: any) => `${entry.week_start} - ${entry.week_end}`);
    return categories[dataPointIndex];
  }

   // options

   getToolTipOptions () {
       return {
           theme: this.getisDark() ? 'dark' : 'light', // Use dark theme for tooltips in dark mode
            style: {
                fontFamily: 'Poppins-Regular'
            },
           x: {
               formatter: this.tooltipFormatter.bind(this), // Bind the method to the class instance
           },
       };
   }

   getLabelsStyleOptions(){
     return  {
        colors: this.getisDark() ? '#9ca3af' : '#1f2937', // White in dark mode, black in light mode
       fontFamily: 'Poppins-Regular', 
    }
   }

   getGridOptions(){
    return {
      borderColor: this.getisDark() ? '#f3f4f60d' : '#e5e7eb',
    }
   }

   getisDark(){
    return document.documentElement.classList.contains('dark');
   }

   getXaxisOptions(){
    return {
      labels: {
        style: this.getLabelsStyleOptions()
      },
      axisBorder: {
        color: this.getisDark() ? '#f3f4f60d' : '#e5e7eb'
      }, 
      axisTicks: {
        color: this.getisDark() ? '#f3f4f60d' : '#e5e7eb'
      }
    };
  }

  getYaxisOptions(){
    return {
      labels: {
        style: this.getLabelsStyleOptions()
      }
    };
  }

renderChart(){
// Detect dark mode (using Tailwind's 'dark' class on <html>)

 const options = {
    chart: {
      type: 'line', 
      toolbar: {
      show: false // Hides the interactivity panel (download, zoom, pan, etc.)
        },
        zoom: {
        enabled: false // Disables zooming
        }
    },
    grid: this.getGridOptions(),
    stroke: {
    curve: 'smooth',
    width: 1
    }, 
    series: [{
      name: 'Weekly Spendings',
      data: this.data.map((entry)=>entry.total_amount)
    }],
    xaxis: this.getXaxisOptions(),
    yaxis: this.getYaxisOptions(),
    tooltip: this.getToolTipOptions()
 };

// Query the chart container from the light DOM
const chartEl = this.querySelector("#chart");
if (chartEl) {
    this.chart = new ApexCharts(chartEl, options);
    this.chart.render();
}

}

updateColors(){
  
    if (this.chart) {
        this.chart.updateOptions({
            xaxis: this.getXaxisOptions(),
            yaxis: this.getYaxisOptions(),
            tooltip: this.getToolTipOptions(), 
            grid: this.getGridOptions()
        });
    }
}

async fetchData(){
    if(weeklyChartData.useCachedData && weeklyChartData.data){
        this.data = weeklyChartData.data // this data is assumed to be already sorted
        weeklyChartData.useCachedData = false // reset this so we can fetch again
    }
    else{
        const data = await fetchJSONData('/api/weekly-spendings/?limit=10') as Array<any>;
        this.data = data.sort((a: any, b: any) => new Date(a.week_start).getTime() - new Date(b.week_start).getTime());
        weeklyChartData.data = this.data;
    }
    // reverse the data based on entry.week_start to display the most recent week last
    this.chart.updateSeries([{
        name: 'Weekly Spendings',
        data: this.data.map((entry) => entry.total_amount)
    }]); // Render the chart after fetching data
    this.ready = true;
}

firstUpdated() {
    this.ready = false; 
    this.renderChart();
    this.fetchData();

    // Observe changes to the 'dark' class on <html>
    this.observer = new MutationObserver(() => {
        this.updateColors(); // Update colors when theme changes
    });
    this.observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    if (this.observer) {
      this.observer.disconnect();
    }
    if (this.chart) {
      this.chart.destroy();
    }
  }

 render() {
    const spinnerSvg = createElement(Loader, { 
      color: "#888", 
      size: 40, 
      class: "lucide lucide-loader animate-spin"
    }).outerHTML;
    /*
    I tried using lit to render the svg but with 
    lit you can only render a literal value and not the value contained in a variable
    I had to just log it and copy the value
    I must find a workaround
    */ 
    

    return html`
    <div style="position:relative;">
        ${!this.ready ? html`
          <div style="
            position:absolute;
            inset:0;
            display:flex;
            align-items:center;
            justify-content:center;
            z-index:10;
          ">
            ${
                svg`
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" color="#888" size="40" class="lucide lucide-loader animate-spin stroke-blue-500"><path d="M12 2v4"></path><path d="m16.2 7.8 2.9-2.9"></path><path d="M18 12h4"></path><path d="m16.2 16.2 2.9 2.9"></path><path d="M12 18v4"></path><path d="m4.9 19.1 2.9-2.9"></path><path d="M2 12h4"></path><path d="m4.9 4.9 2.9 2.9"></path></svg>
                `}
          </div>
        ` : null}
        <div id="chart"></div>
    </div>
    `
   }
}