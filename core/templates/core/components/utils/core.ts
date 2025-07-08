export async function fetchTextData(url: string){
      try{
      const response = await fetch(url);
      if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.text(); 
      return data;   
      }
      catch(e){
         console.log('Error fetching data ', e) 
      }
}