# Run hazard raster to vector conversions in parallel for various thresholds

# 0.25 0.5 0.75 1 1.25 1.5 1.75 2 2.25 2.5
seq 0.25 0.25 2.5 | parallel convert_hazard_to_vector.sh {}
# 3 3.5 4 4.5 5
seq 3 0.5 5 | parallel convert_hazard_to_vector.sh {}
# 6 7 8 9 10
seq 6 1 10 | parallel convert_hazard_to_vector.sh {}
