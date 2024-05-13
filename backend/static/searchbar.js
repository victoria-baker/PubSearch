// when user presses enter, search runs
function keySearch(event) {
  if (event.key === 'Enter') {
    event.preventDefault();
    search();
  }
}

// Changes text to show that search is running
function display_searching() {
  var main_text = document.getElementById('welcomeText');
  main_text.innerText = "Returning results from your search...";
}

// Changes text to show that search is done
function display_finish() {
  var main_text = document.getElementById('welcomeText');
  main_text.innerText = "Does this look right?";
}

function display_results_container() {
  var results_container = document.getElementById('resultsContainer');
  results_container.style.display = "block";
}

// Event for when user clicks the filter button
function openFilter(){
  var filterButton = document.getElementById('filter');
  var filterAspects = document.getElementById('filterAspects');
  if (filterButton.classList.contains("active-button")){
    filterButton.classList.remove("active-button");
    filterAspects.classList.add("hidden")
  } else{
    filterButton.classList.add("active-button")
    filterAspects.classList.remove("hidden")
  }
}

// Defining lists for Rocchio's globally
var relList = [];
var irrelList = [];

// Sends query to backend and retrives results of search
function search() {
  var filterAlert = document.getElementById('filterAlert');
  filterAlert.classList.add("hidden")
  var minYear = document.getElementById("minYear").value;
  var maxYear = document.getElementById("maxYear").value;
  var author = document.getElementById("authorName").value;
  if (parseInt(minYear) > parseInt(maxYear)){
    filterAlert.classList.remove("hidden")
  } else{
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
    xhr.send(JSON.stringify({
      search_term: searchTerm,
      sy: minYear,
      ey: maxYear,
      author: author
  }));
  }
  var rocchioButton = document.getElementById('rocchio');
  rocchioButton.classList.remove("filter-button");
}

// Runs Rocchio's if user has selected at least one relevant article and one irrelevant article
function rerunSearch(){
  if (relList.length > 0 && irrelList.length > 0){
    var searchTerm = document.getElementById('searchInput').value;
    var minYear = document.getElementById("minYear").value;
    var maxYear = document.getElementById("maxYear").value;
    var author = document.getElementById("authorName").value;
    if (parseInt(minYear) > parseInt(maxYear)){
      filterAlert.classList.remove("hidden")
    } else{
      display_searching();
      var xhr = new XMLHttpRequest();
      xhr.open('POST', '/send-lists', true);
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
          var results = JSON.parse(xhr.responseText);
          displayResults(results);
        }
      };
      xhr.send(JSON.stringify({
        search_term: searchTerm,
        rel_list: relList,
        irrel_list: irrelList,
        sy: minYear,
        ey: maxYear,
        author: author
      }));
      relList = [];
      irrelList = [];
    }
  }
  var rocchioButton = document.getElementById('rocchio');
  rocchioButton.classList.remove("filter-button");
}

// Updates relevant and irrelevant lists if user click's a thumbs up/down
function relevance(type, index){
  var indexListIrrel = irrelList.indexOf(index);
  var indexListRel = relList.indexOf(index);
  if (type == 'up'){
    var indexListIrrel = irrelList.indexOf(index);
    if (indexListIrrel !== -1) {
      irrelList.splice(indexListIrrel, 1);
    }
    if (indexListRel !== -1) {
      relList.splice(indexListRel, 1);
    }
    else{
    relList.push(index);
    }
  } else if (type == 'down'){
    if (indexListRel !== -1) {
      relList.splice(indexListRel, 1);
    }
    if (indexListIrrel !== -1) {
      irrelList.splice(indexListIrrel, 1);
    }
    else{
    irrelList.push(index)
    }
  }
  // window.alert(relList);
  // window.alert(irrelList);
  var rocchioButton = document.getElementById('rocchio');
  if (relList.length > 0 && irrelList.length > 0){
    rocchioButton.classList.add("filter-button");
  } else{
    rocchioButton.classList.remove("filter-button");
  }
}

// Changes the color of the thumb if it is clicked
function changeColor(type, index){
  var indexListIrrel = irrelList.indexOf(index);
  var indexListRel = relList.indexOf(index);

  var upButton = document.getElementById('thumbs-up-' + index);
  var downButton = document.getElementById('thumbs-down-' + index);
  if (type == 'up'){
    if (indexListRel == -1){
      upButton.style.color = '#6d6d6d';
    }
    else {
      upButton.style.color = '#5555FF';
      downButton.style.color = '#6d6d6d';
    }
  }
  else if (type =='down'){
    if (indexListIrrel == -1){
      downButton.style.color = '#6d6d6d';
    }
    else {
      downButton.style.color = '#5555FF';
      upButton.style.color = '#6d6d6d';
    }
  }
}

// Displays the results of the search
function displayResults(data) {
  // Clear previous search results
  document.getElementById('results').innerHTML = '';
  // Display each result
  console.log("This is a message!");
  // Displays message if there are no results
  if (data.length === 0) {
    // Display a message indicating no results found
    document.getElementById('results').innerHTML = '<p>No articles found. Please input another query or adjust filter settings.</p>';
    display_finish();
    return;
  }
  // Creates every result
  data.forEach(function (result, index) {
    var resultDiv = document.createElement('div');
    resultDiv.className = 'result-item';

    var parts = result.split("@");
    var title = parts[0]; // publication title
    var linky = parts[1]; // publication link
    var abstract = parts[2]; // abstract
    //split abstract by ***, then take the first part, bold second part, add third part. 
    var abstractParts = abstract.split("***");
    var citations = parts[3]; // citations

    var titleElement = document.createElement('span');
    titleElement.className = 'result-title';
    titleElement.textContent = title;
    titleElement.onclick = function () { window.open(linky, '_blank'); };
    titleElement.style.cursor = 'pointer';

    resultDiv.appendChild(titleElement); // Append the title element

    var abstractElement = document.createElement('p');
    abstractElement.innerHTML = abstractParts[0] + "<span class='highlight'>" + abstractParts[1] + "</span>" + abstractParts[2];
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
}

// Attach the search function to the window object so it's available globally
window.search = search;

// Slider logic
var slider = document.getElementById("year");
var sliderValue = document.getElementById("sliderValue");
slider.addEventListener("input", function() {
  sliderValue.value = slider.value;
});
sliderValue.addEventListener("input", function() {
  slider.value = sliderValue.value;
});
