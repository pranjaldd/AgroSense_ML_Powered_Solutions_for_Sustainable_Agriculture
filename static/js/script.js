document.addEventListener("DOMContentLoaded", () => {
    // Show welcome alert once page is loaded
    alert("Welcome to the Impact Page!");

    // Add click events to all feature cards
    const featureCards = document.querySelectorAll('.feature-card');

    featureCards.forEach(card => {
        card.addEventListener('click', () => {
            const feature = card.dataset.feature;
            console.log(`Clicked on: ${feature}`);
            // Optional: Show a nicer toast or alert
            alert(`You clicked on: ${feature}`);
        });

        // Optional: Hover animation effect
        card.addEventListener('mouseenter', () => {
            card.style.transform = "scale(1.05)";
            card.style.boxShadow = "0 4px 15px rgba(0, 128, 0, 0.2)";
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = "scale(1)";
            card.style.boxShadow = "none";
        });
    });
});
