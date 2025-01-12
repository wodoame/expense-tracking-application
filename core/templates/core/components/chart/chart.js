(async function(){
  const ctx = document.getElementById('myChart');
  let data = await fetchJSONData('/api/categories/?metrics=1');  
  data = data.filter((category)=>category.metrics.total_amount_spent > 0);
  const categoryName = data.map(category => category.name);
  const categoryData = data.map(category => category.metrics.total_amount_spent);
    
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: categoryName ,
      datasets: [{
        label: 'Amount Spent (GHS)',
        data: categoryData,
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
  document.getElementById('chart-loader').classList.add('hidden');
})()