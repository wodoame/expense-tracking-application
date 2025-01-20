(async function(){
  const ctx = document.getElementById('myChart');
  let data = await fetchJSONData('/api/categories/?metrics=1');  
  data.sort((a, b) => b.metrics.total_amount_spent - a.metrics.total_amount_spent);
  data = data.slice(0, 5);
  data = data.filter((category)=>category.metrics.total_amount_spent > 0);
  const categoryName = data.map(category => category.name);
  const categoryData = data.map(category => category.metrics.total_amount_spent);
    
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: categoryName,
      datasets: [{
        label: 'Amount Spent (GHS)',
        data: categoryData,
        borderWidth: 1
      }]
    },
    options: {
      responsive:false,
      scales: {
        y: {
          beginAtZero: true
        }, 
        x: {
          ticks: {
            autoSkip: false,  // Show all labels
            maxRotation: 45,   // Prevent tilting
            minRotation:0,    // Prevent tilting
          }
        }
      }
    }
  });
  document.getElementById('chart-loader').classList.add('hidden');
})()