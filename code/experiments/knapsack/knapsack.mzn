int: n=5; % number of objects
set of int: OBJ = 1..n;
int: capacity=200000;
array[OBJ] of int: profit=[1300,1000,520,480,325];
array[OBJ] of int: size=[90,72,43,40,33];

array[OBJ] of var int: x; % how many of each object

constraint forall(i in OBJ)(x[i] >= 0);
constraint sum(i in OBJ)(size[i] * x[i]) <= capacity;
%solve maximize sum(i in OBJ)(profit[i] * x[i]);
solve satisfy;
