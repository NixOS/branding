// Date must be set to none for deterministic builds
#set document(date: none)
#set page(margin: 0pt, width: 2048pt, height: 2048pt)

#let data = json("final.json")

#let palette-colour(intOrStr) = if type(intOrStr) == int {
  if intOrStr == 0 { luma(0) } else if intOrStr == 1 {
    luma(255)
  } else if intOrStr == 2 { rgb("#5b7ec8") } else if intOrStr == 3 {
    rgb("#87adfa")
  } else if intOrStr == 4 { rgb("#5fb8f2") } else if intOrStr == 5 {
    rgb("#aaa1f6")
  } else if intOrStr == 6 { rgb("#e99861") } else if intOrStr == 7 {
    rgb("#f08d94")
  } else if intOrStr == 8 { rgb("#d991d2") } else if intOrStr == 9 {
    rgb("#6fc488")
  } else { panic("Invalid Colour ID: " + intOrStr) }
} else { rgb(intOrStr) }

// https://typst.app/universe/package/one-liner
#let fit-to-width(max-text-size: 800pt, min-text-size: 256pt, it) = context {
  let contentsize = measure(it)
  layout(size => {
    if contentsize.width > 0pt {
      // Prevent failure on empty content
      let ratio-x = size.width / contentsize.width
      let ratio-y = size.height / contentsize.height
      let ratio = if ratio-x < ratio-y {
        ratio-x
      } else {
        ratio-y
      }

      let newx = contentsize.width * ratio
      let newy = contentsize.height * ratio
      let suggestedtextsize = 1em * ratio
      if (suggestedtextsize + 0pt).to-absolute() > max-text-size {
        suggestedtextsize = max-text-size
      }
      if (suggestedtextsize + 0pt).to-absolute() < min-text-size {
        suggestedtextsize = min-text-size
      }
      set text(size: suggestedtextsize)
      it
    }
  })
}

#let icon(
  type: none,
  colours: none,
  contents: none,
) = {
  set page(
    fill: palette-colour(if type == "standard" { colours.background } else {
      colours.border
    }),
    background: {
      if type == "standard" {
        grid(
          columns: 1,
          rows: (992pt, 64pt, 992pt),
          gutter: 0pt,
          rect(
            width: 100%,
            height: 100%,
            stroke: none,
            inset: if contents.style == "text" { 128pt } else { 0pt },
            if contents.style == "text" {
              align(center + bottom, fit-to-width(text(
                font: "Route 159",
                weight: "bold",
                fill: palette-colour(colours.text),
                contents.text,
              )))
            } else if contents.style == "image" {
              align(center + bottom, image(
                { "icons/" + contents.image + ".svg" },
                height: 992pt,
                fit: "contain",
              ))
            } else { panic("Invalid style: " + content.style) },
          ),

          rect(width: 100%, height: 100%, fill: palette-colour(colours.border)),

          rect(
            width: 100%,
            height: 100%,
            fill: palette-colour(2),
            inset: 0pt,
            image(
              "icons/nixos-logomark-white-flat-minimal.svg",
              fit: "contain",
            ),
          ),
        )
      } else {
        circle(
          radius: 768pt,
          fill: palette-colour(colours.background),
          inset: -224pt,
          image({ "icons/" + contents.image + ".svg" }, fit: "contain"),
        )
      }
    },
  )
  pagebreak(weak: true)
  // FIXME: For some reason, the icons aren't generated correctly if there isn't *something* in the first page.
  text(fill: rgb("#00000000"), [.])
}

#if sys.inputs.singleIcon == "null" {
  for room in data.values() {
    icon(type: room.type, colours: room.colours, contents: room.contents)
  }
} else {
  icon(
    type: data.at(sys.inputs.singleIcon).type,
    colours: data.at(sys.inputs.singleIcon).colours,
    contents: data.at(sys.inputs.singleIcon).contents,
  )
}
