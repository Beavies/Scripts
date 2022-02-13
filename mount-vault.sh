#!/bin/bash
#####################################
# mount vaults
#
# in VAULTDIR 1 directory per encrypted folder
# in MOUNTPOINT is where the vault will be mounted under a name with the same name
###################################
VAULTDIR=/home/dso/Documentos/VAULT
MOUNTPOINT=/home/dso/Documentos

declare -A VAULTS

isMounted() {
    local m="$1"
    mount | grep $m | grep gocrypt > /dev/null
}

detectVaults() {
    local num=1
    unset VAULTS

    echo -e "Vaults detectadas:"
    echo
    cd "$VAULTDIR"

    for v in *; do
        if [[ -d $v ]]; then
            VAULTS[$num]="${v}"

            if isMounted $v; then
                echo -e "${num}. $v (Montado)"
            else
                echo -e "${num}. $v"
            fi
            ((num++))
        fi
    done

    echo -e "0. Quit"
    echo
}

mountVault() {
    local v="$1"
    local workfolder="${MOUNTPOINT}/$v"

    if isMounted "$v"; then
        echo -e "\t- $v montada.... desmontando"
        echo
        fusermount -u "${workfolder}"
    else
        if [[ ! -d "$workfolder" ]]; then
            echo -e "\t- $workfolder no existe... creando"
            mkdir -p "$workfolder"
        fi
        echo -e "\t- Montando vault $v en ${workfolder}"
        gocryptfs "${VAULTDIR}/$v" "$workfolder"
        read -p "Pulsa tecla para continuar..."
    fi
}

while true; do
    detectVaults

    read -p "Opcion: " opt

    case $opt in
        "0") echo "saliendo..."; break ;;
    esac

    if [[ -n ${VAULTS[$opt]} ]]; then
        echo
        mountVault ${VAULTS[$opt]}
    fi
done
