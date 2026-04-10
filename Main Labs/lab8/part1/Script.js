// Complete variable definitions and random functions

const customName = document.getElementById("custom-name"); // Input field for custom name
const generateBtn = document.querySelector(".generate");    // Generate button
const story = document.querySelector(".story");             // Output paragraph

function randomValueFromArray(array) {
  const random = Math.floor(Math.random() * array.length); // Get random index
  return array[random]; // Return random element
}

// Story text with placeholders
const storyText = "It was 94 Fahrenheit outside, so :insertx: went for a walk. When they got to :inserty:, they stared in horror for a few moments, then :insertz:. Bob saw the whole thing, but was not surprised — :insertx: weighs 300 pounds, and it was a hot day.";

// Arrays of random story elements
const insertX = ["Willy the Goblin", "Big Daddy", "Father Christmas"];
const insertY = ["the soup kitchen", "Disneyland", "the White House"];
const insertZ = ["spontaneously combusted", "melted into a puddle on the sidewalk", "turned into a slug and slithered away"];

// Event listener and result function definition

generateBtn.addEventListener("click", result); // Call result when clicked

function result() {
  // Create a new story from the template
  let newStory = storyText;

  // Get random elements from each array
  const xItem = randomValueFromArray(insertX);
  const yItem = randomValueFromArray(insertY);
  const zItem = randomValueFromArray(insertZ);

  // Replace placeholders with random items
  newStory = newStory.replaceAll(":insertx:", xItem);
  newStory = newStory.replaceAll(":inserty:", yItem);
  newStory = newStory.replaceAll(":insertz:", zItem);

  // Replace "Bob" with custom name if provided
  if (customName.value !== "") {
    const name = customName.value;
    newStory = newStory.replace("Bob", name);
  }

  // Convert to UK units if UK locale selected
  if (document.getElementById("uk").checked) {
    const weight = Math.round(300 / 14) + " stone";         // Convert pounds to stone
    const temperature = Math.round((94 - 32) * 5 / 9) + " centigrade"; // Convert Fahrenheit to centigrade
    newStory = newStory.replace("300 pounds", weight);
    newStory = newStory.replace("94 Fahrenheit", temperature);
  }

  // Display the story
  story.textContent = newStory;
  story.style.visibility = "visible";
}