# Parts library

Bought parts considered for the S3 Rally Sim pod, one TOML card per orderable part, grouped by category.
Every value cites the vendor document (and PDF page) it came from. The selector in
[`tools/partsel/`](../tools/partsel/) checks these cards against the requirements in
[`requirements/`](../requirements/); the chosen parts are listed in
[`requirements/selection.toml`](../requirements/selection.toml) and flow into the CAD as `cad/pod/bought.py`.

| Category | Cards |
|---|---|
| [`seats/`](seats/) | Recaro Pro Racer SPG XL, Recaro Pole Position N.G., Sparco Circuit II QRT, Sparco Master Advanced 8855-2021 |
| [`dd-wheelbases/`](dd-wheelbases/) | Simucube 2 Pro, Simucube 2 Sport, MOZA R21 Ultra, Simagic Alpha U |
| [`pedal-sets/`](pedal-sets/) | Heusinkveld Ultimate+ and Sprint (3-pedal), Simagic P2000, Fanatec ClubSport V3 |
| [`servo-motors/`](servo-motors/) | Kollmorgen AKM2G-51K and -52L, Beckhoff AM8052, Yaskawa SGM7A-20, Delta ECM-B3M, Siemens 1FL6054 |
| [`gearboxes/`](gearboxes/) | Apex ABR142 50:1, Wittenstein SPK+ 140 and 180 50:1, Neugart WPLN142 50:1 and WPLHE120 40:1 |
| [`rod-ends/`](rod-ends/) | SKF SIKB 20 F, SIKB 16 F, SIKAC 20 M, SI 20 C; igus KBRM-20 |
| [`profile-rails/`](profile-rails/) | HIWIN HGW25CC (E2) and HGH25CA, THK HSR25C, Rexroth R1651 size 25, NSK NH25AN |
| [`ballscrews/`](ballscrews/) | HIWIN 25-10, Rexroth FEM-E-S 25x10, THK BNK2520 and BLK2020 |

Rules for a card: copy numbers exactly as printed (unit conversion only, said in the notes); every value cites a
source; leave a value out rather than guess (the selector reports it as CHECK); where a maker prints a rule
instead of a number (e.g. "T2NOT = 3 x T2N"), record the rule and let the selector derive the number.
