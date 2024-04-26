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

var relList = [];
var irrelList = [];

// searchbar.js
function search() {
  relList = [];
  irrelList = [];
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
  xhr.send(JSON.stringify({data: searchTerm}));
}

function rerunSearch(){
  if (relList.length > 0 && irrelList.length > 0){
  // var xhr = new XMLHttpRequest();
  // xhr.open('POST', '/send-lists', true);
  // xhr.setRequestHeader('Content-Type', 'application/json');
  // xhr.onreadystatechange = function () {
  //   if (xhr.readyState == 4 && xhr.status == 200) {
  //     var results = JSON.parse(xhr.responseText);
  //     displayResults(results);
  //   }
  // };
  // xhr.send(JSON.stringify({
  //   rel_list: relList,
  //   irrel_list: irrelList
  // }));
  relList = [];
  irrelList = [];
}
}

function relevance(type, index){
  if (type == 'up'){
    var indexListIrrel = irrelList.indexOf(index);
    if (indexListIrrel !== -1) {
      irrelList.splice(indexListIrrel, 1);
    }
    relList.push(index);
  } else if (type == 'down'){
    var indexListRel = relList.indexOf(index);
    if (indexListRel !== -1) {
      relList.splice(indexListRel, 1);
    }
  irrelList.push(index)
  }
  // window.alert(relList);
  // window.alert(irrelList);
}

function changeColor(type, index){
  var upButton = document.getElementById('thumbs-up-' + index);
  var downButton = document.getElementById('thumbs-down-' + index);
  if (type == 'up'){
    upButton.style.color = '#5555FF';
    downButton.style.color = '#6d6d6d';
  }
  else if (type =='down'){
    downButton.style.color = '#5555FF';
    upButton.style.color = '#6d6d6d';
  }
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

    var citationsElement = document.createElement('span');
    citationsElement.innerHTML = 'Citation Count: ' + citations;

    var thumbsUpButton = document.createElement('button');
    thumbsUpButton.innerHTML = '<i class="fas fa-thumbs-up"></i>';
    thumbsUpButton.className = 'thumbs-up';
    thumbsUpButton.id = 'thumbs-up-' + index;
    thumbsUpButton.onclick = function () {
      relevance('up', index);
      changeColor('up', index);
    };

    var thumbsDownButton = document.createElement('button');
    thumbsDownButton.innerHTML = '<i class="fas fa-thumbs-down"></i>';
    thumbsDownButton.className = 'thumbs-down';
    thumbsDownButton.id = 'thumbs-down-' + index;
    thumbsDownButton.onclick = function () {
      relevance('down', index);
      changeColor('down', index);
    };

    var buttonContainer = document.createElement('div');
    buttonContainer.className = 'button-container';
    buttonContainer.appendChild(thumbsUpButton);
    buttonContainer.appendChild(thumbsDownButton);

    resultDiv.appendChild(citationsElement);
    resultDiv.appendChild(buttonContainer);

    document.getElementById('results').appendChild(resultDiv);
  });
  display_finish();
  display_results_container();
  // console.log('relList:', relList);
}

// Attach the search function to the window object so it's available globally
window.search = search;