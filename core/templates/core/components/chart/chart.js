(async function(){
  const ctx = document.getElementById('myChart');
  const data = await fetchJSONData('/api/categories/');  
  const categoryName = data.map(category => category.name);
  const categoryData = data.map(category => category.product_count);
    
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: categoryName ,
      datasets: [{
        label: 'Amount Spent',
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