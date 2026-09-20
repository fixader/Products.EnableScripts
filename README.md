# Products.EnableScripts

[English / PyPI description](README.en.md)

> **RestrictedPython er begrenset av en grunn.** Dette produktet åpner bevisst
> deler av Zopes sikkerhetsgrenser. Bruk det bare når du stoler på alle som kan
> opprette eller redigere Python Scripts. Tilgangen gjelder hele serverprosessen.
> Bibliotekskall kan få tilgang til filer, nettverk og serverressurser selv om
> scriptet kjører som restricted kode. Avkryssingene er ikke en sandkasse og
> garanterer ikke isolasjon. Les [SECURITY.md](SECURITY.md) før aktivering.

Et Zope 5/6-produkt for å velge hvilke installerte biblioteker som kan brukes
fra **Script (Python)**. Innstillinger finnes under
**Control Panel → EnableScripts** (`/Control_Panel/EnableScripts/manage_main`).

Hvert bibliotek har en hovedavkryssing. Fold ut biblioteket for å styre
enkeltimporter, objekter, metoder og attributter. Bibliotekene er av ved første
installasjon; alle underpunkter er på som standard. Underpunktene beholdes når
hovedvalget slås av. Avhengigheter aktiveres automatisk ved lagring.

## Installasjon

Installer i **samme Python-miljø som Zope**:

```sh
python -m pip install /path/to/products_enablescripts-0.1.0-py3-none-any.whl
```

Pillow og ReportLab er valgfrie. De blir ikke installert eller oppgradert av
grunnpakken. Installer dem separat, eller bruk ekstraavhengighetene `pillow`,
`reportlab` eller `all` ved kildeinstallasjon:

```sh
python -m pip install '/path/to/Products.EnableScripts[all]'
```

Start Zope på nytt, åpne kontrollpanelet som **Manager på roten**, velg
biblioteker, lagre og start **alle Zope-prosesser** på nytt. Panelet viser hva
som er aktivt i prosessen som behandler forespørselen, og om den har ventende
endringer. Manglende biblioteker vises uten aktivert hovedavkryssing.

### Buildout

Kildekoden skal ligge utenfor genererte `parts/`- og instance-mapper:

```ini
[buildout]
develop =
    src/Products.EnableScripts

[instance]
eggs =
    Zope
    Products.PythonScripts
    Products.EnableScripts
    Pillow
    reportlab
```

Flett dette inn i den eksisterende konfigurasjonen; behold øvrige eggs og
innstillinger. En egg-distribusjon kan også hentes fra deres vanlige pakkelager.
Buildout må beholde ZODB-lagringen. Produktkoden gjeninstalleres fra deklarert
kilde; avkryssingene ligger i ZODB, ikke i genererte instance-filer.

## Integrasjoner

* `io.BytesIO`: binære strømmer i minnet. `io.open` og `FileIO` åpnes ikke av dette valget.
* Pillow: `Image`, `ImageDraw`, `ImageFont`, `ImageOps`, `ImageEnhance`, enum-verdier og tilhørende objekter.
* ReportLab Canvas: Canvas, tekst-/stiobjekter, ImageReader, farger, sideformater og skrifter.
* ReportLab Platypus: dokumenter, avsnitt, tabeller, flowables og stiler.
* PDF-/bildehjelpere: `PdfBuffer`, `ImageBuffer`, `send_pdf_response` fra vedlagte GlobalModule.
* Zope-bilder: `save_image_object`, med kontroll av brukerens rettigheter.
* Utvidet `io`: øvrige offentlige io-importer fra gamle GlobalModule, inkludert filsystemtilgang.
* XML / ElementTree: XML-parser og elementobjekter.
* HTTP / urllib: URL-håndtering, forespørsler og responsobjekter.
* ReportLab-strekkoder: Barcode, Code128 og ECC200 DataMatrix.
* Hubarcode: modulene fra labserverens GlobalModules, dersom pakken er installert.

ReportLab-listene utvides med offentlige eksporterte navn og Canvas-/ImageReader-
metoder fra installert versjon for å bevare den gamle funksjonaliteten.
Underpunkter som kommer til ved en biblioteksoppgradering er på som standard.
Interne navn med `_` inngår ikke. Dette endrer ikke RestrictedPythons språkregler.

### Direkte bruk

```python
from io import BytesIO
from PIL import Image, ImageDraw
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader

image = Image.new('RGB', (400, 150), 'white')
ImageDraw.Draw(image).text((20, 20), 'Hei fra Zope', fill='black')
buffer = BytesIO()
canvas = Canvas(buffer)
canvas.drawImage(ImageReader(image), 30, 550, width=400, height=150)
canvas.save()
context.REQUEST.RESPONSE.setHeader('Content-Type', 'application/pdf')
return buffer.getvalue()
```

Hjelpere importeres med `from Products.EnableScripts import ImageBuffer` osv.
Gamle importer fra `Products.GlobalModule` må oppdateres. Rapportbibliotekene
importeres fortsatt fra `reportlab` og `PIL`.

## Overgang fra GlobalModule / GlobalModules

Ta vare på originalproduktet og en ZODB-backup. Deaktiver gamle aktiveringsprodukter
før EnableScripts tas i bruk; andre produkter kan ellers fortsatt gi tilgang som
EnableScripts viser som avslått. Aktiver de tilsvarende bibliotekene i panelet.
Ingen eksisterende scripts endres automatisk av produktet.

Sikkerhetsdeklarasjonene er **globale i hver Python-prosess**, ikke per mappe,
bruker eller nettsted. Avkryssinger styrer tilgang fra restricted kode, ikke hva
betrodd Python-kode inne i bibliotekene kan gjøre. For eksempel kan Pillow,
ReportLab og urllib behandle filstier eller URL-er når deres API tillater det.

Lagring endrer bare ZODB-innstillinger. Ingen global tilgang endres inne i en
HTTP-transaksjon. Ved oppstart lastes en fast policy i hver prosess. Manglende
valgfrie biblioteker logges og hoppes over, og vises med årsak i panelet.

## Flere integrasjoner

En installert egg kan tilby entry point-gruppen `enablescripts.integrations`:

```toml
[project.entry-points."enablescripts.integrations"]
my_library = "my_package.integration:features"
```

`features()` returnerer en liste av `Products.EnableScripts.registry.Feature`:

```python
from Products.EnableScripts.registry import Feature

def features():
    return [Feature(
        key='my_library',
        title='My Library',
        description='Selected supported operations.',
        modules={'my_library': ('Document',)},
        classes={'my_library:Document': ('render', 'save')},
        distributions=('my-library',),
        requires=('bytesio',),
    )]
```

Bruk `types` i stedet for `classes` for uforanderlige C-typer som BytesIO.
Valg må ha unike feature-nøkler og ikke overlappe andre integrasjoners deklarasjoner.
En ukjent installert pakke blir aldri åpnet automatisk. Omstart kreves også etter
installasjon av en ny integrasjon.

## Tester og pakking

```sh
python -m pip install -e '.[all,test]'
python -m pytest -q
python -m build
```

Restricted-script-tester kjøres i separate prosesser for å unngå at globale
sikkerhetsdeklarasjoner fra én test påvirker den neste.
