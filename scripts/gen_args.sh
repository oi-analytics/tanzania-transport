# Generate args for convert_ssbn_bands.sh to run using GNU parallel
ssbn_return_periods=(5 10 20 50 75 100 200 250 500 1000)

declare -A ssbnmodels
ssbnmodels=(
    ["TZ_fluvial_defended"]="FD"
    ["TZ_fluvial_undefended"]="FU"
    ["TZ_pluvial_defended"]="PD"
    ["TZ_pluvial_undefended"]="PU"
    ["TZ_urban_defended"]="UD"
    ["TZ_urban_undefended"]="UU"
)

for model in ${!ssbnmodels[@]}
do
for rp in ${ssbn_return_periods[@]}
do
abbr=${ssbnmodels[${model}]}

for lower in $(seq 0.25 0.25 4.75)
do
    upper=$(bc <<< "$lower + 0.25")
    echo $lower $upper $model $abbr $rp
done

echo "5.00 1000 $model $abbr $rp"

done
done
