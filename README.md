# Super Duper Encryption Tool

## What's this?

It's a file encryption and decryption tool.

## Where do I put in the password?

Um... password?

Oh, buddy.

Passwords are low-entropy relics of the 90s, reused across sites, and breached before you’ve even finished typing them. You deserve better.

Our _superior_ tool trades in secure keys, not passwords. The kind of keys that don’t fit on a sticky note, can’t be phished, and would make a password manager weep with joy.

In the big '25, if you’re still saying “just use a strong password,” you’re already compromised, which is why we provide _actually_ secure alternatives.

## Methods

### <img src="static/methods/chess/img.png" /> Chess

1. Arrange the chess board in any way you want.
2. Upload a file (or do it before this) to be encrypted/decrypted with the board.

---

### <img src="static/methods/location/img.png" /> Location

1. Zoom in very far and click anywhere on the map.
2. Upload a file (or do it before this) to be encrypted/decrypted with the location.

---

### <img src="static/methods/safe/img.png" /> Safe

1. Spin the dial to make a unique sequence.
2. Upload a file (or do it before this) to be encrypted/decrypted with the sequence.

---

### <img src="static/methods/pattern_lock/img.png" /> Pattern

1. Connect dots in any patterns to form a unique connection sequence
2. To change the pattern, simply redo step 1 to make a new pattern. The old pattern will disappear automatically.
3. Upload a file (or do it before this) to be encrypted/decrypted with the pattern.

A 3x3 grid is the default, but you may choose to use a 4x4 or 6x6 grid.

As the key is simply the sequence in of the connected dots based on their position, a 3x3 encrypted file can be decrypted from a 4x4 pattern.

---

### <img src="static/methods/music/img.png" /> Music

1. Place down notes on the grid.
2. Upload a file (or do it before this) to be encrypted/decrypted with the song.

---

### <img src="static/methods/direction/img.png" width="16" /> Direction

1. Drag to make a unique sequence of directions.
2. Upload a file (or do it before this) to be encrypted/decrypted with the sequence.

---

### <img src="static/methods/colour_picker/img.png" /> Colour Picker

1. Click and drag on scale of each red, green and blue to generate the desired colour as your encryption key. The colour and its hex representation will be shown at the bottom of the scale.
2. Upload a file (or do it before this) to be encrypted/decrypted with the pattern.

Simply telling the other person about the colour of key will give them a hard time getting the exact code for decryption.

## Running locally

1. [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
2. Clone our repository: `git clone https://github.com/xerif-wenghoe/code-jam-12`
3. Change into the directory: `cd code-jam-12`
4. Sync dependencies: `uv sync`
5. Run the server: `uv run server.py`
6. Access the tool at http://localhost:8000

## Technical details

- We use [Pyodide](https://pyodide.org/) for logic and DOM manipulation.
- All methods eventually generate a 256-bit key for AES.
- [We implemented AES ourselves](cj12/aes.py).
- Encrypted data is contained inside our [custom container format](cj12/container.py) which stores:
  - Magic bytes (`SDET`)
  - Method used
  - Original filename
  - Hash of decrypted data
  - Encrypted data

## License

This project is licensed under the [MIT license](LICENSE).
