#!/bin/bash

OUTPUT_FILE="resultats.csv"

echo "Match,A_Main_Dead,A_Sec_Dead,B_Main_Dead,B_Sec_Dead" > "$OUTPUT_FILE"

javac -cp "jars/*" -s src/ -d beans/ src/supportGUI/*.java src/algorithms/*.java src/characteristics/*.java

TOTAL_MATCHES=16
MAX_JOBS=4

seq 1 "$TOTAL_MATCHES" | xargs -I {} -P "$MAX_JOBS" bash -c '
    echo "  -> Starting match {}..."
    timeout 120s xvfb-run -a bash -c "(sleep 3 && xdotool key space) & java -Dsun.java2d.opengl=false -cp \"jars/*:beans/\" supportGUI.Viewer" > logs_benchmark/match_{}.log 2>&1
'

echo "Matches complete! Analyzing logs..."

for i in $(seq 1 "$TOTAL_MATCHES"); do
    A_MAIN=$(cat logs_benchmark/match_$i.log 2>/dev/null | grep -c "STAT_TRACKER: A_MAIN DIED")
    A_SEC=$(cat logs_benchmark/match_$i.log 2>/dev/null | grep -c "STAT_TRACKER: A_SEC DIED")
    B_MAIN=$(cat logs_benchmark/match_$i.log 2>/dev/null | grep -c "STAT_TRACKER: B_MAIN DIED")
    B_SEC=$(cat logs_benchmark/match_$i.log 2>/dev/null | grep -c "STAT_TRACKER: B_SEC DIED")
    
    echo "$i,$A_MAIN,$A_SEC,$B_MAIN,$B_SEC" >> "$OUTPUT_FILE"
done

