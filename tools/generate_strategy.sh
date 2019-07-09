#!/usr/bin/env bash

FILE="$1"

# rm "$FILE"_strategy.aut
# rm "$FILE"_counter.aut
# rm "$FILE"_strategy.pdf
# rm "$FILE"_counter.pdf

python ${SLUGS_DIR}/tools/StructuredSlugsParser/compiler.py "$FILE".structuredslugs > "$FILE".slugsin

${SLUGS_DIR}/src/slugs --explicitStrategy "$FILE".slugsin > "$FILE"_strategy.aut
${SLUGS_DIR}/src/slugs --counterStrategy "$FILE".slugsin > "$FILE"_counter.aut

# python /home/adam/repos/rcla/synthesis/src/aut_tools.py -a "$FILE"_strategy.aut -g "$FILE"_strategy.gv -s "$FILE".structuredslugs
# python /home/adam/repos/rcla/synthesis/src/aut_tools.py -a "$FILE"_counter.aut -g "$FILE"_counter.gv -s "$FILE".structuredslugs
#
# dot -Tpdf "$FILE"_strategy.gv -o "$FILE"_strategy.pdf
# dot -Tpdf "$FILE"_counter.gv -o "$FILE"_counter.pdf
