let motDuJour = ""; // Stocke le mot du jour
let essaisRestants = 6; // Limite des essais

// Charger le mot du jour automatiquement au chargement de la page
window.addEventListener("DOMContentLoaded", async () => {
    const response = await fetch("https://motdle-app.azurewebsites.net/api/mot");
    const data = await response.json();
    motDuJour = data.mot.toLowerCase();
    console.log(`Mot du jour (debug) : ${motDuJour}`); // Pour débogage
});

// Vérifier une proposition lorsque l'utilisateur clique sur "Soumettre"
document.getElementById("submitGuess").addEventListener("click", () => {
    const userGuess = document.getElementById("guess").value.toLowerCase().trim();

    if (userGuess.length !== motDuJour.length) {
        alert(`Veuillez entrer un mot de ${motDuJour.length} lettres.`);
        return;
    }

    if (essaisRestants <= 0) {
        alert("Vous n'avez plus d'essais !");
        return;
    }

    afficherResultat(userGuess);
    document.getElementById("guess").value = ""; // Réinitialiser le champ
    essaisRestants--;

    if (userGuess === motDuJour) {
        alert("Félicitations ! Vous avez trouvé le mot !");
    } else if (essaisRestants === 0) {
        alert(`Dommage ! Le mot du jour était : ${motDuJour}`);
    }
});

// Afficher le résultat de la proposition
function afficherResultat(proposition) {
    const ligne = document.createElement("div");
    ligne.className = "tentative";

    // Créer une copie mutable des lettres disponibles dans le mot du jour
    const lettresRestantes = motDuJour.split("");

    // Première passe : Vérifier les lettres bien placées (vert)
    const resultat = Array(proposition.length).fill("incorrect");
    for (let i = 0; i < proposition.length; i++) {
        if (proposition[i] === motDuJour[i]) {
            resultat[i] = "correct";
            lettresRestantes[i] = null; // Marquer cette lettre comme utilisée
        }
    }

    // Deuxième passe : Vérifier les lettres mal placées (jaune)
    for (let i = 0; i < proposition.length; i++) {
        if (resultat[i] === "incorrect" && lettresRestantes.includes(proposition[i])) {
            resultat[i] = "misplaced";
            lettresRestantes[lettresRestantes.indexOf(proposition[i])] = null; // Marquer cette lettre comme utilisée
        }
    }

    // Afficher les résultats
    for (let i = 0; i < proposition.length; i++) {
        const lettre = document.createElement("span");
        lettre.textContent = proposition[i];
        lettre.className = resultat[i];
        ligne.appendChild(lettre);
    }

    document.getElementById("tentatives").appendChild(ligne);
}