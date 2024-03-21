function keySearch(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      search();
    }
  }
  
function search() {
    var searchTerm = document.getElementById('searchInput').value;

}

function displayResults(data){
  // Clear previous search results
  document.getElementById('results').innerHTML = '';

  var allResults = document.getElementById('results');
  data.array.forEach(result => {
    var oneResult = document.createElement('div');
    oneResult.textContent = result.title;
    allResults.appendChild(oneResult)
  });
}
