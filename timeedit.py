#!/usr/bin/python
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from time import sleep
from datetime import datetime
import logging
import sys
from os import listdir, system
from os.path import realpath, dirname, isfile, join


logfile = open("/var/log/timeedit.log","a")
def log(message):
    print(message)
    logfile.write(message+"\n")

def run():
    global ROM

    # Sjekker om det er riktig dag å kjøre på
    # Dette bør endres til å heller holde styr på om det er gjort reservasjon allerede
    weekday = datetime.today().weekday()
    if weekday != UKEDAG:
        log(f"Reservasjon skal gjøres på ukedag {UKEDAG}, men i dag er det {weekday}")
        log("Hopper over denne configen")
        return

    tries = 0
    maxtries = 5
    while 1:
        try:
            # Åpne nettleser
            options = FirefoxOptions()
            options.add_argument("--headless")
            driver = webdriver.Firefox(options=options)


            # Logger inn på min usn
            driver.get("https://min.usn.no/")
            driver.find_element_by_id("feide_form").submit()
            sleep(5)
            driver.find_element_by_id("org_selector_filter").send_keys("Universit\n\n")
            sleep(1)
            driver.find_element_by_id("selectorg_button").submit()
            sleep(5)
            driver.find_element_by_id("username").send_keys(BRUKERNAVN)
            driver.find_element_by_id("password").send_keys(PASSORD)
            driver.find_element_by_name("f").submit()

            # Finner link til timeedit
            sleep(5)
            link_start=driver.page_source.find("https:\\/\\/cloud.timeedit")
            link = driver.page_source[link_start:link_start+100].split("&")[0].replace("\\","")


            # Åpner timeedit
            driver.get("https://cloud.timeedit.net/usn/web/rombooking/ri1Q5002.html")
            sleep(5)
            driver.find_element_by_partial_link_text("innlogging").click()


            # Søker etter romnummer
            sleep(5)
            driver.find_element_by_css_selector(".objectinput.objectinputtext").send_keys(ROM[0])

            # Går til neste uke
            sleep(5)
            driver.find_element_by_id("leftresdateinc").click()

            # Går til dag nummer X
            sleep(5)
            driver.execute_script(f"document.getElementsByClassName('slotfree2')[{UKEDAG}].click();")


            # Åpner reservasjonsdialogen
            sleep(5)
            driver.execute_script(f"document.getElementsByClassName('slotfree2')[{UKEDAG}].click();")

            # Setter starttid
            timeslotStart = Select(driver.find_element_by_class_name('timeslotStart'))
            timeslotStart.select_by_visible_text(STARTTID)

            # Setter sluttid
            timeslotEnd = Select(driver.find_element_by_class_name("timeslotEnd"))
            timeslotEnd.select_by_visible_text(SLUTTID)

            # Setter aktivitetstype til gruppearbeid
            driver.find_element_by_class_name("mandatory").click()
            driver.find_element_by_xpath("//div[contains(text(), 'Gruppearbeid')]").click()


            # Bestiller
            driver.find_element_by_id("continueRes2").click()


            # Sjekker om reservasjonen kunne gjennomføres
            errormessage = None
            try:
                errormessage = driver.find_element_by_xpath("//div[contains(text(),'Reservasjonen kunne ikke gjennomføres')]").text

            # Hvis ikke TimeEdit viser noen feilmelding er forhåpentligvis alt OK
            except NoSuchElementException:
                log("Suksess! Rommet er nå forhåpentligvis blitt booket.")

                if EPOST:
                    try:
                        # Åpne dialog for epostbekreftelse
                        sleep(5)
                        showsendmail = driver.find_element_by_id("showsendmail")
                        actions = ActionChains(driver)
                        actions.move_to_element(showsendmail)
                        actions.click()
                        actions.perform()

                        # Fyll inn epostadresse og send inn
                        sleep(5)
                        driver.find_element_by_id("sendmailaddresses").clear()

                        driver.find_element_by_id("sendmailaddresses").send_keys("\n".join(EPOST))
                        driver.find_element_by_id("sendmailbutton").click()

                    except:
                        log("Klarte ikke å registrere epostbekreftelse, men reservasjonen bør likevel være gjennomført")

                # Avslutt uten feilkode
                break

            # Hvis TimeEdit gir feilmelding ved registrering, prøv et annet rom eller avslutt
            else:
                log(errormessage)
                if "opptatt" in errormessage:
                    if BRUKERNAVN in errormessage:
                        log(f"Brukernavn {BRUKERNAVN} har allerede en annen bestilling på samme klokkeslett.")
                        return

                    elif len(ROM) > 1:
                        log("Rommet er opptatt, prøver neste rom")
                        ROM = ROM[1:]
                        tries = 0 # Resett antall forsøk før vi begynner på neste rom

                    else:
                        log("Ingen av de spesifiserte rommene er ledig til dette tidspunktet")
                        return

                elif "overskredet" in errormessage:
                    sys.exit(1)

                else:
                    log("En ukjent feil oppsto")
                    tries += 1
                    if tries<maxtries:
                        log("Prøver igjen")
                    else:
                        log("Maks antall forsøk er oppbrukt. Avslutter.")
                        return

        # Hvis bruker avbryter programmet, avslutt med kode 130
        except KeyboardInterrupt:
            log("Mottok KeyboardInterrupt. Avslutter.")
            sys.exit(130)

        # Hvis vi fanger en sys.exit() må vi kalle den på nytt.
        except SystemExit:
            sys.exit(1)

        # Hvis noe skjer før vi kommer til bestilling kan det noen ganger hjelpe å prøve igjen
        except:
            logging.exception("En feil oppsto under reservering!")
            tries += 1
            if tries<maxtries:
                log("Prøver igjen...")
            else:
                log("Maks antall forsøk er oppbrukt. Avslutter.")
                return

        # Lukker nettleseren før vi prøver igjen
        driver.close()



# Åpne alle konfigurasjonsfiler fra ./config/ og kjør reservasjoner for de
script_dir = dirname(realpath(__file__))
config_dir = script_dir + "/config"

config_files = [f for f in listdir(config_dir) if isfile(join(config_dir, f))]

for config_file in config_files:
    if config_file[-3:] == ".py":
        conf = config_dir+"/"+config_file

        # Validerer config
        ret = system(script_dir + "/" + "validate_config.py " + conf)
        if ret == 0:
            # Kjører config
            exec(open(conf, "r").read())
            log(f"Kjører reservasjon fra {config_file}")
            log(f"BRUKERNAVN: {BRUKERNAVN}")
            log(f"ROM: {ROM}")
            log(f"UKEDAG: {UKEDAG}")
            log(f"STARTTID: {STARTTID}")
            log(f"SLUTTID: {SLUTTID}")
            log(f"EPOST: {EPOST}")
            run()
        else:
            log(f"Hopper over invalid config {config_file}")
