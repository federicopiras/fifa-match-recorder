from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import pandas as pd

# Configura Chrome headless
options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)

fifa_versions = {
    # "FIFA 25": "https://sofifa.com/teams?type=club&r=250035&set=true",
    # "FIFA 24": "https://sofifa.com/teams?type=club&r=240050&set=true",
    # "FIFA 23": "https://sofifa.com/teams?type=club&r=230054&set=true",
    # "FIFA 22": "https://sofifa.com/teams?type=club&r=220069&set=true",
    # "FIFA 21": "https://sofifa.com/teams?type=club&r=210064&set=true",
    "FIFA 20": "https://sofifa.com/teams?type=club&r=200061&set=true"
}

for fifa_version, base_url in fifa_versions.items():
    teams = []
    championships = []
    nationalities = []

    offset = 0
    first_page = True

    while True:
        url = f"{base_url}&offset={offset}"
        driver.get(url)

        # Attendi il caricamento della tabella
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
        )

        # Rimuovi il popup dei cookie solo una volta
        if first_page:
            try:
                cookie_modal = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "onetrust-banner-sdk"))
                )
                driver.execute_script("arguments[0].remove();", cookie_modal)
                print("Popup cookie rimosso.")
            except TimeoutException:
                print("Nessun popup dei cookie trovato.")
            first_page = False

        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        if not rows:
            break  # Nessuna riga trovata, fine della paginazione

        for row in rows:
            try:
                team_name = row.find_element(By.CSS_SELECTOR, "td:nth-child(2) a").text.strip()
                championship = row.find_element(By.CSS_SELECTOR, "td:nth-child(2) .sub").text.strip()
                flag_element = row.find_element(By.CLASS_NAME, "flag")
                nationality = flag_element.get_attribute("title")

                teams.append(team_name)
                championships.append(championship)
                nationalities.append(nationality)
            except Exception as e:
                print(f"Errore in una riga: {e}")
                continue

        offset += 60  # Prossima pagina
        time.sleep(1.5)  # Attesa tra le pagine

    # Salva i dati
    df = pd.DataFrame({
        "Team": teams,
        "Championship": championships,
        "Nationality": nationalities
    })

    filename = f"{fifa_version.replace(' ', '_').lower()}_teams.csv"
    df.to_csv(filename, index=False)
    print(f"Salvato: {filename} ({len(df)} squadre)")

driver.quit()