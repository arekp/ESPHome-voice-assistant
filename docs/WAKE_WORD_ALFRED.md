# Własne słowo budzące: „Alfred" / „Alfredzie"

Oficjalnych modeli microWakeWord o takim słowie nie ma, więc trzeba wytrenować własny
(`alfred.tflite` + `alfred.json`). Jeden model rozpoznaje oba warianty.

## 1. Trening w Google Colab (GPU T4)

Notebook: [kahrendt/microWakeWord `basic_training_notebook.ipynb`](https://github.com/kahrendt/microWakeWord/blob/main/notebooks/basic_training_notebook.ipynb).
Wersja z GitHuba jest dziś nieaktualna względem Colaba (Python 3.13, nowe biblioteki),
dlatego potrzebne są poprawki. Colab pyta o dostęp do sekretu `HF_TOKEN` – odmawiaj, anonimowe
pobieranie wystarcza.

**Frazy.** Generator próbek (Piper, model `en_US-libritts_r`) jest angielski, więc działa
zapis fonetyczny, bez polskich głosów: `alfred` i `alfredzhe` (dla „Alfredzie").
Próbki obu fraz trafiają do jednego katalogu `generated_samples`, a model uczy się ich razem.

**Poprawki względem notebooka:**

1. Generator próbek: `piper-phonemize-cross==1.2.1` nie ma pakietu pod Pythona 3.13.
   Uruchom generator w venv 3.10 (`uv venv --python 3.10`), na tagu `v2.0.0` repozytorium
   `rhasspy/piper-sample-generator` (nowsze commity zmieniły API), z
   `TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1` (nowy PyTorch inaczej odrzuca stary plik `.pt`)
   i doinstalowanym `webrtcvad-wheels`.
2. `pip install "datasets<4.0"` + restart sesji – nowsze `datasets` zwraca dekodery torchcodec,
   których notebook nie obsługuje.
3. AudioSet: plik `bal_train09.tar` już nie istnieje. Użyj
   `data/bal_train/09.parquet` z `agkphysics/AudioSet` (kolumna `audio`, bajty FLAC; wystarczy
   ok. 500 klipów, przeskalowanych do 16 kHz).
4. Katalog `mit_rirs` po nieudanym pierwszym przebiegu zostaje pusty – usuń go przed ponownym
   pobraniem.
5. Trening kończy się OOM-killem (12 GB RAM) przy walidacji ambient. Przytnij zbiór
   `negative_datasets/dinner_party_eval` do ok. 35% długości każdego nagrania
   (`RaggedMmap.from_generator`), oryginał zostaw jako `dinner_party_eval_full`.

Po treningu pobierz `trained_models/wakeword/tflite_stream_state_internal_quant/stream_state_internal_quant.tflite`.
Notebook jest „punktem startowym" – model może wymagać strojenia (patrz niżej).

## 2. Manifest `alfred.json`

Model potrzebuje pliku JSON (wzór: `okay_nabu.json` w `esphome/micro-wake-word-models`):

```json
{
  "type": "micro",
  "wake_word": "Alfred",
  "author": "arekp",
  "website": "https://github.com/arekp",
  "model": "alfred.tflite",
  "trained_languages": ["pl"],
  "version": 2,
  "micro": {
    "probability_cutoff": 0.97,
    "sliding_window_size": 5,
    "feature_step_size": 10,
    "tensor_arena_size": 26080,
    "minimum_esphome_version": "2024.7.0"
  }
}
```

`probability_cutoff` i `sliding_window_size` dostrajasz po testach. Jeśli model nie ładuje się,
zwiększ `tensor_arena_size`.

## 3. Zmiana w konfiguracji

Pliki `alfred.json` i `alfred.tflite` wrzuć obok `esp_ver2.yaml` (w HA: `/config/esphome/`).
W [esp_ver2.yaml](../esp_ver2.yaml) podmień model:

```yaml
micro_wake_word:
  id: wake_word_engine
  microphone: board_microphone
  models:
    - model: alfred.json
      id: alfred_local
      internal: true
```

oraz w `on_client_connected` zamień `micro_wake_word.enable_model: okay_nabu_local`
na `micro_wake_word.enable_model: alfred_local`.

## 4. Test i strojenie

Po wgraniu sprawdź logi (`[W]`/`[E]`) i wypowiedz oba warianty z różnej odległości oraz z hałasem
w tle. Notuj fałszywe wybudzenia i nietrafienia:

- za dużo fałszywych wybudzeń → podnieś `probability_cutoff` (np. 0.98–0.99),
- słowo nie reaguje → obniż `probability_cutoff` (np. 0.9) lub wygeneruj więcej próbek
  (inne warianty fonetyczne, np. `alfred` / `alfret` / `alfredzie`) i wytrenuj ponownie.
