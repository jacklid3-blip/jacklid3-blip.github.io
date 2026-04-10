const displayedImage = document.querySelector(".displayed-img"); // Main displayed image
const thumbBar = document.querySelector(".thumb-bar");           // Thumbnail container

const btn = document.querySelector("button");     // Darken/Lighten button
const overlay = document.querySelector(".overlay"); // Dark overlay element

// Array of image objects with filename and alt text
const images = [
  { filename: "pic1.jpg", alt: "Closeup of a human eye" },
  { filename: "pic2.jpg", alt: "Rock that looks like a wave" },
  { filename: "pic3.jpg", alt: "Purple and white pansies" },
  { filename: "pic4.jpg", alt: "Section of wall from a pharaoh's tomb" },
  { filename: "pic5.jpg", alt: "Large moth on a leaf" }
];

// Base URL for all images
const baseURL = "https://mdn.github.io/shared-assets/images/examples/learn/gallery/";

// Loop through images and add thumbnails to the thumb bar
for (const image of images) {
  const newImage = document.createElement("img");       // Create new img element
  newImage.src = baseURL + image.filename;              // Set src to base URL + filename
  newImage.alt = image.alt;                             // Set alt text
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