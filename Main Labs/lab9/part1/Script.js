const displayedImage = document.querySelector(".displayed-img"); // Main displayed image
const thumbBar = document.querySelector(".thumb-bar");           // Thumbnail container

const btn = document.querySelector("button");     // Darken/Lighten button
const overlay = document.querySelector(".overlay"); // Dark overlay element

// Array of image filenames
const images = ["pic1.jpg", "pic2.jpg", "pic3.jpg", "pic4.jpg", "pic5.jpg"];

// Array of alt text for each image
const altText = [
  "Closeup of a human eye",
  "Rock that looks like a wave",
  "Purple and white pansies",
  "Section of wall from a pharaoh's tomb",
  "Large moth on a leaf"
];

// Base URL for all images
const baseURL = "https://mdn.github.io/shared-assets/images/examples/learn/gallery/";

// Loop through images starting at 1 (matching pic1.jpg, pic2.jpg, etc.)
for (let i = 1; i <= 5; i++) {
  const newImage = document.createElement("img");       // Create new img element
  newImage.src = baseURL + "pic" + i + ".jpg";          // Set src using loop number
  newImage.alt = altText[i - 1];                        // Set alt text (array index is i-1)
  newImage.setAttribute("tabindex", "0");               // Make focusable via keyboard
  thumbBar.appendChild(newImage);                       // Add to thumbnail bar

  // Click event to display clicked thumbnail as main image
  newImage.addEventListener("click", updateDisplayedImage);

  // Keydown event for Enter key (accessibility)
  newImage.addEventListener("keydown", function(e) {
    if (e.key === "Enter") {
      updateDisplayedImage(e);
    }
  });
}

// Function to update the displayed image when thumbnail is clicked
function updateDisplayedImage(e) {
  displayedImage.src = e.target.src;   // Set main image src to clicked thumbnail src
  displayedImage.alt = e.target.alt;   // Set main image alt to clicked thumbnail alt
}

// Darken/Lighten button click handler
btn.addEventListener("click", function() {
  const btnClass = btn.getAttribute("class");  // Get current button class
  if (btnClass === "dark") {
    btn.textContent = "Lighten";                      // Change button text
    overlay.style.backgroundColor = "rgb(0 0 0 / 0.5)"; // Add dark overlay
    btn.setAttribute("class", "light");               // Change class to light
  } else {
    btn.textContent = "Darken";                       // Change button text
    overlay.style.backgroundColor = "rgb(0 0 0 / 0)"; // Remove dark overlay
    btn.setAttribute("class", "dark");                // Change class to dark
  }
});