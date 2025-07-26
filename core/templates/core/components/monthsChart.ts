import { BaseElement } from "./baseElement";
import { customElement, property } from "lit/decorators.js";
import { html, svg } from "lit";
import ApexCharts from "apexcharts";
import { fetchJSONData } from "../../../../ts/utils";
import { createElement } from "lucide";
import { Loader } from "lucide";
import { unsafeSVG } from "lit/directives/unsafe-svg.js";

export const monthlyChartData = {
    data: undefined, 
    useCachedData: false
}

@customElement('months-chart')
export class MonthsChart extends BaseElement{
   @property({ type: Array }) accessor data: Array<any> = [];
   @property({ type: Boolean }) accessor ready: boolean = false;

   chart: ApexCharts | null = null;
   observer: MutationObserver | null = null;

   // Define the formatter as a class method
    private tooltipFormatter(value: any, { dataPointIndex }: { dataPointIndex: number }): string {
    const categories = this.data.map((entry: any) => `${entry.month_start} - ${entry.month_end}`);
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
    colors: ['#f97316'], // Orange color
    grid: this.getGridOptions(),
    stroke: {
    curve: 'smooth',
    width: 1
    },
    markers: {
      size: 5,
      colors: ['#f97316'],
    //   strokeColors: '#fff',
      strokeWidth: 0,
      hover: {
        size: 7,
      }
    },
    series: [{
      name: 'Monthly Spendings',
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
    if(monthlyChartData.useCachedData && monthlyChartData.data){
        this.data = monthlyChartData.data // this data is assumed to be already sorted
        monthlyChartData.useCachedData = false // reset this so we can fetch again
    }
    else{
        const data = await fetchJSONData('/api/monthly-spendings/?limit=10');
        this.data = data.monthly_spendings.sort((a: any, b: any) => new Date(a.month_start).getTime() - new Date(b.month_start).getTime());
        monthlyChartData.data = this.data;
    }
    // reverse the data based on entry.month_start to display the most recent month last
    this.chart.updateSeries([{
        name: 'Monthly Spendings',
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
      class: "lucide lucide-loader animate-spin stroke-blue-500"
    }).outerHTML;
  

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
              svg`${unsafeSVG(spinnerSvg)}`
            }
          </div>
        ` : null}
        <div id="chart"></div>
    </div>
    `
   }
}
