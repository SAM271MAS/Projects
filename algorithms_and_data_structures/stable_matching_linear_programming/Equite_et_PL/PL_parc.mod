set P;  # Ensemble des collèges
set E;  # Ensemble des étudiants

param rank{P, E};  # Classement de l'étudiant e
param Cap{P};      # Capacité de chaque parcours

var x{p in P, e in E}, binary;  # 1 si le parcours p admet l'étudiant e

maximize total_score: sum{p in P, e in E} (11 - rank[p,e]) * x[p,e];  # Maximisation du score total

subject to student_assignment{e in E}:  
    sum{p in P} x[p,e] = 1;  # Chaque étudiant doit être affecté à un seul parcours

subject to capacity_constraint{p in P}:  
    sum{e in E} x[p,e] <= Cap[p];  # La capacité d'un parcours ne doit pas être dépassée

subject to top8_constraint{p in P, e in E: rank[p,e] > 8}:
    x[p,e] = 0;  # Un étudiant avec un classement supérieur à k=8 ne peut pas être affecté à ce parcours

solve;  # Résolution du modèle
display x;  # Affichage de la solution
display total_score;  # Affichage du score total obtenu
end;

