const currentDate = new Date(); 
console.log(currentDate);
console.log(currentDate.getDate());
const date = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0)
console.log(date.getDate()); // obtain last day of the month
console.log(date.getDay()); // obtain day of the week it is (1=Monday)
console.log(date.getDate() - date.getDay()); // obtain which day Sunday starts on the calendar





