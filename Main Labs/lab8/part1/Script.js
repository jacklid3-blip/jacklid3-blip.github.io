// Complete variable definitions and random functions

const customName = document.getElementById("custom-name"); // Input field for custom name
const generateBtn = document.querySelector(".generate");    // Generate button
const story = document.querySelector(".story");             // Output paragraph

function randomValueFromArray(array) {
  const random = Math.floor(Math.random() * array.length); // Get random index
  return array[random]; // Return random element
}

// Arrays of random story elements
const characters = ["Willy the Goblin", "Big Daddy", "Father Christmas"];
const places = ["the soup kitchen", "Disneyland", "the White House"];
const events = ["spontaneously combusted", "melted into a puddle on the sidewalk", "turned into a slug and slithered away"];

// Partial return random string function

function returnRandomStoryString() {
  // Get random elements from each array
  const randomCharacter = randomValueFromArray(characters);
  const randomPlace = randomValueFromArray(places);
  const randomEvent = randomValueFromArray(events);

  // Build story with placeholders replaced
  let storyText = `It was 94 Fahrenheit outside, so ${randomCharacter} went for a walk. When they got to ${randomPlace}, they stared in horror for a few moments, then ${randomEvent}. Bob saw the whole thing, but was not surprised — ${randomCharacter} weighs 300 pounds, and it was a hot day.`;

  return storyText;
}

// Event listener and partial generate function definition

generateBtn.addEventListener("click", generateStory); // Call generateStory when clicked

function generateStory() {
  // Create a new random story
  let newStory = returnRandomStoryString();

  // Replace "Bob" with custom name if provided
  if (customName.value !== "") {
    const name = customName.value;
    newStory = newStory.replace("Bob", name);
  }

  // Convert to UK units if UK locale selected
  if (document.getElementById("uk").checked) {
    const weight = Math.round(300 / 14) + " stone";         // Convert pounds to stone
    const temperature = Math.round((94 - 32) * 5 / 9) + " Celsius"; // Convert Fahrenheit to Celsius
    newStory = newStory.replace("300 pounds", weight);
    newStory = newStory.replace("94 Fahrenheit", temperature);
  }

  // Display the story
  story.textContent = newStory;
  story.style.visibility = "visible";
}