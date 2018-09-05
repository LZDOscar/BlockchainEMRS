#!/bin/sh

nohup factomd -network=LOCAL > ./factomd.log 2>1 &
nohup factom-walletd > ./factom_wallet.log 2>1 &
