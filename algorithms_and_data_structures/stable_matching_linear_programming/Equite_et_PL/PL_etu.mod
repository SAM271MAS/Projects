set E;  # Ensemble des étudiants
set P;  # Ensemble des programmes

var x{e in E, p in P}, binary;  # 1 si l'étudiant e est assigné au programme p

param rank{e in E, p in P};  # Classement du programme p pour l'étudiant e (1 = meilleur, 9 = dernier)
param Cap{p in P};           # Capacité du programme p

maximize total_score: sum{e in E, p in P} (9 - rank[e,p]) * x[e,p];  # Maximisation du score total en utilisant Borda

subject to c1{e in E}: sum{p in P} x[e,p] = 1;  # Chaque étudiant doit être affecté à un seul programme
subject to c2{p in P}: sum{e in E} x[e,p] <= Cap[p];  # La capacité d'un programme ne doit pas être dépassée
subject to c3{e in E}: sum{p in P: rank[e,p] <= 5} x[e,p] = 1;  # Chaque étudiant doit choisir un programme parmi les k=5 premiers options

solve;  # Résolution du modèle
display x;  # Affichage de la solution d'affectation des étudiants aux programmes
display total_score;  # Affichage du score total obtenu
end;

