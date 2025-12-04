#!/bin/bash

# --------------------------
# File: run_rag_tests.sh
# Usage: bash run_rag_tests.sh
# --------------------------

# List of 10 test questions
questions=(
  "What is FTTH?"
  "How much does FTTH cost?"
  "Can I upgrade or downgrade my subscription package?"
  "What are the operating hours of the co-working space?"
  "What amenities come with the Executive Office?"
  "How do I register for the Pearson VUE exam?"
  "Can I pay for the exam later?"
  "How do I register for the training program?"
  "How will I know if my payment is confirmed?"
  "When will I receive my renewal notification?"
)

output_file="rag_output.txt"

# Clear previous output
> "$output_file"

# Loop through each question
for q in "${questions[@]}"; do
  echo "---------------------------" >> "$output_file"
  echo "Q: $q" >> "$output_file"

  # Call the FastAPI /ask endpoint
  answer=$(curl -s -X POST http://127.0.0.1:8000/ask \
            -H "Content-Type: application/json" \
            -d "{\"query\": \"$q\"}" | jq -r '.answer')

  # Format answer: add <think> section if needed
  echo -e "A:\n<think>\n$answer\n</think>\n" >> "$output_file"
done

echo "✅ RAG test completed. Results saved in $output_file"
