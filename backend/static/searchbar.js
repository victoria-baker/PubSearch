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
  results_container.style.display= "block";
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
    
    var titleElement = document.createElement('span'); // Create a span for title
    titleElement.className = 'result-title';
    titleElement.textContent = title;
    titleElement.onclick = function() { window.open(linky, '_blank'); }; // Open link in new tab
    titleElement.style.cursor = 'pointer'; // Make it look clickable

    var final_result = document.createElement('h2');
    final_result.appendChild(titleElement);
    resultDiv.appendChild(final_result);

    var abstractElement = document.createElement('p');
    abstractElement.innerHTML = abstract;
    resultDiv.appendChild(abstractElement);

    var final_result = title.link(linky);
    //resultDiv.innerHTML = '<h2>' + index + '. ' + result.title + '</h2><p>' + result.link + '</p>';
    var title_html = document.createElement('h2');
    title_html.classList.add('title-link');
    title_html.innerHTML = final_result;
    resultDiv.appendChild(title_html);
    resultDiv.innerHTML += '<br>' + abstract;
    
    document.getElementById('results').appendChild(resultDiv);
  });
  display_finish();
  display_results_container();
}


// Attach the search function to the window object so it's available globally
window.search = search;