#!/bin/bash

mkdir -p logs

LOG="logs/processamento.log"
ERR="logs/processamento.err"

echo "========================================================" > "$LOG"
echo "Início: $(date)" >> "$LOG"
echo "========================================================" >> "$LOG"

echo "" > "$ERR"

while IFS= read -r favela
do
    echo "" | tee -a "$LOG"
    echo "========================================================" | tee -a "$LOG"
    echo "PID $$ | $(date) | $favela" | tee -a "$LOG"
    echo "========================================================" | tee -a "$LOG"

    python processa_favelas.py "$favela" \
        >> "$LOG" \
        2>> "$ERR"

    STATUS=$?

    if [ $STATUS -eq 0 ]; then
        echo "✓ Concluída: $favela" | tee -a "$LOG"
    else
        echo "✗ Erro: $favela (exit code $STATUS)" | tee -a "$LOG"
    fi

done < logs/favelas_pendentes.txt

echo "" >> "$LOG"
echo "========================================================" >> "$LOG"
echo "Fim: $(date)" >> "$LOG"
echo "========================================================" >> "$LOG"