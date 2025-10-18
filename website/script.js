document.querySelectorAll("#nav-navigation a").forEach(link => {
    link.addEventListener("click", function () {
        // Rimuove active da tutti
        document.querySelectorAll("#nav-navigation a").forEach(l => l.classList.remove("active"));
        // Aggiunge active a questo
        this.classList.add("active");
    });
});