import sys

# Importerer config
from config import *

errors=0

if not BRUKERNAVN:
    print("BRUKERNAVN er ikke satt.")
    errors+=1
elif BRUKERNAVN == "Studentnummeret ditt":
    print("BRUKERNAVN er ikke endret fra default verdi")
    errors+=1

if not PASSORD:
    print("PASSORD er ikke satt.")
    errors+=1
elif PASSORD == "Passordet ditt":
    print("PASSORD er ikke endret fra default verdi.")
    errors+=1

if not ROM:
    print("ROM er ikke satt.")
    errors+=1

if not UKEDAG:
    print("UKEDAG er ikke satt.")
    errors+=1
elif UKEDAG<0 or UKEDAG>6:
    print("UKEDAG har ugyldig verdi.")
    errors+=1

if not STARTTID:
    print("STARTTID er ikke satt.")
    errors+=1
elif len(STARTTID)!=5 or STARTTID[2]!=":" or not STARTTID.replace(":","").isnumeric():
    print("STARTTID har feil format.")
    errors+=1
elif int(STARTTID.replace(":","")) < 800 or int(STARTTID.replace(":","")) > 2030:
    print("Ugyldig klokkeslett for STARTTID")
    errors+=1

if not SLUTTID:
    print("SLUTTID er ikke satt.")
    errors+=1
elif len(SLUTTID)!=5 or SLUTTID[2]!=":" or not SLUTTID.replace(":","").isnumeric():
    print("SLUTTID har feil format.")
    errors+=1
elif int(SLUTTID.replace(":","")) < 830 or int(SLUTTID.replace(":","")) > 2100:
    print("Ugyldig klokkeslett for SLUTTID")
    errors+=1

if errors:
    print(f"\nERROR! {errors} feil oppdaget! Vennligst sjekk config.py")
    sys.exit(1)
else:
    print("Alt ser bra ut")

