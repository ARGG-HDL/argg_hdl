 #!/bin/bash 
 date=$(stat -c %y "$1")
 
 while sleep 1; do date2=$(stat -c %y "$1")
   if [[ $date2 != $date ]]; then 
        echo "changed!"; 
        python $1
        date=$(stat -c %y "$1")
   fi
   # possibly exit [status] instead of break
   # or if you want to watch for another change, date=$date2
 done