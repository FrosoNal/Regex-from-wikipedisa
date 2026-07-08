"""Κύριο πρόγραμμα: λαμβάνει URL πόλης από Wikipedia και εμφανίζει τα στοιχεία της."""
from fetchers import fetch_html
from extractors import (
    extract_title,
    extract_population,
    extract_area,
    extract_country,
    extract_coordinates,
    extract_altitude,
    extract_timezone,
    extract_temperature,
)


def main():
    url = input("Εισάγετε URL πόλης: ").strip()

    print("\nΛήψη σελίδας…")
    try:
        html = fetch_html(url)
    except Exception as e:
        print(f"Σφάλμα κατά τη λήψη: {e}")
        return

    print("  ΠΛΗΡΟΦΟΡΙΕΣ ΠΟΛΗΣ")

    # 1. Όνομα
    title = extract_title(html)
    print(f"{'Όνομα πόλης':<20}: {title or 'Δεν βρέθηκε'}")

    # 2. Πληθυσμός
    pop = extract_population(html)
    print(f"{'Πληθυσμός':<20}: {pop or 'Δεν βρέθηκε'}")

    # 3. Έκταση
    area = extract_area(html)
    print(f"{'Έκταση':<20}: {(area + ' km²') if area else 'Δεν βρέθηκε'}")

    # 4. Χώρα
    country = extract_country(html)
    print(f"{'Χώρα/Περιφέρεια':<20}: {country or 'Δεν βρέθηκε'}")

    # 5. Συντεταγμένες
    coords = extract_coordinates(html)
    print(f"{'Συντεταγμένες':<20}: {coords or 'Δεν βρέθηκαν'}")

    # 6. Υψόμετρο
    alt = extract_altitude(html)
    print(f"{'Υψόμετρο':<20}: {(alt + ' μ.') if alt else 'Δεν βρέθηκε'}")

    # 7. Ζώνη ώρας
    tz = extract_timezone(html)
    print(f"{'Ζώνη ώρας':<20}: {tz or 'Δεν βρέθηκε'}")

    # 8. Θερμοκρασία — από τμήμα Κλίμα
    temps = extract_temperature(html)
    if temps:
        labels = {
            "highest_max": "Υψηλότερη Μέγιστη",
            "mean":        "Μέση Μηνιαία     ",
            "lowest_min":  "Χαμηλότερη Ελάχ. ",
        }
        for key, label in labels.items():
            if key in temps:
                print(f"  {label}: {temps[key]} °C")
    else:
        print("  Δεν βρέθηκαν δεδομένα θερμοκρασίας.")

    print("=" * 50)


if __name__ == "__main__":
    main()
