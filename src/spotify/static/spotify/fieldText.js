const searchTypeDropdown = document.getElementById("search_type_dropdown");
const searchInput = document.getElementById("search_input");

const placeholderTexts = {
  track: "Search for a song...",
  album: "Search for an album...",
  playlist: "Search for a playlist...",
  link: "Paste a Spotify link...",
};

searchTypeDropdown.addEventListener("change", function () {
  const selectedType = this.value;
  searchInput.placeholder = placeholderTexts[selectedType];
});

document.addEventListener("DOMContentLoaded", function () {
  const initialType = searchTypeDropdown.value;
  searchInput.placeholder = placeholderTexts[initialType];
});
