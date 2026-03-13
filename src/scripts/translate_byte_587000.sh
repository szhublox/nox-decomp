#!/bin/sh

GAMEFILES="${HOME}"/.config/nox/
BINARY="${HOME}"/src/nox-decomp/src/src/out

cd "$(dirname $0)/.."
tmpdir="$(mktemp -d)"
grep -ho '(const char \*)&byte_587000\[[0-9]\+\]' *.c > "${tmpdir}"/references
sed -i -e 's/^/print /' "${tmpdir}"/references
echo -e "b compat_fopen\nr" > "${tmpdir}"/gdbstart
cat "${tmpdir}"/gdbstart "${tmpdir}"/references > "${tmpdir}"/gdbscript

(cd "${GAMEFILES}" && gdb --batch -x "${tmpdir}"/gdbscript "${BINARY}") > "${tmpdir}"/gdboutput
grep -o '^\$[0-9].*$' "${tmpdir}"/gdboutput > "${tmpdir}"/gdbtruncated
sed -i -e 's/^[^+]\++\([0-9]\+\)> \(.\+\)$/\1 \2/' "${tmpdir}"/gdbtruncated

for i in $(seq 1 $(wc -l "${tmpdir}"/gdbtruncated | cut -f1 -d' ')); do
    line=$(tail -n $i "${tmpdir}"/gdbtruncated | head -n1)
    part1=$(echo $line | cut -f1 -d' ')
    part2=$(echo $line | cut -f2- -d' ' | sed 's/\\/\\\\/g' | sed 's/\//\\\//g')
    echo "sed -i -e s/(const char \*)&byte_587000\[${part1}\]/${part2}/"
    sed -i -e "s/(const char \*)&byte_587000\[${part1}\]/${part2}/" *.c
done

cd "${tmpdir}"
rm references gdbstart gdbscript gdboutput gdbtruncated
rmdir "${tmpdir}"
