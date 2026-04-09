const fileGrid = document.querySelector("#file-grid")
const notesList = document.querySelector("#notes-list")
const commandsList = document.querySelector("#commands-list")
const heroStats = document.querySelector("#hero-stats")
const cardTemplate = document.querySelector("#file-card-template")
const liveRegion = document.querySelector("#live-region")

const state = {
  release: null,
}

const appendSoftWrappedText = (element, value) => {
  const parts = value
    .split(/(?<=[a-z])(?=[A-Z])|(?<=\.)/g)
    .filter(Boolean)

  element.replaceChildren()
  parts.forEach((part, index) => {
    element.append(document.createTextNode(part))
    if (index < parts.length - 1) {
      element.append(document.createElement("wbr"))
    }
  })
}

const messageNode = (text) => {
  const paragraph = document.createElement("p")
  paragraph.className = "sample-empty"
  paragraph.setAttribute("role", "status")
  paragraph.textContent = text
  return paragraph
}

const announce = (message) => {
  if (!liveRegion) {
    return
  }

  liveRegion.textContent = ""
  window.requestAnimationFrame(() => {
    liveRegion.textContent = message
  })
}

const metric = (label, value) => {
  const card = document.createElement("div")
  card.className = "hero-stat"
  const labelNode = document.createElement("p")
  labelNode.className = "hero-stat-label"
  labelNode.textContent = label
  const valueNode = document.createElement("p")
  valueNode.className = "hero-stat-value"
  valueNode.textContent = value
  card.append(labelNode, valueNode)
  return card
}

const renderHero = (release) => {
  const { totals, compression, release_date: releaseDate } = release
  heroStats.replaceChildren(
    metric("Release date", releaseDate || "Unknown"),
    metric("Compressed", totals.compressed_size || "Unknown"),
    metric("Original", totals.original_size || "Unknown"),
    metric(
      "Compression",
      compression.algorithm
        ? `${compression.algorithm} level ${compression.level}`
        : "Unknown",
    ),
  )
}

const renderNotes = (notes) => {
  notesList.replaceChildren(
    ...notes.map((note) => {
      const item = document.createElement("li")
      item.textContent = note
      return item
    }),
  )
}

const renderCommands = (commands) => {
  commandsList.replaceChildren(
    ...commands.map((command) => {
      const pre = document.createElement("pre")
      pre.textContent = command
      return pre
    }),
  )
}

const renderSamples = async (file, container, button) => {
  if (file.resource_name === "Manifest") {
    container.replaceChildren(
      messageNode("The manifest is plain JSON. Use the download link to open or save it directly."),
    )
    announce("Manifest download guidance displayed.")
    return
  }

  button.disabled = true
  button.textContent = "Loading..."
  button.setAttribute("aria-expanded", "true")
  samplesBusy(container, true)
  announce(`Loading sample records for ${file.resource_name}.`)

  try {
    const response = await fetch(file.sample_path)
    if (!response.ok) {
      throw new Error(`Failed to load samples for ${file.resource_name}`)
    }
    const payload = await response.json()
    if (!payload.records.length) {
      container.replaceChildren(messageNode("No sample records were returned."))
      announce(`No sample records were returned for ${file.resource_name}.`)
      return
    }

    container.replaceChildren(
      ...payload.records.map((record) => {
        const pre = document.createElement("pre")
        pre.textContent = JSON.stringify(record, null, 2)
        return pre
      }),
    )
    announce(`Loaded ${payload.records.length} sample records for ${file.resource_name}.`)
  } catch (error) {
    container.replaceChildren(messageNode(error.message))
    announce(error.message)
  } finally {
    button.disabled = false
    button.textContent = "Reload samples"
    samplesBusy(container, false)
  }
}

const samplesBusy = (container, isBusy) => {
  container.setAttribute("aria-busy", String(isBusy))
}

const renderFiles = (files) => {
  fileGrid.setAttribute("aria-busy", "true")
  fileGrid.replaceChildren(
    ...files.map((file) => {
      const fragment = cardTemplate.content.cloneNode(true)
      const card = fragment.querySelector(".file-card")
      const label = fragment.querySelector(".file-label")
      const name = fragment.querySelector(".file-name")
      const downloadLink = fragment.querySelector(".download-link")
      const compressedSize = fragment.querySelector(".compressed-size")
      const originalSize = fragment.querySelector(".original-size")
      const ratio = fragment.querySelector(".ratio")
      const button = fragment.querySelector(".sample-button")
      const samples = fragment.querySelector(".samples")

      const sampleRegionId = `samples-${file.resource_name.toLowerCase()}`
      const headingId = `file-heading-${file.resource_name.toLowerCase()}`
      appendSoftWrappedText(label, file.resource_name)
      appendSoftWrappedText(name, file.filename)
      name.id = headingId
      card.setAttribute("aria-labelledby", headingId)
      downloadLink.href = file.download_path
      downloadLink.setAttribute("aria-label", `Download ${file.filename}`)
      compressedSize.textContent = file.compressed_size || "Unknown"
      originalSize.textContent = file.original_size || "Unknown"
      ratio.textContent =
        typeof file.compression_ratio_pct === "number"
          ? `${file.compression_ratio_pct}%`
          : "n/a"
      button.setAttribute("aria-controls", sampleRegionId)
      button.setAttribute("aria-expanded", "false")
      button.setAttribute("aria-label", `Load sample records for ${file.resource_name}`)
      samples.id = sampleRegionId
      samples.setAttribute("role", "region")
      samples.setAttribute("aria-label", `${file.resource_name} sample records`)
      samplesBusy(samples, false)

      button.addEventListener("click", () => renderSamples(file, samples, button))
      card.dataset.resource = file.resource_name

      return fragment
    }),
  )
  fileGrid.setAttribute("aria-busy", "false")
}

const load = async () => {
  fileGrid.setAttribute("aria-busy", "true")
  const response = await fetch("/api/release.json")
  if (!response.ok) {
    throw new Error("Unable to load release metadata.")
  }
  const release = await response.json()
  state.release = release
  renderHero(release)
  renderFiles(release.files)
  renderNotes(release.notes)
  renderCommands(release.commands)
  announce("Release metadata loaded.")
}

load().catch((error) => {
  fileGrid.replaceChildren(messageNode(error.message))
  fileGrid.setAttribute("aria-busy", "false")
  announce(error.message)
})
