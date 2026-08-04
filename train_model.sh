#!/bin/bash
#
# Melatih model Naive Bayes lewat endpoint POST /predictions/train.
# Jalankan server dulu: ./run.sh --dev
#
# Cara pakai: ./train_model.sh
#
set -e

# ---------- Pengaturan (ubah di sini kalau perlu) ----------
BASE_URL="http://127.0.0.1:8000"
USERNAME="demoadmin"
PASSWORD="password123"
TEST_SIZE=0.2                       # 20% data untuk testing, 80% untuk training
NOTES="Manual training via train_model.sh"

# ---------- 1. Login untuk mendapatkan access token ----------
echo "🔐 Login as '$USERNAME'..."
TOKEN=$(curl -sS -X POST "$BASE_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}" \
    | jq -r '.access_token')

# Token kosong / null berarti login gagal atau server belum jalan
if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    echo "❌ Login failed. Is the server running? (./run.sh --dev)"
    exit 1
fi

# ---------- 2. Panggil endpoint training ----------
echo "🚀 Training..."
RESULT=$(curl -sS -X POST "$BASE_URL/predictions/train" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "{\"test_size\": $TEST_SIZE, \"notes\": \"$NOTES\"}")

# Kalau tidak ada field accuracy, berarti response-nya error
if [ "$(echo "$RESULT" | jq -r '.accuracy // "null"')" = "null" ]; then
    echo "❌ Training failed:"
    echo "$RESULT" | jq -r '.detail // .'
    echo "   Not enough damage records"
    exit 1
fi

# ---------- 3. Tampilkan hasil evaluasi ----------
echo
echo "✅ Training completed."

# Ambil 6 nilai sekaligus dari JSON, metrik dikali 100 supaya jadi persen
read -r train_n test_n acc prec rec f1 < <(echo "$RESULT" | jq -r '
    [ .training_samples, .test_samples,
      (.accuracy * 100), (.precision * 100), (.recall * 100), (.f1_score * 100) ]
    | join(" ")')

printf "  Train samples : %s\n"     "$train_n"
printf "  Test samples  : %s\n"     "$test_n"
printf "  Accuracy      : %.2f%%\n" "$acc"
printf "  Precision     : %.2f%%\n" "$prec"
printf "  Recall        : %.2f%%\n" "$rec"
printf "  F1 score      : %.2f%%\n" "$f1"

# Metrik per kelas: satu baris untuk tiap kelas kerusakan
echo
echo "Per-class metrics:"
printf "  %-10s%10s%10s%10s%10s\n" "class" "precision" "recall" "f1" "support"
echo "$RESULT" | jq -r '
    .classification_report
    | to_entries[]
    | [.key, (.value.precision * 100), (.value.recall * 100), (.value["f1-score"] * 100), .value.support]
    | @tsv
' | while IFS=$'\t' read -r cls prec rec f1 sup; do
    printf "  %-10s%9.2f%%%9.2f%%%9.2f%%%10s\n" "$cls" "$prec" "$rec" "$f1" "$sup"
done

# Confusion matrix: matriks 3x3, urutan kelasnya ringan, sedang, berat
echo
echo "Confusion matrix (row = actual, column = predicted):"
printf "  %-10s%8s%8s%8s\n" "" "ringan" "sedang" "berat"
classes=(ringan sedang berat)
row=0
while IFS=$'\t' read -r a b c; do
    printf "  %-10s%8s%8s%8s\n" "${classes[$row]}" "$a" "$b" "$c"
    row=$((row + 1))
done < <(echo "$RESULT" | jq -r '.confusion_matrix[] | @tsv')

echo
echo "💾 Model saved."
