while IFS= read -r line
do
    node index.js -r 737173 -u https://$line -o output --nowarn >> noscript.log
done < "$1"