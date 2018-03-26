# Filter out intersections with a max flood_depth of 999
cat data/tanzania_flood/hazard_network_intersections.csv \
    | grep '\,999' \
    | cut -f 2,3,4,5 -d ',' \
    | sort | uniq \
    > intersect_999.csv
