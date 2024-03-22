function keySearch(event) {
  if (event.key === 'Enter') {
    event.preventDefault();
    search();
  }
}

// searchbar.js
function search() {
  var searchTerm = document.getElementById('searchInput').value;
  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/send-data', true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4 && xhr.status == 200) {
      var results = JSON.parse(xhr.responseText);
      displayResults(results);
    }
  };
  xhr.send(JSON.stringify({ data: searchTerm }));
}

function displayResults(data) {
  // Clear previous search results
  document.getElementById('results').innerHTML = '';
  // Display each result
  console.log("This is a message!");
  //alert("This is a message!");
  data.forEach(function (result, index) {
    var resultDiv = document.createElement('div');
    resultDiv.className = 'result-item';
    //resultDiv.innerHTML = '<h2>' + index + '. ' + result.title + '</h2><p>' + result.link + '</p>';
    resultDiv.innerHTML = '<h2>' + (index + 1) + '. ' + result + '</h2>';
    document.getElementById('results').appendChild(resultDiv);
  });
}


// Attach the search function to the window object so it's available globally
window.search = search;