# This file plots the datas in file datas.dat
# To create the .eps file simply execute :
# gnuplot datas.p

set xlabel "Configurations"
set ylabel "Secondes"
set xtics ("Configuration 1" 1, "Configuration 2" 2, "Configuration 3" 3, "Configuration 4" 4, "Configuration 5" 5)
set data style linespoints
set terminal postscript eps color


set title "Python"
set output "datas1.eps"
plot "datas.dat" using 1:2 title "DMS", "datas.dat" using 1:3 title "TeamBuilder"

set title "Perl"
set output "datas2.eps"
plot "datas.dat" using 1:4 title "DMS", "datas.dat" using 1:5 title "TeamBuilder"

set title "Samba"
set output "datas3.eps"
plot "datas.dat" using 1:6 title "DMS", "datas.dat" using 1:7 title "TeamBuilder"
