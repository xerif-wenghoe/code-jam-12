from js import document


async def start() -> None:
    document.title = "Code Jam 12"
    document.body.innerHTML = """

<div class="main">

  <div class="section">
    <h1 class="title">Super Ultra Encryptor</h1>
  </div>

  <div class="section">
    <label for="fileInput" class="dropzone">Drag & Drop files here or click to select</label>
    <input type="file" id="fileInput" style="display:none" />
  </div>

  <div class="section">
    <div class="selections">
      <img src="assets/images/p1.jpg" class="image-placeholder">
      <img src="assets/images/p1.jpg" class="image-placeholder">
      <img src="assets/images/p1.jpg" class="image-placeholder">
      <img src="assets/images/p1.jpg" class="image-placeholder">
      <img src="assets/images/p1.jpg" class="image-placeholder">
    </div>
  </div>

  <div class="section">
  </div>

</div>

"""
