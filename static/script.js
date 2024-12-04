let motDuJour = ""; // Stocke le mot du jour
let essaisRestants = 6; // Limite des essais

// Charger le mot du jour et les informations du mot précédent
window.addEventListener("DOMContentLoaded", async () => {
    try {
        const response = await fetch("https://motdle-app.azurewebsites.net/api/mot");
        const data = await response.json();

        // Stocker le mot du jour
        motDuJour = data.mot.toLowerCase();
        console.log(`Mot du jour (debug) : ${motDuJour}`); // Pour débogage

        // Mettre à jour le message avec le nombre d'utilisateurs ayant trouvé le mot du jour
        const usersFoundToday = data.users_found_today;
        document.getElementById("motMessage").textContent = 
            `Trouvez le mot du jour ! Vous avez 6 essais. (${usersFoundToday} personnes ont déjà trouvé celui d'aujourd'hui).`;

        // Afficher le mot précédent et son nombre d'utilisateurs
        if (data.mot_precedent.word) {
            document.getElementById("motPrecedent").textContent = 
                `Le mot d'hier était "${data.mot_precedent.word}" (${data.mot_precedent.users_found} utilisateurs l'ont trouvé).`;
        } else {
            document.getElementById("motPrecedent").textContent = 
                "Aucun mot précédent disponible.";
        }
    } catch (error) {
        console.error("Erreur lors du chargement des données :", error);
    }
});

// Vérifier une proposition lorsque l'utilisateur clique sur "Soumettre"
document.getElementById("submitGuess").addEventListener("click", async () => {
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
        // Envoyer une requête pour incrémenter le compteur d'utilisateurs ayant trouvé le mot
        try {
            await fetch("https://motdle-app.azurewebsites.net/api/found", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ word: motDuJour })
            });
        } catch (error) {
            console.error("Erreur lors de la mise à jour des statistiques :", error);
        }
    } else if (essaisRestants === 0) {
        alert(`Dommage ! Le mot du jour était : ${motDuJour}`);
    }
});

// Afficher le résultat de la proposition
function afficherResultat(proposition) {
    const ligne = document.createElement("div");
    ligne.className = "tentative";

    const lettresRestantes = motDuJour.split("");

    // Vérifier les lettres bien placées (vert)
    const resultat = Array(proposition.length).fill("incorrect");
    for (let i = 0; i < proposition.length; i++) {
        if (proposition[i] === motDuJour[i]) {
            resultat[i] = "correct";
            lettresRestantes[i] = null; // Marquer cette lettre comme utilisée
        }
    }

    // Vérifier les lettres mal placées (jaune)
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