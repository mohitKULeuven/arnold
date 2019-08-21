int: W=4; % number of Warehousse
set of int: WARE = 1..W;
int: F=3; % number of Factories
set of int: FACT = 1..F;

array[WARE] of int: demand=[30,20,35,20];
array[FACT] of int: production=[40,40,25];

array[FACT,WARE] of var int: ship;

%int: m = max(demand);
%array[FACT,WARE] of var 0..m: ship;
constraint forall(f in FACT, w in WARE)(ship[f,w] >= 0);

constraint forall(w in WARE)
                 (sum(f in FACT)(ship[f,w]) >= demand[w]);

constraint forall(f in FACT)
                 (sum(w in WARE)(ship[f,w]) <= production[f]);

solve satisfy;

