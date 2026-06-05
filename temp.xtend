\nodeshadowed [at={(-5,8 )},yslant=0.05]
{\Huge Ti\textcolor{orange}{\emph{k}}Z};
\nodeshadowed [at={( 0,8.3)}]
{\huge \textcolor{green!50!black!50}{\&}};
\nodeshadowed [at={( 5,8 )},yslant=-0.05]
{\Huge \textsc{PGF}};
\nodeshadowed [at={( 0,5 )}]
{Manual for Version \pgftypesetversion};
\foreach \where in {-9cm,9cm} {
\nodeshadowed [at={(\where,5cm)}] { \tikz
\draw [green!20!black, rotate=90,
l-system={rule set={F -> FF-[-F+F]+[+F-F]},
axiom=F, order=4,step=2pt,
randomize step percent=50, angle=30,
randomize angle percent=5}] l-system; }}
\foreach \i in {0.5,0.6,...,2}
\fill
[white,opacity=\i/2,
decoration=Koch snowflake,
shift=(horizon),shift={(rand*11,rnd*7)},
scale=\i,double copy shadow={
opacity=0.2,shadow xshift=0pt,
shadow yshift=3*\i pt,fill=white,draw=none}]
decorate {
decorate {
decorate {
(0,0)- ++(60:1) -- ++(-60:1) -- cycle
} } };
\node (left text) ...
\node (right text) ...
\fill [decorate,decoration={footprints,foot of=gnome},
opacity=.5,brown] (rand*8,-rnd*10)
to [out=rand*180,in=rand*180] (rand*8,-rnd*10);
\end{tikzpicture}

