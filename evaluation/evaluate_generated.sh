mkdir ./output
python code/check_generated_parallel.py --input data/RQ1-2_CodeLlama-13B.json --output output/evaluate_result.json
python code/calculate_ca.py --input output/evaluate_result.json --output output/ca_result.json
diff output/ca_result.json data/RQ1-2_CodeLlama-13B_ca-result.json
ret=$?

if [[ $ret -eq 0 ]]; then
    echo "Get the same result."
else
    echo "Get different results."
fi