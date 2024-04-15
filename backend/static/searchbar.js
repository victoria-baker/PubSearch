function keySearch(event) {
  if (event.key === 'Enter') {
    event.preventDefault();
    search();
  }
}

function display_searching() {
  var main_text = document.getElementById('welcomeText');
  main_text.innerText = "Returning results from your search...";
}

function display_finish() {
  var main_text = document.getElementById('welcomeText');
  main_text.innerText = "Does this look right?";
}

function display_results_container() {
  var results_container = document.getElementById('resultsContainer');
  results_container.style.display = "block";
}

// searchbar.js
function search() {
  display_searching();
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
  // Displays message if there are no results
  if (data.length === 0) {
    // Display a message indicating no results found
    document.getElementById('results').innerHTML = '<p>No articles found. Please input another query.</p>';
    display_finish();
    return;
  }
  //alert("This is a message!");
  data.forEach(function (result, index) {
    var resultDiv = document.createElement('div');
    resultDiv.className = 'result-item';

    var parts = result.split("@");
    var title = parts[0]; // publication title
    var linky = parts[1]; // publication link
    var abstract = parts[2]; // abstract
    var citations = parts[3]; // citations

    var titleElement = document.createElement('span');
    titleElement.className = 'result-title';
    titleElement.textContent = title;
    titleElement.onclick = function () { window.open(linky, '_blank'); };
    titleElement.style.cursor = 'pointer';

    resultDiv.appendChild(titleElement); // Append the title element

    var abstractElement = document.createElement('p');
    abstractElement.innerHTML = abstract;
    resultDiv.appendChild(abstractElement); // Append the abstract

    var citationsElement = document.createElement('p');
    citationsElement.innerHTML = 'Citation Count:  ' + citations;
    resultDiv.appendChild(citationsElement); // Append the citations

    document.getElementById('results').appendChild(resultDiv); // Append resultDiv to the container
  });
  display_finish();
  display_results_container();
}


// Attach the search function to the window object so it's available globally
window.search = search;