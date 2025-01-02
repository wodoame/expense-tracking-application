(function(){
  const ctx = document.getElementById('myChart');
  const categories = JSON.parse(document.getElementById('categories').textContent);
  const categoryName = categories.map(category => category.name);
  const categoryData = categories.map(category => category.product_count);
  
    
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
})()