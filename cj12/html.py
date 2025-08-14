from textwrap import dedent

FILE_AREA = dedent("""
    <section id="file-display">
    <div class="inner-flex">
        <p>{file_name}</p>
        <p>{file_size} KB</p>
    </div>
    <div class="inner-flex">
        <label for="key-input">Encryption/Decryption Key:</label>
        <input type="password" id="key-input" placeholder="Enter your key here" />
    </div>
    <div class="inner-flex">
        <button id="encrypt-button" class="right button" disabled>Encrypt</button>
        <button id="decrypt-button" class="right button" disabled>Decrypt</button>
    </div>
    </section>
""")


DOWNLOAD_SECTION = dedent("""
    <div class="inner-flex">
        <p>File {operation} successfully!</p>
        <p>Size: {file_size} bytes</p>
        <button id="download-button" class="button">Download {title} File</button>
    </div>
""")
