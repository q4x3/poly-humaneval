import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--input", type=str, default=None)
parser.add_argument("--output", type=str, default="./output_data/result.json")

args = parser.parse_args()
input_file = args.input
output_file = args.output

with open(input_file, "r") as f:
    expected_result = json.load(f)

ca_result = {}
for src_lang in expected_result:
    ca_result[src_lang] = {}
    for tgt_lang in expected_result[src_lang]:
        assert len(expected_result[src_lang][tgt_lang]) == 164
        pass_cnt = len([x for x in expected_result[src_lang][tgt_lang] if x])
        ca_result[src_lang][tgt_lang] = round((pass_cnt / 164) * 100, 2)

with open(output_file, "w") as f:
    json.dump(ca_result, f, indent=4)