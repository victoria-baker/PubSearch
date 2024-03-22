function keySearch(event) {
  if (event.key === 'Enter') {
    event.preventDefault();
    search();
  }
}

function search() {
  // Your dummy data
  var dummyData = [
    { title: "Result 1", description: "This is the first dummy result." },
    { title: "Result 2", description: "This is the second dummy result." },
    { title: "Result 3", description: "This is the third dummy result." }
  ];
  
  displayResults(dummyData);
}

function displayResults(data){
  // Clear previous search results
  document.getElementById('results').innerHTML = '';

  // Assuming you want to show the title and description
  data.forEach(result => {
    var resultDiv = document.createElement('div');
    resultDiv.className = 'result-item'; // Add some class for styling
    resultDiv.innerHTML = '<h2>' + result.title + '</h2><p>' + result.description + '</p>';
    document.getElementById('results').appendChild(resultDiv);
  });
}

// Attach the search function to the window object so it's available globally
window.search = search;
