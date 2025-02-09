// Toggle Light and Dark Mode
function toggleDarkMode() {
    const body = document.body;
    const moonIcon = document.getElementById("moon-icon");
    const sunIcon = document.getElementById("sun-icon");

    // Toggle dark mode class on the body
    body.classList.toggle("dark-mode");

    // Check if dark mode is enabled
    const isDarkMode = body.classList.contains("dark-mode");

    // Toggle icons
    if (isDarkMode) {
        moonIcon.style.display = "none"; // Hide moon icon
        sunIcon.style.display = "inline"; // Show sun icon
    } else {
        sunIcon.style.display = "none"; // Hide sun icon
        moonIcon.style.display = "inline"; // Show moon icon
    }

    // Save user preference in localStorage
    localStorage.setItem("darkMode", isDarkMode);
}

// Check for saved user preference on page load
document.addEventListener("DOMContentLoaded", () => {
    const savedDarkMode = localStorage.getItem("darkMode") === "true";
    const body = document.body;
    const moonIcon = document.getElementById("moon-icon");
    const sunIcon = document.getElementById("sun-icon");

    if (savedDarkMode) {
        body.classList.add("dark-mode");
        moonIcon.style.display = "none"; // Hide moon icon
        sunIcon.style.display = "inline"; // Show sun icon
    } else {
        body.classList.remove("dark-mode");
        moonIcon.style.display = "inline"; // Show moon icon
        sunIcon.style.display = "none"; // Hide sun icon
    }
});

function toggleUserMenu() {
    let dropdown = document.getElementById("userDropdown");
    dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
}

document.addEventListener("click", function(event) {
    let userMenu = document.getElementById("userDropdown");
    let userIcon = document.querySelector(".user-icon");
    
    if (!userMenu.contains(event.target) && !userIcon.contains(event.target)) {
        userMenu.style.display = "none";
    }
});
