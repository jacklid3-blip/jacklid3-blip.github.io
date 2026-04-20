// =============================================
// Show/Hide Comments Toggle
// =============================================

// Grab the toggle button and the comment wrapper container
const showHideBtn = document.querySelector('.show-hide');
const commentWrapper = document.querySelector('.comment-wrapper');

// Hide the comments section by default on page load
commentWrapper.style.display = 'none';

// Toggle the comment wrapper visibility when the button is clicked
showHideBtn.onclick = function() {
  let showHideText = showHideBtn.textContent;
  if(showHideText === 'Show comments') {
    // Reveal comments and update button label
    showHideBtn.textContent = 'Hide comments';
    commentWrapper.style.display = 'block';
  } else {
    // Hide comments and reset button label
    showHideBtn.textContent = 'Show comments';
    commentWrapper.style.display = 'none';
  }
};

// =============================================
// Comment Form Submission
// =============================================

// Select the form and its input fields
const form = document.querySelector('.comment-form');
const nameField = document.querySelector('#name');
const commentField = document.querySelector('#comment');

// Select the unordered list where new comments will be appended
const list = document.querySelector('.comment-container');

// Intercept the form submit event and call submitComment instead of reloading the page
form.onsubmit = function(e) {
  e.preventDefault();
  submitComment();
};

// Builds a new comment list item from the form inputs and appends it to the comment list
function submitComment() {
  // Create DOM elements for the new comment entry
  const listItem = document.createElement('li');
  const namePara = document.createElement('p');
  const commentPara = document.createElement('p');

  // Read the current values from the input fields
  const nameValue = nameField.value;
  const commentValue = commentField.value;

  // Populate the paragraphs with the entered text
  namePara.textContent = nameValue;
  commentPara.textContent = commentValue;

  // Attach the name and comment paragraphs to the list item, then add it to the list
  list.appendChild(listItem);
  listItem.appendChild(namePara);
  listItem.appendChild(commentPara);

  // Clear the input fields after submission
  nameField.value = '';
  commentField.value = '';
}
